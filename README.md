Install with:
`curl -sSL https://raw.githubusercontent.com/CloudWave-CaaS/openvas_helper/refs/heads/main/installation-TEST.sh | bash`

These scripts convert OpenVAS output to JSON for easy ingestion.

OPTIONAL:  Install a Service
```
[Unit]
Description=OpenVAS XML to JSON Listener Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/Chronicle-Convert-Service.py
Restart=always
User=root
WorkingDirectory=/usr/local/bin/
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=openvas_listener

[Install]
WantedBy=multi-user.target
```
