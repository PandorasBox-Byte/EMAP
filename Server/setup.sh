#!/bin/bash

# EMA Server Development Setup Script
# Initializes database, installs dependencies, and starts server

set -e

echo "🚀 Starting EMA Server Setup..."
echo ""

# Check Python version
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if ! python3 -m venv venv; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
source venv/bin/activate
echo "✅ Virtual environment created and activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
if ! pip install -r requirements.txt; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check/Create .env file
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please update .env with your database configuration"
else
    echo "✅ .env file exists"
fi
echo ""

# Database initialization
echo "🗄️  Initializing database..."
python3 -c "
from app import app, db

with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created successfully')
    except Exception as e:
        print(f'⚠️  Database init: {e}')
"
echo ""

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  1. source venv/bin/activate"
echo "  2. python app.py"
echo ""
echo "Or with Gunicorn (production):"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
