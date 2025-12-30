#!/bin/bash
set -e

echo "========================================="
echo "Setting up Testaurant as systemd service"
echo "========================================="

# Get the current directory
APP_DIR=$(pwd)
APP_USER=$(whoami)

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/testaurant.service"

echo "Creating systemd service file at $SERVICE_FILE..."

cat > $SERVICE_FILE << EOF
[Unit]
Description=Testaurant Backend API
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling testaurant service..."
systemctl enable testaurant

# Start service
echo "Starting testaurant service..."
systemctl start testaurant

# Show status
echo ""
echo "========================================="
echo "Service Setup Complete!"
echo "========================================="
echo ""
echo "Service status:"
systemctl status testaurant --no-pager
echo ""
echo "Useful commands:"
echo "  sudo systemctl status testaurant   # Check service status"
echo "  sudo systemctl restart testaurant  # Restart service"
echo "  sudo systemctl stop testaurant     # Stop service"
echo "  sudo journalctl -u testaurant -f   # View logs"
echo ""
