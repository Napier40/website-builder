# Website Builder - Flask Test Suite

## Overview
This test suite uses **pytest** and **mongomock** to test the Flask backend without requiring a real MongoDB connection. All tests run in complete isolation using an in-memory mock database.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures (app, client, users, tokens)
├── unit/
│   ├── __init__.py
│   └── test_models.py             # Unit tests: UserModel, WebsiteModel, SubscriptionModel
├── integration/
│   ├── __init__.py
│   ├── test_auth.py               # Auth API: register, login, me, profile, password
│   ├── test_websites.py           # Websites API: CRUD, pages, publish
│   └── test_admin.py              # Admin API: dashboard, users, moderation, override
└── api-tests.http                 # VS Code REST Client tests (manual)
```

## Running Tests

### Prerequisites
```bash
cd website-builder/flask-backend
pip install -r requirements.txt
```

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run a specific test file
```bash
pytest tests/unit/test_models.py
pytest tests/integration/test_auth.py
pytest tests/integration/test_websites.py
pytest tests/integration/test_admin.py
```

### Run a specific test class
```bash
pytest tests/integration/test_auth.py::TestLogin
```

### Run a specific test
```bash
pytest tests/integration/test_auth.py::TestLogin::test_login_success
```

### Run with coverage report
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Run in watch mode (auto-rerun on file change)
```bash
pip install pytest-watch
ptw
```

## Test Fixtures

All fixtures are defined in `conftest.py` and are available to all test files:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `flask_app` | session | Flask test app with mongomock |
| `client` | function | HTTP test client |
| `clean_db` | function (autouse) | Clears all DB collections before each test |
| `registered_user` | function | A pre-created regular user |
| `registered_admin` | function | A pre-created admin user |
| `user_token` | function | JWT for the regular user |
| `admin_token` | function | JWT for the admin user |
| `auth_headers` | function | `Authorization: Bearer <user_token>` |
| `admin_headers` | function | `Authorization: Bearer <admin_token>` |
| `registered_website` | function | A pre-created website for the user |

## VS Code REST Client Tests (api-tests.http)

1. Install the **REST Client** extension (humao.rest-client) in VS Code
2. Start the Flask server: `python run.py`
3. Open `tests/api-tests.http`
4. Run the **Register** and **Login** requests first to obtain tokens
5. Copy the tokens into the `@userToken` and `@adminToken` variables at the top of the file
6. Run any request by clicking **Send Request** above each block

## VS Code Debugging (launch.json)

The project includes VS Code launch configurations. To debug:
1. Open VS Code in `website-builder/flask-backend/`
2. Press `F5` or go to **Run → Start Debugging**
3. Select either **Flask: Run** or **pytest: Run All Tests**

## Coverage Targets

| Module | Target |
|--------|--------|
| Models | ≥ 90% |
| Auth Blueprint | ≥ 85% |
| Websites Blueprint | ≥ 85% |
| Admin Blueprint | ≥ 80% |
| Overall | ≥ 80% |