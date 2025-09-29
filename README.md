# DC Metro Map LED Display

This project displays real-time DC Metro train positions using WS281x LED strips on a Raspberry Pi Zero W2.

## Hardware Requirements

1. Raspberry Pi Zero W2
2. WS281x LED strip (at least 27 LEDs for the Red Line stations)
3. 5V power supply capable of powering your LED strip
4. Three wires to connect the LED strip to the Pi

## Hardware Setup

1. Connect the LED strip to your Raspberry Pi:
   - Ground (GND) → Pi GND pin
   - Power (5V) → Pi 5V pin
   - Data Input (DI) → Pi GPIO18 (default)

   Note: If using a long LED strip or many LEDs, power the strip directly from the power supply rather than through the Pi.

## Software Setup

1. Get a WMATA API key:
   - Visit https://developer.wmata.com/
   - Sign up for a free account
   - Create a new API key

2. Install required system packages:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git
```

3. Clone and set up the project:
```bash
cd ~
git clone https://github.com/thenotoriousJeremy/metro-map.git
cd metro-map
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Create a `.env` file with your WMATA API key:
```bash
echo "WMATA_API_KEY=your-api-key-here" > .env
```

5. Set up the systemd service:
```bash
sudo cp metro-map.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable metro-map
sudo systemctl start metro-map
```

## Testing the Setup

1. Check if the service is running:
```bash
sudo systemctl status metro-map
```

2. View the logs:
```bash
sudo journalctl -u metro-map -f
```

3. Test the web interface:
   - Open a web browser to `http://<your-pi-ip>:5000`
   - Click "Start Updates" to begin displaying train positions
   - The LED strip should start showing train positions with comet effects

## Configuration

You can adjust several settings:

1. LED strip configuration in `led_controller.py`:
   - `LED_COUNT`: Number of LEDs in your strip
   - `PIN`: GPIO pin number (default: 18)
   - `BRIGHTNESS`: LED brightness (0-255)

2. Station mapping in `config.py`:
   - Maps station codes to LED indices
   - Adjust if you want to change which LED represents each station

3. Update frequency in `app.py`:
   - Change `time.sleep(10)` to adjust how often positions update

## Troubleshooting

1. If LEDs don't light up:
   - Check physical connections
   - Ensure correct GPIO pin is set in `led_controller.py`
   - Run `sudo chmod a+rw /dev/mem` to give LED access permission

2. If web interface shows "LED controller not initialized":
   - The script might not have permission to access GPIO
   - Try running with sudo: `sudo -E python app.py`

3. If no train data appears:
   - Verify your WMATA API key in .env file
   - Check internet connectivity
   - Look for error messages in the logs

4. If service fails to start:
   - Check logs: `sudo journalctl -u metro-map -n 50`
   - Verify Python virtual environment path in service file

## API Endpoints

- `GET /` - Web interface
- `GET /api/status` - Service status
- `POST /start_updates` - Start train position updates
- `POST /stop_updates` - Stop updates
- `GET /led_status` - Current LED states
- `POST /set_led` - Manually control LEDs
