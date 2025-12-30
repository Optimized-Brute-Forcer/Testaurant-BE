#!/bin/bash
set -e

echo "========================================="
echo "Testaurant Backend - EC2 Deployment"
echo "========================================="

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "Error: Python 3.11 is not installed."
    echo "Please install Python 3.11 first:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.11 python3.11-venv python3.11-dev"
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "Warning: .env file not found!"
    echo "Please create .env file with required environment variables."
    echo "You can use .env.example as a template:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "To start the application manually:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8080"
echo ""
echo "To set up as a systemd service, run:"
echo "  sudo bash setup_service.sh"
echo ""
