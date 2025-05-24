#!/bin/bash

set -e

# Define version
VERSION="1.2.1"

# Define paths
SERVICE_FILE="/etc/systemd/system/openvas_listener.service"
BIN_DIR="/usr/local/bin"
LOG_DIR="/var/log/scans"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Remove existing service file if it exists
if [ -f "$SERVICE_FILE" ]; then
    systemctl stop openvas_listener || true
    systemctl disable openvas_listener || true
    rm -f "$SERVICE_FILE"
fi

# Remove existing scripts if they exist
rm -f "$BIN_DIR/Chronicle-Convert-Service.py" "$BIN_DIR/Chronicle-Convert.py"

# Download scripts
wget -O "$BIN_DIR/Chronicle-Convert-Service.py" "https://raw.githubusercontent.com/CloudWave-CaaS/openvas_helper/refs/heads/main/Chronicle-Convert-Service.py"
wget -O "$BIN_DIR/Chronicle-Convert.py" "https://raw.githubusercontent.com/CloudWave-CaaS/openvas_helper/refs/heads/main/Chronicle-Convert.py"

# Set execute permissions
chmod +x "$BIN_DIR/Chronicle-Convert-Service.py"
chmod +x "$BIN_DIR/Chronicle-Convert.py"

# Install systemd service
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=OpenVAS XML to JSON Listener Service v$VERSION
After=network.target

[Service]
ExecStart=/usr/bin/python3 $BIN_DIR/Chronicle-Convert-Service.py
Restart=always
User=root
WorkingDirectory=$BIN_DIR
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=openvas_listener

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable openvas_listener
systemctl restart openvas_listener

echo "Installation complete. Service configuration updated to version $VERSION."
