#!/bin/bash

set -e

# Define paths
SERVICE_FILE="/etc/systemd/system/openvas_listener.service"
OTEL_CONFIG="/opt/observiq-otel-collector/config.yaml"
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

# Modify ObservIQ OpenTelemetry config
if [ -f "$OTEL_CONFIG" ]; then
    # Comment out the existing tcplog section
    sed -i '/tcplog:/,/^$/ s/^/#/' "$OTEL_CONFIG"
    
    # Add filelog configuration
    cat <<EOT >> "$OTEL_CONFIG"
filelog/openvas_results:
    include:
    - /var/log/scans/*.csv
    - /var/log/scans/*.json
    attributes:
      chronicle_log_type: OPENVAS
EOT

    # Replace "- tcplog" with "- filelog/nix_system"
    sed -i 's/- tcplog/- filelog\/nix_system/g' "$OTEL_CONFIG"

    # Restart ObservIQ collector
    systemctl restart observiq-otel-collector
fi

echo "Installation complete. Service and OpenTelemetry configuration updated."
