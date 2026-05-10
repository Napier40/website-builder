# Website Builder - Full Stack Application

A **subscription-based website builder** platform built with **Python Flask** (backend) and **React** (frontend), backed by **SQLite** (zero-config, built into Python) and integrated with **Stripe** payments.

---

## 🏗️ Architecture

```
website-builder/
├── flask-backend/          # Python Flask REST API
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── database.py        # SQLAlchemy db instance + init_db()
│   │   ├── blueprints/        # Route handlers (Flask Blueprints)
│   │   │   ├── auth.py        # /api/auth/*
│   │   │   ├── websites.py    # /api/websites/*
│   │   │   ├── subscriptions.py # /api/subscriptions/*
│   │   │   ├── payments.py    # /api/payments/*
│   │   │   ├── admin.py       # /api/admin/*
│   │   │   ├── plugins.py     # /api/plugins/*
│   │   │   ├── templates.py   # /api/templates/*
│   │   │   └── users.py       # /api/users/*
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── middleware/        # JWT auth, authorization decorators
│   │   ├── services/          # Plugin manager
│   │   └── utils/             # Helper functions
│   ├── config/                # Flask configuration (dev/test/prod)
│   ├── plugins/               # Installable plugins
│   ├── tests/                 # pytest test suite
│   │   ├── conftest.py        # Shared fixtures (in-memory SQLite)
│   │   ├── unit/              # Model unit tests
│   │   └── integration/       # API integration tests
│   ├── run.py                 # Entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variable template
│
├── frontend/               # React Application
│   ├── src/
│   │   ├── App.js             # Root with routing & Stripe
│   │   ├── context/           # Auth context
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Route page components
│   │   └── App.css            # Global styles
│   └── package.json
│
├── docs/                   # Documentation
│   ├── FLASK_API.md           # Full API reference
│   ├── ADMIN_GUIDE.md         # Administrator guide
│   └── PROJECT_SUMMARY.md     # Project overview
│
└── README.md               # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- **No database installation needed** — SQLite is built into Python

### 1. Clone the repository
```bash
git clone https://github.com/Napier40/website-builder.git
cd website-builder
```

### 2. ⚡ One-command startup

This project is designed so **one command launches both services** (backend + frontend) together. Pick whichever flavour you prefer — they all do exactly the same thing:

| Method | Command | Works on |
|--------|---------|----------|
| **npm** (recommended) | `npm run install:all && npm start` | Any OS with Node |
| **Shell script** | `./start.sh` | macOS / Linux |
| **Batch file** | `start.bat` | Windows |
| **Make** | `make install && make start` | macOS / Linux (with make) |

All four methods:
- ✅ Auto-create the Python virtualenv on first run
- ✅ Auto-install backend (pip) and frontend (npm) dependencies
- ✅ Detect port conflicts on 5000/3000 and offer to free them
- ✅ Stream both services' logs with colour-coded prefixes (`[BACKEND]` in cyan, `[FRONTEND]` in magenta)
- ✅ Gracefully shut **both** services down with `Ctrl+C`
- ✅ If either service crashes, the other is stopped automatically

When you see the `🚀  READY  🚀` banner, open **http://localhost:3000** in your browser.

> ⚠️ **Important:** The user interface lives at **http://localhost:3000** (React).
> The API backend at **http://localhost:5000** is the data layer — visiting it in a browser now shows a friendly landing page with a link to the app.

---

### Stopping the services

- From the terminal running `npm start` / `start.sh` → press **Ctrl+C**
- From any terminal → `npm run stop` (or `make stop`) — kills anything on ports 5000/3000

---

### Manual startup (alternative — two terminals)

If you prefer to run each service in its own terminal:

#### Start the Flask Backend
```bash
cd flask-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — only STRIPE keys are required; SQLite needs no config

# Start the server
python run.py
```
API runs at: **http://localhost:5000**

The SQLite database file (`website_builder.db`) is created automatically in `flask-backend/` on first run. Subscription plans and default templates are seeded automatically.

#### Start the React Frontend (in a second terminal)
```bash
cd frontend
npm install
npm start
```
👉 **App runs at: http://localhost:3000** ← open this in your browser

---

## ⚠️ Troubleshooting

### "I see raw JSON like `{\"success\": true, \"message\": \"Website Builder API\"...}`"

**This is not an error** — you've hit the backend API directly. The backend only serves JSON; the user interface is served by the React frontend on a different port.

**Fix:** Open **http://localhost:3000** instead of http://localhost:5000.

Make sure the React frontend is running:
```bash
cd frontend && npm start
```

### "Connection refused" on http://localhost:3000

The React frontend isn't running. Start it with `npm start` from the `frontend/` directory, or use `./start.sh` to start everything at once.

### "Connection refused" on http://localhost:5000

The Flask backend isn't running. Start it with `python run.py` from `flask-backend/` (with venv activated), or use `./start.sh`.

### Admin login
Default admin credentials (change in production):
- Email: `admin@websitebuilder.com`
- Password: `Admin@1234`

This account is created automatically by `start.bat`/`start.sh`/`start.ps1`.
If you're starting Flask manually, run `python seed_admin.py` (from
`flask-backend/`) once to create it. Override with env vars if needed:

```bash
ADMIN_EMAIL=you@example.com ADMIN_PASSWORD=YourSecret python seed_admin.py
```

---

## 🔧 Configuration

Copy `.env.example` to `.env` in `flask-backend/`:

