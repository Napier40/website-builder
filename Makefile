# Website Builder — Makefile for one-command workflows
#
# Usage:  make install    # install all dependencies (backend + frontend)
#         make start      # start both services together
#         make stop       # stop both services
#         make clean      # remove venv, node_modules, db
#         make help       # show this help

.PHONY: help install start dev stop clean test logs backend frontend

# Detect OS for shell selection
ifeq ($(OS),Windows_NT)
    START_CMD := start.bat
    SHELL := cmd.exe
else
    START_CMD := ./start.sh
endif

help: ## Show this help message
	@echo "Website Builder — Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd flask-backend && (python3 -m venv venv || python -m venv venv) && \
		. venv/bin/activate && pip install -q --upgrade pip && \
		pip install -q -r ../requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install --no-audit --no-fund
	@echo "✓ All dependencies installed."

start: ## Start both services together (backend + frontend)
	@$(START_CMD)

dev: start ## Alias for 'start'

stop: ## Stop both services (kills processes on ports 5000 and 3000)
	@node scripts/stop.js 2>/dev/null || \
	(lsof -ti:5000 | xargs -r kill -9 2>/dev/null; \
	 lsof -ti:3000 | xargs -r kill -9 2>/dev/null; \
	 echo "Stopped services on ports 5000 and 3000.")

clean: ## Remove venv, node_modules, and SQLite database
	rm -rf flask-backend/venv flask-backend/website_builder.db
	rm -rf frontend/node_modules
	rm -rf node_modules
	@echo "✓ Cleaned."

test: ## Run backend tests
	cd flask-backend && . venv/bin/activate && pytest

backend: ## Start ONLY the backend (foreground)
	cd flask-backend && . venv/bin/activate && python run.py

frontend: ## Start ONLY the frontend (foreground)
	cd frontend && BROWSER=none npm start

logs: ## Tail backend.log and frontend.log (if using start.sh with redirection)
	@tail -f backend.log frontend.log 2>/dev/null || echo "No log files found (start.sh streams to stdout by default)."
