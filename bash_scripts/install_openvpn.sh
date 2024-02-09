#!/bin/bash

# Access variables
config_file_path="$1"

# Update and install OpenVPN
sudo apt update
sudo apt install openvpn -y

# Create a new systemd service file for OpenVPN
cat << EOF | sudo tee /etc/systemd/system/openvpn-custom.service > /dev/null
[Unit]
Description=Custom OpenVPN client instance
After=network.target

[Service]
ExecStart=/usr/sbin/openvpn --config $config_file_path
Restart=always
RestartSec=3
Type=simple

[Install]
WantedBy=multi-user.target
EOF

# Reload Systemd, enable, and start the OpenVPN service
sudo systemctl daemon-reload
sudo systemctl enable openvpn-custom
sudo systemctl start openvpn-custom

# Optionally, check the service status
# sudo systemctl status openvpn-custom
