#!/bin/bash

set -e

echo "🏦 Setting up Loan Approval AI System..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Virtual environment is activated and ready to use."
echo ""
echo "To get started:"
echo "  1. Make sure venv is activated:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start all services:"
echo "     chmod +x run_all_services.sh"
echo "     ./run_all_services.sh"
echo ""
echo "  3. Open browser to http://localhost:8501"
echo ""
echo "═══════════════════════════════════════════════════════════════"
