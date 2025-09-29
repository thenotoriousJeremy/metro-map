#!/usr/bin/env bash
# Install script to prepare the Pi and enable the metro-map service.
set -euo pipefail

# Ensure script is run as root
if [ "$(id -u)" -ne 0 ]; then 
  echo "Please run as root (use sudo)"
  exit 1
fi

PROJECT_DIR=/home/jeremy/metro-map
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

# Set up permissions for LED strip and GPIO
usermod -a -G gpio jeremy
chmod a+rw /dev/mem
chmod a+rw /dev/gpiomem

# Set correct ownership
chown -R jeremy:jeremy "$PROJECT_DIR"

# Create venv and install dependencies as jeremy user
su - jeremy << EOF
cd "$PROJECT_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Check for .env file
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create it with your WMATA API key:"
    echo "echo 'WMATA_API_KEY=your-api-key-here' > .env"
fi

# Set up minimal runtime directory in RAM
mkdir -p /run/metro-map
chown pi:pi /run/metro-map
chmod 755 /run/metro-map

# Copy service files and enable
cp "$PROJECT_DIR/$SERVICE_NAME" /etc/systemd/system/
cp "$PROJECT_DIR/scripts/metro-map-restart.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable metro-map metro-map-restart.timer
systemctl start metro-map metro-map-restart.timer

# Add minimal RAM disk mount to fstab if not already present
if ! grep -q "/run/metro-map" /etc/fstab; then
    echo "tmpfs /run/metro-map tmpfs size=5M,mode=0755,uid=pi,gid=pi,noexec 0 0" >> /etc/fstab
    mount /run/metro-map
fi

# Configure system for low memory usage
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    cat >> /etc/sysctl.conf << EOF
# Optimize for low memory usage
vm.swappiness = 10
vm.dirty_background_ratio = 1
vm.dirty_ratio = 50
vm.dirty_writeback_centisecs = 12000
EOF
    sysctl -p
fi

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
