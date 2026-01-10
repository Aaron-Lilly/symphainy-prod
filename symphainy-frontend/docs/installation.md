# Installation Guide

This document provides comprehensive instructions for setting up the Symphainy frontend development environment, including prerequisites, installation steps, and troubleshooting.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [Development Environment](#development-environment)
- [Backend Integration](#backend-integration)
- [Troubleshooting](#troubleshooting)
- [Common Issues](#common-issues)

## 🎯 Prerequisites

### System Requirements

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 8.0.0 or higher (or yarn 1.22.0+)
- **Git**: Version 2.0.0 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

### Required Software

#### Node.js Installation

**Windows:**
1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Run the installer and follow the setup wizard
3. Verify installation: `node --version` and `npm --version`

**macOS:**
```bash
# Using Homebrew
brew install node

# Or download from nodejs.org
# Verify installation
node --version
npm --version
```

**Linux (Ubuntu/Debian):**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

#### Git Installation

**Windows:**
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Run the installer with default settings
3. Verify installation: `git --version`

**macOS:**
```bash
# Using Homebrew
brew install git

# Verify installation
git --version
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL
sudo yum install git

# Verify installation
git --version
```

### Development Tools (Recommended)

- **VS Code**: [Download here](https://code.visualstudio.com/)
- **VS Code Extensions**:
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense
  - ESLint
  - Prettier
  - GitLens
  - Auto Rename Tag
  - Bracket Pair Colorizer

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd symphainy-frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env.local

# Edit the environment file with your configuration
nano .env.local
```

### 4. Start Development Server

```bash
npm run dev
```

### 5. Open in Browser

Navigate to [http://localhost:3000](http://localhost:3000)

## 📦 Detailed Installation

### Step 1: Repository Setup

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the frontend directory
cd symphainy-frontend

# Check out the main branch
git checkout main

# Verify the repository structure
ls -la
```

Expected directory structure:
```
symphainy-frontend/
├── app/                    # Next.js App Router pages
├── components/            # React components
├── shared/               # Shared utilities and components
├── lib/                  # Utility libraries
├── styles/               # Global styles
├── public/               # Static assets
├── tests/                # Test files
├── docs/                 # Documentation
├── package.json          # Dependencies and scripts
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

### Step 2: Dependencies Installation

```bash
# Install all dependencies
npm install

# Verify installation
npm list --depth=0
```

If you encounter any issues:

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

### Step 3: Environment Configuration

```bash
# Create environment file
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

Required environment variables:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=10000
NEXT_PUBLIC_API_MAX_RETRIES=3

# WebSocket Configuration
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_WS_RECONNECT_ATTEMPTS=5
NEXT_PUBLIC_WS_HEARTBEAT_INTERVAL=30000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_CROSS_PILLAR=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Step 4: Build Verification

```bash
# Run TypeScript type checking
npm run type-check

# Run linting
npm run lint

# Build the application
npm run build

# Verify build output
ls -la .next/
```

### Step 5: Development Server

```bash
# Start development server
npm run dev

# The application should be available at http://localhost:3000
```

## 🛠️ Development Environment

### VS Code Setup

1. **Install VS Code Extensions**:
   ```bash
   # Install recommended extensions
   code --install-extension ms-vscode.vscode-typescript-next
   code --install-extension bradlc.vscode-tailwindcss
   code --install-extension dbaeumer.vscode-eslint
   code --install-extension esbenp.prettier-vscode
   ```

2. **Configure VS Code Settings**:
   Create `.vscode/settings.json`:
   ```json
   {
     "typescript.preferences.importModuleSpecifier": "relative",
     "typescript.suggest.autoImports": true,
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "editor.codeActionsOnSave": {
       "source.fixAll.eslint": true
     },
     "tailwindCSS.includeLanguages": {
       "typescript": "javascript",
       "typescriptreact": "javascript"
     }
   }
   ```

3. **Configure VS Code Launch Configuration**:
   Create `.vscode/launch.json`:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Next.js: debug server-side",
         "type": "node",
         "request": "launch",
         "program": "${workspaceFolder}/node_modules/next/dist/bin/next",
         "args": ["dev"],
         "cwd": "${workspaceFolder}",
         "console": "integratedTerminal",
         "skipFiles": ["<node_internals>/**"]
       },
       {
         "name": "Next.js: debug client-side",
         "type": "chrome",
         "request": "launch",
         "url": "http://localhost:3000"
       }
     ]
   }
   ```

### Git Configuration

```bash
# Configure Git hooks
npm run prepare

# Set up pre-commit hooks
npx husky install
npx husky add .husky/pre-commit "npm run lint-staged"
```

### Development Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues
npm run type-check   # Run TypeScript type checking

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
npm run test:e2e     # Run end-to-end tests

# Code Quality
npm run format       # Format code with Prettier
npm run format:check # Check code formatting
npm run lint-staged  # Run linting on staged files
```

## 🔗 Backend Integration

### Backend Setup

1. **Clone Backend Repository**:
   ```bash
   cd ..
   git clone <backend-repository-url>
   cd symphainy-mvp
   ```

2. **Set Up Backend Environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   nano .env
   ```

3. **Start Backend Server**:
   ```bash
   # Start the backend server
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend-Backend Integration

1. **Verify API Connection**:
   ```bash
   # Test API connection
   curl http://localhost:8000/api/health
   ```

2. **Update Frontend Environment**:
   ```bash
   # Ensure frontend points to backend
   echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" >> .env.local
   echo "NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000" >> .env.local
   ```

3. **Test Integration**:
   - Start both frontend and backend servers
   - Navigate to http://localhost:3000
   - Verify that API calls work correctly

## 🔧 Troubleshooting

### Common Installation Issues

#### Node.js Version Issues

```bash
# Check Node.js version
node --version

# If version is too old, update Node.js
# Using nvm (Node Version Manager)
nvm install 18
nvm use 18

# Or download from nodejs.org
```

#### npm Installation Issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# If still having issues, try using yarn
npm install -g yarn
yarn install
```

#### TypeScript Compilation Issues

```bash
# Check TypeScript version
npx tsc --version

# Run type checking
npm run type-check

# Fix type issues
npm run type-check -- --noEmit
```

#### Build Issues

```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build

# Check for specific errors
npm run build 2>&1 | tee build.log
```

### Development Server Issues

#### Port Already in Use

```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use a different port
npm run dev -- -p 3001
```

#### Hot Reload Not Working

```bash
# Check file watching limits (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Restart development server
npm run dev
```

#### Environment Variables Not Loading

```bash
# Verify environment file exists
ls -la .env.local

# Check environment variables
npm run dev -- --env-file=.env.local

# Restart development server
npm run dev
```

### Testing Issues

#### Jest Configuration Issues

```bash
# Clear Jest cache
npm run test -- --clearCache

# Run tests with verbose output
npm run test -- --verbose

# Run specific test file
npm run test -- --testPathPattern=MyComponent.test.tsx
```

#### Playwright Issues

```bash
# Install Playwright browsers
npx playwright install

# Run Playwright tests
npm run test:e2e

# Run with UI
npm run test:e2e -- --ui
```

## 🚨 Common Issues

### Issue 1: Module Resolution Errors

**Symptoms**: `Module not found` errors

**Solution**:
```bash
# Check TypeScript paths configuration
cat tsconfig.json | grep paths

# Verify file structure
ls -la components/
ls -la shared/

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Issue 2: Tailwind CSS Not Working

**Symptoms**: Styles not applying

**Solution**:
```bash
# Check Tailwind configuration
cat tailwind.config.js

# Verify CSS imports
cat styles/globals.css

# Rebuild CSS
npm run build
```

### Issue 3: WebSocket Connection Issues

**Symptoms**: WebSocket connection failures

**Solution**:
```bash
# Check WebSocket URL configuration
echo $NEXT_PUBLIC_WS_BASE_URL

# Verify backend WebSocket endpoint
curl -I http://localhost:8000/ws

# Check browser console for errors
```

### Issue 4: API Request Failures

**Symptoms**: API calls returning errors

**Solution**:
```bash
# Check API base URL
echo $NEXT_PUBLIC_API_BASE_URL

# Test API endpoint directly
curl http://localhost:8000/api/health

# Check CORS configuration in backend
```

### Issue 5: Build Performance Issues

**Symptoms**: Slow builds or memory errors

**Solution**:
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"

# Use production build
npm run build

# Check bundle size
npm run analyze
```

## 📞 Getting Help

### Documentation Resources

- [API Documentation](./API.md) - Service layer interfaces
- [Component Library](./components.md) - Component documentation
- [Configuration Guide](./configuration.md) - Environment setup
- [Troubleshooting Guide](./troubleshooting.md) - Common issues

### Support Channels

1. **Check existing issues** in the repository
2. **Create a new issue** with detailed description
3. **Include environment details**:
   - Operating system
   - Node.js version
   - npm version
   - Error messages
   - Steps to reproduce

### Debugging Tips

```bash
# Enable debug logging
DEBUG=* npm run dev

# Check for TypeScript errors
npm run type-check

# Run linting with detailed output
npm run lint -- --debug

# Check bundle analysis
npm run analyze
```

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 