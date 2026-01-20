# Quty Karunia ERP - Desktop App

Electron-based desktop application for Windows, macOS, and Linux.

## 🖥️ Features

- Native desktop application
- Cross-platform (Windows, macOS, Linux)
- Offline mode support
- Auto-update capability
- Native notifications
- System tray integration
- Better performance than web browser
- Local data caching

## 🚀 Setup

### Prerequisites
- Node.js 18+
- Frontend app built (`cd ../frontend && npm run build`)

### Installation

```bash
# Install dependencies
npm install

# Development mode (loads from frontend dev server)
npm run dev

# Build for production
npm run build

# Build for specific platform
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
```

## 📦 Distribution

### Windows
- NSIS installer (.exe)
- Portable version

### macOS
- DMG installer
- App bundle

### Linux
- AppImage (universal)
- DEB package (Debian/Ubuntu)

## 🔧 Architecture

The desktop app wraps the React frontend using Electron:

```
desktop/
├── main.js          # Main process (Electron)
├── preload.js       # Preload script (security)
├── package.json     # Dependencies
└── assets/          # App icons
```

The app loads the frontend from:
- **Development**: http://localhost:3000 (Vite dev server)
- **Production**: ../frontend/dist/ (built files)

## 🎯 Status

**Current**: Structure created with Electron setup
**Next**: Icon design, build testing, installer configuration
