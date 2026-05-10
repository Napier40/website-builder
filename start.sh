#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Website Builder — One-command startup (macOS / Linux)
#
# Starts BOTH the Flask backend (port 5000) and the React frontend (port 3000)
# together, with colour-coded interleaved logs and graceful Ctrl+C shutdown.
#
# Usage:     ./start.sh
# Stop:      Ctrl+C   (kills both processes cleanly)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ─── Colours ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

BACKEND_PORT=${BACKEND_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

BACKEND_PID=""
FRONTEND_PID=""

# ─── Helpers ────────────────────────────────────────────────────────────────
log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[  OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERR ]${NC} $*" >&2; }

port_in_use() {
    local port=$1
    if command -v lsof &>/dev/null; then
        lsof -iTCP:"$port" -sTCP:LISTEN -P -n &>/dev/null
    elif command -v ss &>/dev/null; then
        ss -ltn "sport = :$port" 2>/dev/null | grep -q ":$port"
    elif command -v netstat &>/dev/null; then
        netstat -tln 2>/dev/null | grep -q ":$port "
    else
        return 1
    fi
}

free_port() {
    local port=$1
    if command -v lsof &>/dev/null; then
        local pid
        pid=$(lsof -ti:"$port" 2>/dev/null || true)
        [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
    fi
}

cleanup() {
    echo ""
    log_info "Shutting down..."
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    # Also clean up any children
    sleep 1
    free_port "$BACKEND_PORT"
    free_port "$FRONTEND_PORT"
    log_success "Stopped cleanly. Goodbye 👋"
    exit 0
}
trap cleanup INT TERM EXIT

print_banner() {
    echo -e "${CYAN}${BOLD}"
    cat <<'EOF'
╔══════════════════════════════════════════════════════════╗
║         Website Builder — Unified Startup                ║
║         Flask backend  +  React frontend                 ║
╚══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# ─── Pre-flight checks ──────────────────────────────────────────────────────
print_banner

log_info "Running pre-flight checks..."

if ! command -v python3 &>/dev/null; then
    log_error "python3 is not installed. Install Python 3.9+ and try again."
    exit 1
fi

if ! command -v node &>/dev/null; then
    log_error "Node.js is not installed. Install Node 16+ and try again."
    exit 1
fi

if ! command -v npm &>/dev/null; then
    log_error "npm is not installed."
    exit 1
fi

# Port conflict check
for port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
    if port_in_use "$port"; then
        log_warn "Port $port is already in use."
        read -r -p "         Kill the process and continue? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            free_port "$port"
            sleep 1
            log_success "Port $port freed."
        else
            log_error "Aborting. Free port $port manually and try again."
            trap - EXIT
            exit 1
        fi
    fi
done

log_success "Python, Node, and ports look good."

# ─── Backend setup ──────────────────────────────────────────────────────────
echo ""
log_info "Setting up Flask backend..."
cd flask-backend

if [ ! -d "venv" ]; then
    log_info "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

if ! python -c "import flask" 2>/dev/null; then
    log_info "  Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r ../requirements.txt
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    log_info "  Creating .env from .env.example..."
    cp .env.example .env
fi

log_info "  Ensuring admin user exists..."
python seed_admin.py >/dev/null 2>&1 || true

log_success "Backend ready."
cd ..

# ─── Frontend setup ─────────────────────────────────────────────────────────
echo ""
log_info "Setting up React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    log_info "  Installing npm packages (first run only, may take a few minutes)..."
    npm install --silent --no-audit --no-fund
fi

log_success "Frontend ready."
cd ..

# ─── Start both services ────────────────────────────────────────────────────
echo ""
log_info "Starting services..."

# Launch backend
(
    cd flask-backend
    # shellcheck disable=SC1091
    source venv/bin/activate
    exec python run.py
) 2>&1 | sed -u "s/^/$(printf "${CYAN}${BOLD}[BACKEND] ${NC}")/" &
BACKEND_PID=$!

sleep 2

# Launch frontend
(
    cd frontend
    BROWSER=none exec npm start
) 2>&1 | sed -u "s/^/$(printf "${MAGENTA}${BOLD}[FRONTEND]${NC} ")/" &
FRONTEND_PID=$!

# Wait a moment for both to come up, then print the big banner
sleep 5

echo ""
echo -e "${GREEN}${BOLD}"
cat <<EOF
╔══════════════════════════════════════════════════════════╗
║                    🚀  READY  🚀                         ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   👉  OPEN IN YOUR BROWSER:                              ║
║                                                          ║
║       http://localhost:${FRONTEND_PORT}                             ║
║                                                          ║
║   Backend API:  http://localhost:${BACKEND_PORT}/api/health        ║
║                                                          ║
║   Admin login:  admin@websitebuilder.com / Admin@1234    ║
║                                                          ║
║   Press Ctrl+C to stop both services                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Wait — if either child dies, kill the other and exit
wait -n "$BACKEND_PID" "$FRONTEND_PID" || true
log_error "One of the services has exited. Shutting the other down..."
cleanup
