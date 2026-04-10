#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Website Builder Setup ===${NC}"
echo -e "${YELLOW}This script will set up the Website Builder application.${NC}"
echo

# Check if Node.js is installed
echo -e "${YELLOW}Checking if Node.js is installed...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js (v14 or higher) and try again.${NC}"
    exit 1
fi

NODE_VERSION=$(node -v)
echo -e "${GREEN}Node.js is installed: $NODE_VERSION${NC}"

# Check if npm is installed
echo -e "${YELLOW}Checking if npm is installed...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm and try again.${NC}"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo -e "${GREEN}npm is installed: $NPM_VERSION${NC}"

# Install root dependencies
echo -e "${YELLOW}Installing root dependencies...${NC}"
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install root dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Root dependencies installed successfully.${NC}"

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd backend
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install backend dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Backend dependencies installed successfully.${NC}"

# Create .env file for backend if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file for backend...${NC}"
    cat > .env << EOL
PORT=5000
MONGO_URI=mongodb://localhost:27017/website-builder
JWT_SECRET=your_jwt_secret_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here
EOL
    echo -e "${GREEN}.env file created. Please update it with your actual values.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping creation.${NC}"
fi

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install frontend dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Frontend dependencies installed successfully.${NC}"

# Return to root directory
cd ..

echo
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo -e "${GREEN}You can now start the application with:${NC}"
echo -e "${YELLOW}npm run dev${NC}"
echo
echo -e "${YELLOW}Note: Make sure to update the .env file in the backend directory with your actual values.${NC}"