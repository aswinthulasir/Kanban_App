#!/bin/bash

echo "======================================"
echo "   TodoKanban Application Startup"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads data

echo ""
echo "======================================"
echo "   Starting FastAPI Application"
echo "======================================"
echo ""
echo "Application will be available at:"
echo "  - Main App: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