```env
FLASK_ENV=development
SECRET_KEY=change-me-in-production
JWT_SECRET_KEY=change-me-in-production

# SQLite database path (optional — defaults to flask-backend/website_builder.db)
# DATABASE_URL=sqlite:///website_builder.db

# Stripe (required for payment features)
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS
FRONTEND_URL=http://localhost:3000
```

> **No `MONGO_URI` needed.** SQLite requires zero installation — the database file is created automatically.

---

## 🧪 Testing

Tests use an **in-memory SQLite database** — no external services required.

### Run all tests
```bash
cd flask-backend
pytest
```

### Run specific test suites
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -v --tb=short         # Verbose with short tracebacks
```

### Coverage report
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

---

## 📋 API Overview

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/api/health` | GET | Public | Health check |
| `/api/auth/register` | POST | Public | Register user |
| `/api/auth/login` | POST | Public | Login |
| `/api/auth/me` | GET | User | Current user |
| `/api/websites` | GET/POST | User | List / Create websites |
| `/api/websites/:id` | GET/PUT/DELETE | User | CRUD single website |
| `/api/websites/:id/publish` | PUT | User | Publish website |
| `/api/subscriptions` | GET | Public | List plans |
| `/api/subscriptions/subscribe` | POST | User | Subscribe |
| `/api/payments/intent` | POST | User | Create payment |
| `/api/templates` | GET | Public | List templates |
| `/api/admin/dashboard` | GET | Admin | Stats |
| `/api/admin/users` | GET/PUT/DELETE | Admin | Manage users |
| `/api/admin/moderation` | GET/POST/PUT | Admin | Content moderation |
| `/api/admin/websites/:id/override` | PUT | Admin | Override content |
| `/api/admin/audit-logs` | GET | Admin | Audit trail |

See [docs/FLASK_API.md](docs/FLASK_API.md) for full documentation.

---

## 🔐 Security Features

- **JWT Authentication** (Flask-JWT-Extended, 30-day expiry)
- **bcrypt Password Hashing** (12 rounds)
- **Role-Based Access Control** (user / admin)
- **Subscription-Gated Features** (free / basic / premium / enterprise)
- **CORS Protection** (configurable origin whitelist)
- **Audit Logging** (every significant action is logged)
- **Content Moderation** (admin moderation queue)
- **Admin Override** (admins can correct/remove user content)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 3.1 |
| **Database** | SQLite (built-in), SQLAlchemy 2.0, Flask-SQLAlchemy 3.1 |
| **Auth** | Flask-JWT-Extended, bcrypt |
| **Payments** | Stripe Python SDK |
| **Frontend** | React 18, React Router, Axios |
| **Payments UI** | Stripe Elements |
| **Testing** | pytest, pytest-flask (in-memory SQLite) |
| **Production** | Gunicorn WSGI server |

---

## 👤 User Roles

| Role | Capabilities |
|------|-------------|
| **Guest** | View plans, templates, landing page |
| **User** | Create websites, manage pages, subscribe |
| **Admin** | Everything + moderate content, override pages, view audit logs |

---

## 🌐 Subscription Plans

| Plan | Price | Websites | Custom Domain |
|------|-------|----------|---------------|
| Free | $0 | 1 | No |
| Basic | $9.99/mo | 3 | No |
| Premium | $29.99/mo | 10 | Yes |
| Enterprise | $99.99/mo | Unlimited | Yes |

---

## 📁 VS Code Setup

1. Open `flask-backend/` as the workspace root in VS Code
2. Install recommended extensions:
   - **Python** (ms-python.python)
   - **Pylance** (ms-python.vscode-pylance)
3. Select the virtual environment interpreter: `./venv/bin/python`
4. Create `.env` from `.env.example`
5. Run `python run.py` — the SQLite database is created automatically

---

## 📄 License

MIT License - see LICENSE file for details.
## 🆕 Updated VS Code Setup

This project includes pre-configured VS Code settings for optimal development experience in the `.vscode/` directory.

### Opening in VS Code

Open the **root** `website-builder/` directory (not just `flask-backend/`) as the workspace in VS Code to enable full-stack debugging.

### Recommended Extensions

- **Python** (ms-python.python) — Python language support
- **Pylance** (ms-python.vscode-pylance) — Fast Python IntelliSense
- **ESLint** (dbaeumer.vscode-eslint) — JavaScript/React linting

### Available Tasks (Ctrl+Shift+P -> "Tasks: Run Task")

- `Flask: Install Dependencies` — Install Python packages
- `Flask: Seed Database` — Seed starter templates
- `Flask: Seed Translations` — Seed English translations
- `Flask: Run Tests` — Run pytest test suite
- `Flask: Start Backend Server` — Start Flask on port 5000
- `React: Install Dependencies` — Install npm packages
- `React: Start Dev Server` — Start React on port 3000
- `Full Stack: Start Both Servers` — Start both in parallel
- `Development: Seed and Start` — Seed tables and start both servers

### Debug Configurations (F5)

- `Flask: Debug Backend` — Debug Flask with breakpoints
- `Flask: Run Backend (no debug)` — Run Flask normally

### Pre-configured Settings

- Python interpreter: `flask-backend/venv/bin/python` (auto-selected)
- Test framework: pytest, runs `flask-backend/tests/`
- ESLint: enabled for frontend, auto-fix on save
- Excluded files: node_modules, venv, __pycache__, build, dist, website_builder.db

### First-time Setup

If this is your first time running the application:

1. Run task: **Development: Seed and Start**
2. Or manually from terminal:
   ```bash
   cd flask-backend
   python seed_templates.py
   python seed_translations.py
   python run.py  # In separate terminal: cd frontend && npm start
   ```
