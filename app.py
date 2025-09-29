"""Metro map LED display app for Raspberry Pi.

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
import json
from flask import Flask, jsonify, request, render_template
from led_controller import LEDController
from wmata_client import WMATAClient
from config import STATION_TO_LED, LINE_COLORS, LED_COUNT
import threading
import time

# Load station names
with open('station_names.json', 'r') as f:
    STATION_NAMES = json.load(f)

app = Flask(__name__)
led_controller = LEDController(led_count=LED_COUNT)
wmata_client = None
update_thread = None
should_update = False

# Dictionary to store current LED states
current_led_states = {}

def update_leds():
    """Background thread to update LEDs based on real-time train positions."""
    global should_update, current_led_states
    while should_update:
        try:
            # Get current train positions
            trains = wmata_client.get_train_positions()
            
            # Clear all LEDs and states
            led_controller.clear()
            current_led_states.clear()
            
            # Collect trains at each station
            station_trains = {}
            for train in trains:
                station_code = train.get('StationCode')
                line_code = train.get('LineCode')
                direction_num = train.get('DirectionNum')
                
                if station_code and line_code:
                    if station_code not in station_trains:
                        station_trains[station_code] = []
                    station_trains[station_code].append({
                        'line_code': line_code,
                        'direction_num': direction_num
                    })
            
            # Update LEDs based on trains at each station
            for station_code, trains_at_station in station_trains.items():
                led_index = STATION_TO_LED.get(station_code)
                if led_index is not None:
                    if len(trains_at_station) == 1:
                        # Single train - use its color
                        train = trains_at_station[0]
                        color = LINE_COLORS.get(train['line_code'], (255, 255, 255))
                        direction = "right" if train['direction_num'] == 1 else "left"
                        led_controller.set_comet(led_index, *color, direction=direction)
                        current_led_states[led_index] = {"color": color, "brightness": 1.0}
                    else:
                        # Multiple trains - blend colors
                        r, g, b = 0, 0, 0
                        for train in trains_at_station:
                            color = LINE_COLORS.get(train['line_code'], (255, 255, 255))
                            r += color[0]
                            g += color[1]
                            b += color[2]
                        
                        # Average the colors and ensure they don't exceed 255
                        count = len(trains_at_station)
                        color = (
                            min(255, r // count),
                            min(255, g // count),
                            min(255, b // count)
                        )
                        
                        # For multiple trains, pulse the LED instead of showing direction
                        led_controller.set_pixel(led_index, *color)
                        current_led_states[led_index] = {
                            "color": color,
                            "brightness": 1.0,
                            "pulse": True  # Add pulse flag for multiple trains
                        }
            
            # Show the updates
            led_controller.show()
            
            # Wait before next update
            time.sleep(10)  # Update every 10 seconds
        except Exception as e:
            print(f"Error updating LEDs: {e}")
            time.sleep(30)  # Wait longer on error

@app.route('/')
def index():
    # Create a dictionary of station information for the template
    station_data = {}
    for code, index in STATION_TO_LED.items():
        station_data[code] = {
            "index": index,
            "name": STATION_NAMES.get(code, code)
        }
    
    return render_template('index.html', 
                         station_data=station_data,
                         line_colors=LINE_COLORS)

@app.route('/led_status')
def led_status():
    """Return current LED states for the web interface."""
    return jsonify({
        "leds": [
            {
                "index": index,
                "color": state["color"],
                "brightness": state["brightness"]
            }
            for index, state in current_led_states.items()
        ]
    })

@app.route('/api/status')
def api_status():
    """API endpoint for status checks."""
    return jsonify({
        "status": "running",
        "led_initialized": led_controller.is_initialized(),
        "auto_updates": bool(update_thread and update_thread.is_alive())
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

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
            wmata_client = WMATAClient()
        
        should_update = True
        update_thread = threading.Thread(target=update_leds)
        update_thread.daemon = True
        update_thread.start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_updates', methods=['POST'])
def stop_updates():
    """Stop the background updates and clear the LEDs."""
    global should_update, current_led_states
    
    should_update = False
    if update_thread:
        update_thread.join(timeout=1)
    
    if led_controller.is_initialized():
        led_controller.clear()
        led_controller.show()
    
    current_led_states.clear()
    return jsonify({"status": "stopped"})

@app.route('/set_led', methods=['POST'])
def set_led():
    """Manually set LED colors. Expects JSON body: {"leds": [{"index": 0, "color": [255,0,0]}]}"""
    if not led_controller.is_initialized():
        return jsonify({"error": "LED controller not initialized"}), 400
        
    data = request.get_json()
    if not data or 'leds' not in data:
        return jsonify({"error": "Invalid request format"}), 400
    
    try:
        for led in data['leds']:
            index = led.get('index')
            color = led.get('color')
            if index is not None and color and len(color) == 3:
                led_controller.set_pixel(index, *color)
                current_led_states[index] = color
        led_controller.show()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
