#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Website Builder — One-command startup script
#
# Starts BOTH the Flask backend (port 5000) and the React frontend (port 3000)
# together, so you never have to wonder which URL to open.
#
# Usage:   ./start.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Website Builder — Starting up...                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"

# ─── Check prerequisites ────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 is not installed${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi

# ─── Set up backend ─────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/3] Setting up Flask backend...${NC}"
cd flask-backend

if [ ! -d "venv" ]; then
    echo "    Creating virtual environment..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate
pip install -q -r ../requirements.txt
echo -e "${GREEN}    ✓ Backend dependencies ready${NC}"

# ─── Set up frontend ────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[2/3] Setting up React frontend...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "    Installing npm packages (this may take a moment)..."
    npm install --silent
fi
echo -e "${GREEN}    ✓ Frontend dependencies ready${NC}"

# ─── Start both services ────────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/3] Starting services...${NC}"
cd "$SCRIPT_DIR"

# Trap Ctrl+C to kill both processes cleanly
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill "$BACKEND_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

# Start backend
cd flask-backend
source venv/bin/activate
python run.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}    ✓ Backend started  (PID $BACKEND_PID) → http://localhost:5000${NC}"

# Wait a moment for backend to come up
sleep 3

# Start frontend
cd frontend
BROWSER=none npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}    ✓ Frontend started (PID $FRONTEND_PID) → http://localhost:3000${NC}"

# ─── Summary ────────────────────────────────────────────────────────────────
sleep 2
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🚀  READY  🚀                         ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║  👉 OPEN THIS IN YOUR BROWSER:                           ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║     ${GREEN}http://localhost:3000${BLUE}                             ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║  (The backend API lives at http://localhost:5000)        ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║  Admin login:  admin@websitebuilder.com / Admin@1234     ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║  Logs:  backend.log  ·  frontend.log                     ║${NC}"
echo -e "${BLUE}║  Stop:  Ctrl+C                                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Keep the script running and stream logs
tail -f backend.log frontend.log
