"""
Metro map LED display app for Raspberry Pi.

This app controls LED strips to display real-time Metro train positions.
Requires a WMATA API key set in the WMATA_API_KEY environment variable.

Setup on the Pi:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export WMATA_API_KEY='your-api-key-here'
    python app.py
"""

import os
import sys
import json
import time
import threading
import logging
from pathlib import Path
from logging.handlers import MemoryHandler

from flask import Flask, jsonify, request, render_template

from led_controller import LEDController
from wmata_client import WMATAClient
from config import STATION_TO_LED, LINE_COLORS, LED_COUNT

# --------------------------------------------------------------------------------------
# Logging: stream to stdout so systemd/journald captures logs; optional RAM buffer flush
# --------------------------------------------------------------------------------------
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Clear any pre-configured handlers (e.g., gunicorn/flask defaults)
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)

stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(stream)

# Optional: small in-RAM buffer that flushes at WARNING+
root_logger.addHandler(MemoryHandler(capacity=1024 * 5, flushLevel=logging.WARNING, target=stream))

logger = root_logger

# --------------------------------------------------------------------------------------
# Paths / data loading (robust to different CWD under systemd)
# --------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
STATION_NAMES_PATH = BASE_DIR / "station_names.json"

try:
    with STATION_NAMES_PATH.open("r", encoding="utf-8") as f:
        STATION_NAMES = json.load(f)
    logger.info("Loaded station names from %s", STATION_NAMES_PATH)
except Exception as e:
    logger.error("Failed to load station names: %s", e)
    STATION_NAMES = {}

# --------------------------------------------------------------------------------------
# Flask app
# --------------------------------------------------------------------------------------
app = Flask(__name__)

# Dictionary to store current LED states shown in the web UI
# Per-LED state format: { "color": [r, g, b], "brightness": float, optional flags... }
current_led_states = {}

# Globals controlling the updater
wmata_client = None
update_thread = None
should_update = False

# --------------------------------------------------------------------------------------
# LED controller: default to simulation unless explicitly disabled
# Set METRO_FORCE_SIM=0 to try real hardware; any failure falls back to simulation.
# --------------------------------------------------------------------------------------
force_sim_env = os.environ.get("METRO_FORCE_SIM", "1").strip()
force_simulation = force_sim_env not in ("0", "false", "False")
led_controller = LEDController(led_count=LED_COUNT, force_simulation=force_simulation)
logger.info("LED Mode: %s", "Simulated" if getattr(led_controller, "simulated", False) else "Real")

# --------------------------------------------------------------------------------------
# WMATA client (reads WMATA_API_KEY from .env/env internally; no constructor args)
# --------------------------------------------------------------------------------------
try:
    wmata_client = WMATAClient()
    logger.info("WMATA client initialized")
except Exception as e:
    logger.error("WMATA client init failed: %s", e)
    wmata_client = None

# --------------------------------------------------------------------------------------
# Error handler
# --------------------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unexpected error: %s", e)
    return jsonify({
        "status": "error",
        "message": str(e),
        "led_mode": "simulated" if getattr(led_controller, "simulated", False) else "real"
    }), 500

