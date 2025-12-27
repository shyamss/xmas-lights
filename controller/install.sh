#!/bin/bash

# install.sh
# Bootstrap installation script for Orange Pi / Raspberry Pi
# Downloads latest code from Google Cloud Storage and installs services.
# Usage: curl -sL https://storage.googleapis.com/<PROJECT_ID>-animations/install.sh | sudo bash -s <PROJECT_ID>

set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: sudo ./install.sh <GCP_PROJECT_ID>"
    exit 1
fi

INSTALL_DIR="/opt/xmas-lights"
USER="root"
BUCKET_BASE="https://storage.googleapis.com/${PROJECT_ID}-animations"
TAR_URL="${BUCKET_BASE}/controller.tar.gz"

echo "=== Xmas Lights Installer ==="
echo "Project: $PROJECT_ID"
echo "Install Dir: $INSTALL_DIR"

# 1. Install System Dependencies
echo "Installing dependencies..."
if command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y python3-pip python3-venv git curl tar build-essential python3-dev
else
    echo "Warning: apt-get not found. Ensure python3, pip, venv are installed."
fi

# 2. Prepare Directory
echo "Setting up directory..."
mkdir -p $INSTALL_DIR
# Clean old files to ensure fresh install
rm -rf $INSTALL_DIR/controller

# 3. Download and Extract Code
echo "Downloading controller code from $TAR_URL..."
curl -f -L $TAR_URL -o /tmp/controller.tar.gz
# Extract into INSTALL_DIR. The tarball should contain the 'controller' directory.
tar -xzf /tmp/controller.tar.gz -C $INSTALL_DIR
rm /tmp/controller.tar.gz

# 4. Setup Virtual Environment
echo "Creating virtual environment..."
cd $INSTALL_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install spidev requests

# 5. Create Service for Main Controller
echo "Creating Systemd Service: xmas-lights..."
cat <<EOF > /etc/systemd/system/xmas-lights.service
[Unit]
Description=Xmas Lights Controller
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/controller
# The tarball creates a 'controller' subdir
ExecStart=$INSTALL_DIR/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Create Service for Updater
echo "Creating Systemd Service: xmas-updater..."
ANIM_URL="${BUCKET_BASE}/current_anim.py"

cat <<EOF > /etc/systemd/system/xmas-updater.service
[Unit]
Description=Xmas Lights Updater
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/controller/updater.py --url $ANIM_URL --dest $INSTALL_DIR/controller/generated_anim.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

# 7. Reload and Enable
echo "Enabling services..."
systemctl daemon-reload
systemctl enable xmas-lights
systemctl enable xmas-updater
systemctl restart xmas-lights
systemctl restart xmas-updater

echo "Installation Complete!"
echo "Services are running."