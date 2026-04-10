#!/bin/bash
# ============================================================
# Website Builder - Flask Backend Setup Script
# ============================================================
set -e

echo ""
echo "=============================================="
echo "  Website Builder - Flask Backend Setup"
echo "=============================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.9"

echo "📌 Checking Python version..."
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✅ Python $PYTHON_VERSION detected (3.9+ required)"
else
    echo "❌ Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed."

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "📄 Creating .env file from template..."
    cat > .env << 'EOF'
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
MONGO_URI=mongodb://localhost:27017/website-builder
JWT_SECRET_KEY=change-this-secret-key-in-production
JWT_ACCESS_TOKEN_EXPIRES=2592000
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ .env file created. Please update MONGO_URI and STRIPE_SECRET_KEY."
else
    echo "✅ .env file already exists."
fi

# Check MongoDB
echo ""
echo "🔍 Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    if mongosh --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
        echo "✅ MongoDB is running and accessible."
    else
        echo "⚠️  MongoDB is installed but not running. Start it with: sudo systemctl start mongod"
    fi
elif command -v mongo &> /dev/null; then
    echo "⚠️  MongoDB CLI found but cannot verify connection. Ensure MongoDB is running."
else
    echo "⚠️  MongoDB CLI not found. Please install MongoDB and ensure it is running."
    echo "    Install guide: https://docs.mongodb.com/manual/installation/"
fi

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "  ▶  Start the server:"
echo "     source venv/bin/activate"
echo "     python run.py"
echo ""
echo "  🧪 Run tests:"
echo "     pytest"
echo ""
echo "  📖 API docs: See docs/FLASK_API.md"
echo ""