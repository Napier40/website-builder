#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Website Builder Export to VS Code ===${NC}"
echo -e "${YELLOW}This script will prepare the project for testing in Visual Studio Code.${NC}"
echo

# Create a zip file of the project
echo -e "${YELLOW}Creating project archive...${NC}"
zip -r website-builder.zip . -x "node_modules/*" "*/node_modules/*" "*/build/*" "*/dist/*" "*.git*" "*.env*"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create project archive.${NC}"
    exit 1
fi

echo -e "${GREEN}Project archive created: website-builder.zip${NC}"

# Create instructions file
echo -e "${YELLOW}Creating instructions file...${NC}"
cat > VSCODE_INSTRUCTIONS.md << EOL
# Website Builder - VS Code Testing Instructions

This document provides instructions for testing the Website Builder application in Visual Studio Code.

## Prerequisites

1. Visual Studio Code installed
2. Node.js (v14 or higher) installed
3. MongoDB installed and running locally
4. Git installed

## Setup Instructions

1. Extract the website-builder.zip file to a directory of your choice

2. Open the project in VS Code:
   - Launch VS Code
   - File > Open Folder > Select the extracted website-builder directory

3. Install dependencies:
   \`\`\`bash
   # Install root dependencies
   npm install
   
   # Install backend dependencies
   cd backend
   npm install
   
   # Install frontend dependencies
   cd ../frontend
   npm install
   \`\`\`

4. Configure environment variables:
   - In the backend directory, create a .env file with the following content:
   \`\`\`
   PORT=5000
   MONGO_URI=mongodb://localhost:27017/website-builder
   JWT_SECRET=your_jwt_secret_key_here
   STRIPE_SECRET_KEY=your_stripe_test_key_here
   \`\`\`

5. Start MongoDB:
   - Make sure your local MongoDB server is running

6. Run the application:
   - In the root directory, run:
   \`\`\`bash
   npm run dev
   \`\`\`
   - This will start both the backend and frontend servers

7. Access the application:
   - Backend API: http://localhost:5000
   - Frontend: http://localhost:3000

## Running Tests

1. Run backend tests:
   \`\`\`bash
   cd backend
   npm test
   \`\`\`

2. Run specific test suites:
   \`\`\`bash
   # Unit tests
   npm run test:unit
   
   # Integration tests
   npm run test:integration
   
   # With coverage report
   npm run test:coverage
   \`\`\`

## VS Code Extensions

For the best development experience, install these VS Code extensions:

1. ESLint
2. Prettier
3. MongoDB for VS Code
4. REST Client
5. React Developer Tools
6. Jest Runner

## Project Structure

- \`/backend\`: Node.js/Express API
- \`/frontend\`: React application
- \`/docs\`: Documentation files

## Admin Access

To access admin features, create a user and then manually update the role in MongoDB:

\`\`\`javascript
// In MongoDB shell or MongoDB Compass
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { role: "admin" } }
)
\`\`\`

## Troubleshooting

1. If you encounter CORS issues, make sure both frontend and backend servers are running
2. If MongoDB connection fails, check that MongoDB is running locally
3. For any other issues, check the console logs for error messages
EOL

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create instructions file.${NC}"
    exit 1
fi

echo -e "${GREEN}Instructions file created: VSCODE_INSTRUCTIONS.md${NC}"

# Create a VS Code workspace file
echo -e "${YELLOW}Creating VS Code workspace file...${NC}"
cat > website-builder.code-workspace << EOL
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "editor.formatOnSave": true,
    "editor.tabSize": 2,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    },
    "files.exclude": {
      "**/.git": true,
      "**/.DS_Store": true,
      "**/node_modules": true,
      "**/build": false,
      "**/coverage": true
    },
    "jest.autoRun": {
      "watch": false,
      "onSave": false
    },
    "javascript.updateImportsOnFileMove.enabled": "always",
    "terminal.integrated.env.linux": {
      "NODE_ENV": "development"
    },
    "terminal.integrated.env.osx": {
      "NODE_ENV": "development"
    },
    "terminal.integrated.env.windows": {
      "NODE_ENV": "development"
    }
  },
  "extensions": {
    "recommendations": [
      "dbaeumer.vscode-eslint",
      "esbenp.prettier-vscode",
      "mongodb.mongodb-vscode",
      "humao.rest-client",
      "christian-kohler.npm-intellisense",
      "orta.vscode-jest",
      "ms-vscode.vscode-typescript-next"
    ]
  },
  "launch": {
    "version": "0.2.0",
    "configurations": [
      {
        "type": "node",
        "request": "launch",
        "name": "Launch Backend",
        "skipFiles": [
          "<node_internals>/**"
        ],
        "program": "\${workspaceFolder}/backend/server.js",
        "envFile": "\${workspaceFolder}/backend/.env",
        "console": "integratedTerminal"
      },
      {
        "type": "node",
        "request": "launch",
        "name": "Jest Current File",
        "program": "\${workspaceFolder}/backend/node_modules/.bin/jest",
        "args": [
          "\${fileBasename}",
          "--config",
          "\${workspaceFolder}/backend/package.json"
        ],
        "console": "integratedTerminal",
        "internalConsoleOptions": "neverOpen",
        "disableOptimisticBPs": true
      }
    ],
    "compounds": [
      {
        "name": "Backend + Frontend",
        "configurations": ["Launch Backend"]
      }
    ]
  }
}
EOL

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create VS Code workspace file.${NC}"
    exit 1
fi

echo -e "${GREEN}VS Code workspace file created: website-builder.code-workspace${NC}"

echo
echo -e "${GREEN}=== Export Complete ===${NC}"
echo -e "${GREEN}You can now import the project into Visual Studio Code:${NC}"
echo -e "1. Extract website-builder.zip to your desired location"
echo -e "2. Open VS Code"
echo -e "3. File > Open Workspace from File > Select website-builder.code-workspace"
echo -e "4. Follow the instructions in VSCODE_INSTRUCTIONS.md"
echo