# --------------------------------------------------------------------------------------
# Background updater thread
# --------------------------------------------------------------------------------------
def update_leds():
    """
    Background loop:
      • Fetch ALL station predictions every CACHE_TTL seconds (BRD only).
      • Single train at station: solid line color.
      • Multiple trains: blink between their colors (no blending/comets).
      • After BRD ends at a station: long fade tail.
      • While BRD: pre-glow ONE neighbor (not the one just left / fading).
      • Render LEDs/UI every 1s from cached data; resilient to WMATA hiccups.
    """
    import time
    from time import monotonic, sleep
    global should_update, current_led_states, wmata_client

    # ---- tuning knobs ----
    CACHE_TTL      = 10.0   # seconds between WMATA fetches
    FADE_STEPS     = 24     # seconds of fade after BRD ends (long tail)
    PREGLOW_RISE   = 12.0   # seconds to ramp neighbor up
    MAX_PREGLOW    = 0.6    # neighbor max brightness (0..1)
    WARN_AFTER     = 300.0  # warn if no successful fetch for 5 min
    WARN_INTERVAL  = 30.0   # warn at most every 30s

    # ---- state ----
    next_fetch_time     = 0.0
    last_success_mono   = 0.0
    next_warn_time      = 0.0
    error_count         = 0
    cached_station_trains = {}       # {station_code: [ {line_code: "RD"}, ... ]}
    fading_leds           = {}       # {station_code: {"color": (r,g,b), "steps": int}}
    brd_started_at        = {}       # {station_code: monotonic() when BRD first seen}
    prev_brd              = set()    # stations that were BRD last frame
    last_color_prev       = {}       # {station_code: (r,g,b)} color used last frame

    # quick helpers
    valid_lines = set(LINE_COLORS.keys())            # e.g., {"RD","BL","OR","SV","GR","YL"}
    LED_TO_STATION = {idx: code for code, idx in STATION_TO_LED.items()}

    while should_update:
        now_mono = monotonic()

        # -------- FETCH (rate-limited with cache/backoff) --------
        if now_mono >= next_fetch_time:
            try:
                if wmata_client is None:
                    wmata_client = WMATAClient()
                preds = wmata_client.get_all_station_predictions()
                logging.info("WMATA: fetched %d station predictions", len(preds))

                # Build station->trains map; STRICT BRD only
                station_trains = {}
                for p in preds:
                    station_code = p.get("LocationCode") or p.get("LocationCode1")
                    line_code = (p.get("Line") or p.get("LineCode") or "").upper().strip()
                    raw_min = str(p.get("Min", "")).strip().upper()  # "BRD","ARR","5","--","DLY",...
                    if station_code and line_code in valid_lines and raw_min == "BRD":
                        station_trains.setdefault(station_code, []).append({"line_code": line_code})

                cached_station_trains = station_trains
                last_success_mono = now_mono
                error_count = 0
                next_fetch_time = now_mono + CACHE_TTL
                logging.info("Stations boarding now: %d", len(cached_station_trains))

            except Exception as e:
                error_count += 1
                backoff = min(30 * error_count, 300)
                next_fetch_time = now_mono + backoff
                logging.error("Failed to fetch predictions: %s", e)
                logging.warning("Retrying WMATA fetch in %d s (error %d)", int(backoff), error_count)

        # -------- RENDER from cache every 1s (blink + pre-glow + fades) --------
        try:
            phase = int(time.time())  # 1 Hz blink phase by wall clock
            led_controller.clear()
            current_led_states.clear()

            brd_now = set(cached_station_trains.keys())

            # Start fades for stations that just stopped BRD
            just_stopped = prev_brd - brd_now
            for st in just_stopped:
                color = last_color_prev.get(st)
                if color:
                    fading_leds[st] = {"color": color, "steps": FADE_STEPS}

            last_color_this_frame = {}

            # Render current BRD stations and pre-glow ONE neighbor (not fading)
            for station_code, trains_at_station in cached_station_trains.items():
                led_index = STATION_TO_LED.get(station_code)
                if led_index is None or not trains_at_station:
                    continue

                # Choose color: single solid; multiple blink between their colors
                if len(trains_at_station) == 1:
                    line = trains_at_station[0]["line_code"]
                    color = LINE_COLORS.get(line, (255, 255, 255))
                else:
                    palette = [LINE_COLORS.get(t["line_code"], (255, 255, 255))
                               for t in trains_at_station]
                    color = palette[phase % len(palette)]

                # Full-bright for BRD station
                led_controller.set_pixel(led_index, *color, brightness=1.0)
                current_led_states[led_index] = {"color": list(color), "brightness": 1.0}
                last_color_this_frame[station_code] = color

                # Pre-glow ONE neighbor (direction-agnostic but avoids the just-left/fading station)
                start_t = brd_started_at.setdefault(station_code, monotonic())
                elapsed = monotonic() - start_t
                preglow_b = min(MAX_PREGLOW, (elapsed / PREGLOW_RISE) * MAX_PREGLOW)

                # Candidates: immediate neighbors by LED index
                candidates = []
                for n_idx in (led_index + 1, led_index - 1):  # prefer +1; then -1
                    if not (0 <= n_idx < LED_COUNT):
                        continue
                    neighbor_station = LED_TO_STATION.get(n_idx)
                    if not neighbor_station:
                        continue
                    if neighbor_station in brd_now:          # neighbor already BRD → skip
                        continue
                    if neighbor_station in fading_leds:      # this is likely the just-left station → skip
                        continue
                    candidates.append(n_idx)

                if candidates:
                    n_idx = candidates[0]  # prefer +1 if available due to ordering above
                    led_controller.set_pixel(n_idx, *color, brightness=preglow_b)
                    current_led_states[n_idx] = {"color": list(color), "brightness": preglow_b}

            # Clean BRD start times for stations no longer BRD
            for st in list(brd_started_at.keys()):
                if st not in brd_now:
                    brd_started_at.pop(st, None)

            # Render fade tails for stations that are no longer BRD
            for station_code in list(fading_leds.keys()):
                # Cancel fade if it became BRD again
                if station_code in brd_now:
                    fading_leds.pop(station_code, None)
                    continue
                info = fading_leds[station_code]
                steps = info["steps"]
                if steps <= 0:
                    fading_leds.pop(station_code, None)
                    continue
                led_index = STATION_TO_LED.get(station_code)
                if led_index is None:
                    fading_leds.pop(station_code, None)
                    continue
                r, g, b = info["color"]
                brightness = steps / FADE_STEPS
                led_controller.set_pixel(led_index, r, g, b, brightness=brightness)
                current_led_states[led_index] = {"color": [r, g, b], "brightness": brightness}
                info["steps"] = steps - 1

            led_controller.show()

            # Persist per-frame state
            prev_brd = brd_now
            last_color_prev = last_color_this_frame

        except Exception as e:
            logging.error("LED render error: %s", e)

        # Stale-data warning (rate-limited)
        if last_success_mono > 0 and (now_mono - last_success_mono) > WARN_AFTER and now_mono >= next_warn_time:
            logging.warning("No successful WMATA fetch in 5 minutes.")
            next_warn_time = now_mono + WARN_INTERVAL

        sleep(1.0)

