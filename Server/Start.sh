#!/bin/bash

# EMA Server Startup Script

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 EMA Server Startup${NC}"
echo "================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}📚 Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Create database if it doesn't exist
echo -e "${BLUE}🗄️  Initializing database...${NC}"
python3 << 'PYTHON_EOF'
from app import db, app
with app.app_context():
    db.create_all()
PYTHON_EOF

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}📊 Starting EMA Server in background...${NC}"
echo "================================"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the Flask application in background
LOG_FILE="logs/ema_$(date +%Y%m%d_%H%M%S).log"
nohup python3 app.py > "$LOG_FILE" 2>&1 &
PID=$!

echo -e "${GREEN}✨ Server started with PID: $PID${NC}"
echo -e "${GREEN}✨ Listening on http://localhost:5000${NC}"
echo -e "${GREEN}🔐 Admin panel: http://localhost:5000/admin/${NC}"
echo -e "${GREEN}📝 Default login: admin / admin123${NC}"
echo ""
echo -e "${BLUE}📝 Log file: $LOG_FILE${NC}"
echo -e "${BLUE}View logs: tail -f $LOG_FILE${NC}"
echo -e "${BLUE}Stop server: kill $PID${NC}"
echo "================================"

# Save PID to file for easy reference
echo $PID > .ema_pid
