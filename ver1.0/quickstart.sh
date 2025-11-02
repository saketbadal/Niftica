#!/bin/bash
# quickstart.sh

echo "🚀 Nifty Options AI Recommender - Quick Start"
echo "============================================"

# Check prerequisites
echo "Checking prerequisites..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python $python_version found"

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi
echo "✅ gcloud CLI found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials!"
    echo "   Run: nano .env"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs reports

# Run tests
echo ""
echo "Running tests..."
python -m pytest tests/ -v

# Setup Firestore (optional)
echo ""
read -p "Do you want to setup Firestore collections? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/setup_firestore.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run locally: python app.py"
echo "3. Deploy to GCP: ./deploy.sh"
echo ""
echo "For help, see README.md"