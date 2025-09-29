# DC Metro Map LED Display

Real-time DC Metro train positions displayed on WS281x LED strips using a Raspberry Pi Zero W2. Features automatic daily restarts, memory management, and error recovery for reliable 24/7 operation.

## Hardware Requirements

1. Raspberry Pi Zero W2 (recommended) or any Raspberry Pi with WiFi
2. WS281x LED strip (99 LEDs needed for full system map)
3. 5V power supply:
   - For <30 LEDs: Standard 2.5A Pi power supply works
   - For full map (99 LEDs): 5V/10A power supply recommended
4. Connection wires (22-20 AWG recommended)
5. Optional: Project box or case

## Hardware Setup

1. Power setup:
   - **For <30 LEDs**: Connect LED strip's power directly to Pi's 5V and GND
   - **For full map**:
     - Connect power supply's GND to both Pi's GND and LED strip's GND
     - Connect power supply's 5V directly to LED strip's 5V
     - Connect Pi's GND to LED strip's GND (ensure common ground)

2. LED strip connections:
   ```
   LED Strip    →   Raspberry Pi
   GND         →   GND (Pin 6)
   DI (Data)   →   GPIO18 (Pin 12)
   5V          →   See power setup above
   ```

3. Important notes:
   - Keep data wire (DI) short to prevent signal issues
   - Use capacitors across power/ground if seeing glitches
   - Consider level shifter if seeing unreliable behavior

## Software Installation

1. Set up Raspberry Pi OS:
   ```bash
   # Download Raspberry Pi OS Lite (64-bit recommended)
   # Flash to SD card using Raspberry Pi Imager
   # Enable SSH and configure WiFi in Imager
   ```

2. First boot setup:
   ```bash
   # SSH into your Pi
   ssh pi@your-pi-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   ```

3. Install required packages:
   ```bash
   sudo apt install -y python3-pip python3-venv git
   ```

4. Get WMATA API key:
   - Visit https://developer.wmata.com/
   - Sign up for free account
   - Create new primary key
   - Save key for next steps

5. Clone and setup project:
   ```bash
   # Clone repository
   cd ~
   git clone https://github.com/thenotoriousJeremy/metro-map.git
   cd metro-map

   # Create and activate virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

6. Configure environment:
   ```bash
   # Create .env file with your WMATA API key
   echo "WMATA_API_KEY=your-key-here" > .env

   # Set permissions for LED control
   sudo chmod a+rw /dev/mem
   ```

7. Run installation script:
   ```bash
   # Make script executable
   chmod +x scripts/install-on-pi.sh

   # Run installer
   sudo ./scripts/install-on-pi.sh
   ```

## System Configuration

The installer automatically configures:

1. Systemd service for automatic startup
2. Daily restart timer at 4 AM
3. RAM-based runtime directory
4. Memory optimization settings
5. SD card write reduction

To manually control the service:
```bash
# Check status
sudo systemctl status metro-map

# Start/stop service
sudo systemctl start metro-map
sudo systemctl stop metro-map

# View logs
sudo journalctl -u metro-map -f

# Check timer status
sudo systemctl list-timers metro-map-restart.timer
```

## Web Interface

Access the control interface at:
```
http://<your-pi-ip>:5000
```

Features:
- Start/stop updates
- View LED status
- Monitor system health
- Real-time train positions

## Monitoring & Maintenance

1. Health endpoint:
   ```
   http://<your-pi-ip>:5000/health
   ```
   Shows:
   - Memory usage
   - LED controller status
   - Update thread status

2. Automatic maintenance:
   - Daily restart at 4 AM
   - Automatic restart if memory exceeds 95%
   - Progressive error backoff
   - Network connectivity monitoring

3. Log viewing:
   ```bash
   # View service logs
   sudo journalctl -u metro-map -f

   # View last 100 logs
   sudo journalctl -u metro-map -n 100

   # View logs since last boot
   sudo journalctl -u metro-map -b
   ```

## Customization

1. LED configuration (`config.py`):
   - Adjust `STATION_TO_LED` mapping
   - Modify `LINE_COLORS` if needed
   - Change `LED_COUNT` for different strip lengths

2. Update frequency (`app.py`):
   - Default: 10 seconds
   - Modify `time.sleep(10)` in update loop

3. Memory thresholds (`app.py`):
   - Warning at 85% usage
   - Restart at 95% usage

4. Restart time (`scripts/metro-map-restart.timer`):
   - Default: 4 AM
   - Modify `OnCalendar` setting

## Troubleshooting

1. LEDs not working:
   - Check physical connections
   - Verify permissions: `sudo chmod a+rw /dev/mem`
   - Test LED strip: `python map_stations.py`

2. No train updates:
   - Check WMATA API key in `.env`
   - Verify network connection
   - Check service logs for errors

3. Service won't start:
   - Check logs: `sudo journalctl -u metro-map -n 50`
   - Verify Python environment
   - Check file permissions

4. High memory usage:
   - Monitor `/health` endpoint
   - Check logs for memory warnings
   - Service will auto-restart if critical

5. System freezes:
   - Wait for automatic daily restart
   - Manual restart: `sudo systemctl restart metro-map`
   - Check SD card health

## Support

For issues, please:
1. Check the logs first
2. Open an issue on GitHub with:
   - Log output
   - Hardware details
   - Steps to reproduce

## License

MIT License - See LICENSE file for details
