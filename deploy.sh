#!/bin/bash
# Deployment script for Ubuntu/Debian servers

set -e  # Exit on error

echo "=================================="
echo "Ghana Legal Scraper - Deployment"
echo "=================================="

# Check Python version
python3 --version

# Create application directory
INSTALL_DIR="/opt/ghana-legal-scraper"
mkdir -p $INSTALL_DIR

# Copy files to installation directory
echo "Installing files..."
cp -r . $INSTALL_DIR/

# Change to installation directory
cd $INSTALL_DIR

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data/raw data/processed data/logs data/stats

# Set permissions
chown -R www-data:www-data $INSTALL_DIR
chmod -R 755 $INSTALL_DIR

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/glis-api.service > /dev/null <<EOF
[Unit]
Description=Ghana Legal Scraper API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python main.py api --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable glis-api
sudo systemctl start glis-api

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "API Server started and running on http://localhost:8000"
echo ""
echo "View API documentation at:"
echo "  http://localhost:8000/docs"
echo ""
echo "Check service status:"
echo "  sudo systemctl status glis-api"
echo ""
echo "View logs:"
echo "  sudo journalctl -u glis-api -f"
echo ""
echo "Next steps:"
echo "1. Configure nginx as reverse proxy (optional)"
echo "2. Set up SSL/TLS with Let's Encrypt"
echo "3. Run scraping campaign: python main.py scrape"
echo ""
