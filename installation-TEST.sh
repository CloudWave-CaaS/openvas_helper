#!/bin/bash

set -e

# Define paths
SERVICE_FILE="/etc/systemd/system/openvas_listener.service"
BIN_DIR="/usr/local/bin"
LOG_DIR="/var/log/scans"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Download scripts
wget -O "$BIN_DIR/Chronicle-Convert-Service.py" "https://raw.githubusercontent.com/CloudWave-CaaS/openvas_helper/refs/heads/main/Chronicle-Convert-Service.py"
wget -O "$BIN_DIR/Chronicle-Convert.py" "https://raw.githubusercontent.com/CloudWave-CaaS/openvas_helper/refs/heads/main/Chronicle-Convert.py"

# Set execute permissions
chmod +x "$BIN_DIR/Chronicle-Convert-Service.py"
chmod +x "$BIN_DIR/Chronicle-Convert.py"

# Install systemd service
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=OpenVAS XML to JSON Listener Service
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


echo "Installation complete. Service configuration updated."
