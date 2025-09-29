#!/usr/bin/env bash
# Install script to prepare the Pi and enable the metro-map service.
set -euo pipefail

# Ensure script is run as root
if [ "$(id -u)" -ne 0 ]; then 
  echo "Please run as root (use sudo)"
  exit 1
fi

PROJECT_DIR=/home/pi/metro-map
SERVICE_NAME=metro-map.service

# Install system dependencies
apt update
apt install -y python3-pip python3-venv git

# Ensure project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: $PROJECT_DIR not found. Please clone the repository first:"
  echo "git clone https://github.com/thenotoriousJeremy/metro-map.git $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

# Set up permissions for LED strip
chmod a+rw /dev/mem

# Create venv and install dependencies
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create it with your WMATA API key:"
    echo "echo 'WMATA_API_KEY=your-api-key-here' > .env"
fi

# Copy service and enable
cp "$PROJECT_DIR/$SERVICE_NAME" /etc/systemd/system/
systemctl daemon-reload
systemctl enable metro-map
systemctl start metro-map

# Print status information
echo "Installation complete!"
echo
echo "Please ensure you have:"
echo "1. Set up your WMATA API key in .env file"
echo "2. Connected your LED strip to GPIO18"
echo "3. Adjusted LED count in config.py if needed"
echo
echo "The web interface should be available at:"
echo "http://$(hostname -I | cut -d' ' -f1):5000"
echo
echo "View the logs with: sudo journalctl -u metro-map -f"
