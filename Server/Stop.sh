#!/bin/bash

# EMA Server Stop Script

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping EMA Server${NC}"
echo "================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Read PID from saved file
if [ -f ".ema_pid" ]; then
    PID=$(cat .ema_pid)
    if kill $PID 2>/dev/null; then
        echo -e "${GREEN}✅ Server stopped (PID: $PID)${NC}"
        rm .ema_pid
    else
        echo -e "${RED}❌ Server with PID $PID not found or already stopped${NC}"
        rm .ema_pid
    fi
else
    # Try to find and kill any Python processes running app.py
    PKG=$(pgrep -f "python3 app.py" || true)
    if [ ! -z "$PKG" ]; then
        kill $PKG 2>/dev/null
        echo -e "${GREEN}✅ Stopped processes: $PKG${NC}"
    else
        echo -e "${RED}❌ No EMA server process found${NC}"
    fi
fi

echo "================================"
