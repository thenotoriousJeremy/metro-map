#!/usr/bin/env bash
# Install script to prepare the Pi and enable the metro-map service.
set -euo pipefail

PROJECT_DIR=/home/pi/metro-map
SERVICE_NAME=metro-map.service

# Assumes repo already cloned into $PROJECT_DIR
cd "$PROJECT_DIR"

# Create venv and install
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Copy service and enable
sudo cp "$PROJECT_DIR/$SERVICE_NAME" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now $SERVICE_NAME

echo "metro-map installed and service enabled"
