#!/bin/bash

# deploy.sh - Setup script for PDF Extractor on a server

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment setup for PDF Extractor..."

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 3. Activate Virtual Environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# 4. Install Dependencies
echo "⬇️  Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Deployment setup complete!"
echo ""
echo "To run the application in production (using gunicorn):"
echo "  source venv/bin/activate"
echo "  gunicorn -w 4 -b 0.0.0.0:8000 app:app"
echo ""
echo "To run the application in development mode:"
echo "  source venv/bin/activate"
echo "  python app.py"

# 5. Run the application
python app.py