# --------------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------------
@app.route('/')
def index():
    station_data = {
        code: {"index": idx, "name": STATION_NAMES.get(code, code)}
        for code, idx in STATION_TO_LED.items()
    }
    return render_template('index.html', station_data=station_data, line_colors=LINE_COLORS)

@app.route('/led_status')
def led_status():
    """Return current LED states for the web interface."""
    return jsonify({
        "leds": [
            {
                "index": index,
                "color": state.get("color", [0, 0, 0]),
                "brightness": state.get("brightness", 1.0),
                **({} if "pulse" not in state else {"pulse": True})
            }
            for index, state in sorted(current_led_states.items())
        ]
    })

@app.route('/api/status')
def api_status():
    """API endpoint for status checks."""
    return jsonify({
        "status": "running",
        "led_initialized": led_controller.is_initialized(),
        "led_mode": "simulated" if getattr(led_controller, "simulated", False) else "real",
        "auto_updates": bool(update_thread and update_thread.is_alive())
    })

@app.route('/health')
def health():
    mem_usage = get_memory_usage()
    return jsonify({
        "status": "healthy",
        "memory": mem_usage,
        "led_initialized": led_controller.is_initialized(),
        "updates_running": bool(update_thread and update_thread.is_alive())
    })

@app.route('/start_updates', methods=['POST'])
def start_updates():
    """Start the background thread that updates LEDs based on train positions."""
    global update_thread, should_update, wmata_client

    if not led_controller.is_initialized():
        return jsonify({"error": "LED controller not initialized"}), 400

    if update_thread and update_thread.is_alive():
        return jsonify({"status": "already running"})

    try:
        if wmata_client is None:
            wmata_client = WMATAClient()  # no args; reads env/.env internally
        should_update = True
        update_thread = threading.Thread(target=update_leds, daemon=True)
        update_thread.start()
        logger.info("Updater thread started")
        return jsonify({"status": "started"})
    except Exception as e:
        logger.error("Failed to start updates: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/stop_updates', methods=['POST'])
def stop_updates():
    """Stop the background updates and clear the LEDs."""
    global should_update, current_led_states, update_thread

    should_update = False
    if update_thread:
        update_thread.join(timeout=1)

    if led_controller.is_initialized():
        led_controller.clear()
        led_controller.show()

    current_led_states.clear()
    logger.info("Updater thread stopped; LEDs cleared")
    return jsonify({"status": "stopped"})

@app.route('/set_led', methods=['POST'])
def set_led():
    """
    Manually set LED colors.
    Expects JSON body: {"leds": [{"index": 0, "color": [255, 0, 0], "brightness": 1.0}]}
    """
    if not led_controller.is_initialized():
        return jsonify({"error": "LED controller not initialized"}), 400

    data = request.get_json(silent=True) or {}
    if 'leds' not in data or not isinstance(data['leds'], list):
        return jsonify({"error": "Invalid request format"}), 400

    try:
        for led in data['leds']:
            index = led.get('index')
            color = led.get('color')
            brightness = float(led.get('brightness', 1.0))
            if index is not None and isinstance(color, (list, tuple)) and len(color) == 3:
                led_controller.set_pixel(index, *color)
                current_led_states[index] = {"color": list(color), "brightness": brightness}
        led_controller.show()
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("set_led failed: %s", e)
        return jsonify({"error": str(e)}), 400

# -----------------------------------
# Debug helpers for connectivity/tests
# -----------------------------------
@app.route('/debug/wmata', methods=['GET'])
def debug_wmata():
    """Call WMATA and return a tiny sample to prove connectivity."""
    global wmata_client
    if wmata_client is None:
        wmata_client = WMATAClient()
    data = wmata_client.get_train_positions()
    sample = data[:3]
    return jsonify({"count": len(data), "sample": sample})

@app.route('/debug/fake', methods=['POST'])
def debug_fake():
    """Populate a couple of LEDs to test the web UI without WMATA."""
    global current_led_states
    led_controller.clear()
    # Example indices; adjust if desired
    led_controller.set_pixel(14, 255, 0, 0)   # e.g., Metro Center red
    led_controller.set_pixel(44, 0, 0, 255)   # e.g., L'Enfant blue
    current_led_states = {
        14: {"color": [255, 0, 0], "brightness": 1.0},
        44: {"color": [0, 0, 255], "brightness": 1.0},
    }
    led_controller.show()
    return {"ok": True}

# --------------------------------------------------------------------------------------
# Utils
# --------------------------------------------------------------------------------------
def get_memory_usage():
    """Get current memory usage of the system."""
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = {}
            for line in f:
                key, value = line.split(':')
                value = value.strip().split()[0]
                mem_info[key] = int(value)

        total = mem_info.get('MemTotal', 0)
        available = mem_info.get('MemAvailable', 0)
        used = total - available

        usage = {
            'total_mb': total / 1024,
            'used_mb': used / 1024,
            'available_mb': available / 1024,
            'usage_percent': (used / total) * 100 if total > 0 else 0
        }

        # Auto-restart if critically high (optional safeguard)
        if usage['usage_percent'] > 95:
            logger.error("Critical memory usage - requesting restart")
            try:
                import subprocess
                subprocess.run(['systemctl', 'restart', 'metro-map'], check=False)
            except Exception as e:
                logger.error("Failed to request restart: %s", e)

        return usage
    except Exception as e:
        logger.error("Error checking memory usage: %s", e)
        return None

# --------------------------------------------------------------------------------------
# Startup helpers
# --------------------------------------------------------------------------------------
def start_auto_updates():
    """Start updater thread if not already running."""
    global update_thread, should_update
    if not update_thread or not update_thread.is_alive():
        should_update = True
        update_thread = threading.Thread(target=update_leds, daemon=True)
        update_thread.start()
        logger.info("Auto-updates started")

if __name__ == '__main__':
    # Start updates when running directly (also covered by before_serving)
    try:
        start_auto_updates()
    except Exception as e:
        logger.error("Failed to start auto updates in __main__: %s", e)

    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
