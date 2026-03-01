#!/bin/bash

# EMA Server Setup - Simplified Setup Script
# For development environment

echo "🚀 EMA Server Setup"
echo "===================="

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "⚙️  Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created (edit with your settings)"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from app import db, app
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 To start the development server:"
echo "   1. Activate venv: source venv/bin/activate"
echo "   2. Run: python app.py"
echo "   3. Admin panel: http://localhost:5000/admin/"
echo ""
echo "📝 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  For production deployment, use deploy_to_linux.sh"
