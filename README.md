# Website Builder - Full Stack Application

A **subscription-based website builder** platform built with **Python Flask** (backend) and **React** (frontend), backed by **MongoDB** and integrated with **Stripe** payments.

---

## 🏗️ Architecture

```
website-builder/
├── flask-backend/          # Python Flask REST API
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── database.py        # MongoDB connection (PyMongo)
│   │   ├── blueprints/        # Route handlers (Flask Blueprints)
│   │   │   ├── auth.py        # /api/auth/*
│   │   │   ├── websites.py    # /api/websites/*
│   │   │   ├── subscriptions.py # /api/subscriptions/*
│   │   │   ├── payments.py    # /api/payments/*
│   │   │   ├── admin.py       # /api/admin/*
│   │   │   ├── plugins.py     # /api/plugins/*
│   │   │   ├── templates.py   # /api/templates/*
│   │   │   └── users.py       # /api/users/*
│   │   ├── models/            # PyMongo data models
│   │   ├── middleware/        # JWT auth, authorization decorators
│   │   ├── services/          # Plugin manager
│   │   └── utils/             # Helper functions
│   ├── config/                # Flask configuration (dev/test/prod)
│   ├── plugins/               # Installable plugins
│   ├── tests/                 # pytest test suite
│   │   ├── conftest.py        # Shared fixtures
│   │   ├── unit/              # Model unit tests
│   │   └── integration/       # API integration tests
│   ├── run.py                 # Entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
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
- MongoDB 5.0+

### 1. Clone the repository
```bash
git clone https://github.com/Napier40/website-builder.git
cd website-builder
```

### 2. Start the Flask Backend
```bash
cd flask-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and Stripe keys

# Start the server
python run.py
```
API runs at: **http://localhost:5000**

### 3. Start the React Frontend
```bash
cd frontend
npm install
npm start
```
App runs at: **http://localhost:3000**

---

## 🔧 Configuration

Edit `flask-backend/.env`:

```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

# MongoDB
MONGO_URI=mongodb://localhost:27017/website-builder

# JWT (change this in production!)
JWT_SECRET_KEY=your-very-secure-secret-key

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Testing

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

### VS Code REST Client
Open `flask-backend/tests/api-tests.http` with the REST Client extension to run manual API tests.

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
- **bcrypt Password Hashing** (10 rounds)
- **Role-Based Access Control** (user / admin)
- **Subscription-Gated Features** (basic / premium / enterprise)
- **CORS Protection** (configurable origin whitelist)
- **Audit Logging** (every significant action is logged)
- **Content Moderation** (admin moderation queue)
- **Admin Override** (admins can correct/remove user content)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 3.1 |
| **Database** | MongoDB, PyMongo 4.x |
| **Auth** | Flask-JWT-Extended, bcrypt |
| **Payments** | Stripe Python SDK |
| **Frontend** | React 18, React Router, Axios |
| **Payments UI** | Stripe Elements |
| **Testing** | pytest, mongomock, pytest-flask |
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
   - **REST Client** (humao.rest-client)
   - **Pylance** (ms-python.vscode-pylance)
3. Select the virtual environment interpreter: `./venv/bin/python`
4. Use **F5** to launch with the debug configuration

---

## 📄 License

MIT License - see LICENSE file for details.