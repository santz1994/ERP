# 🎨 Quty Karunia ERP - User Interfaces

This folder contains all user interface applications for the Quty Karunia ERP system across different platforms.

## 📂 Structure

```
erp-ui/
├── frontend/        # Web Application (React + TypeScript)
├── mobile/          # Mobile App (React Native - iOS/Android)
└── desktop/         # Desktop App (Electron - Windows/Mac/Linux)
```

---

## 🌐 Frontend (Web Application)

**Technology**: React 18 + TypeScript + Vite  
**Status**: ✅ **100% Complete - Production Ready**

### Features
- 15 production pages
- Responsive design (Tailwind CSS)
- Real-time updates (React Query + WebSocket)
- State management (Zustand)
- 11 department modules
- Admin tools (Users, Masterdata, Import/Export)

### Quick Start
```bash
cd frontend
npm install
npm run dev
# Access: http://localhost:3000
```

### Production Build
```bash
cd frontend
npm run build
npm run preview
```

**Deployment**: Docker container (port 3000)

---

## 📱 Mobile (iOS & Android)

**Technology**: React Native 0.73  
**Status**: 🚧 **Structure Created - Awaiting Implementation**

### Planned Features
- Native iOS and Android apps
- Barcode/QR code scanning
- Offline mode with local storage
- Push notifications
- Camera for QC inspections
- Optimized for production floor

### Target Users
- Production operators
- QC inspectors
- Warehouse staff
- Mobile supervisors

### Quick Start
```bash
cd mobile
npm install
npm run android  # For Android
npm run ios      # For iOS (Mac only)
```

**Next Steps**: Screen development, API integration, native features

---

## 🖥️ Desktop (Cross-Platform)

**Technology**: Electron 28 + Frontend Web App  
**Status**: 🚧 **Structure Created - Ready for Build**

### Features
- Native Windows/macOS/Linux app
- Wraps the frontend React app
- Offline mode support
- Auto-update capability
- System tray integration
- Better performance than browser

### Target Users
- Office staff
- Managers
- Admin users
- Users preferring native apps

### Quick Start
```bash
# Development mode
cd desktop
npm install
npm run dev  # Loads from frontend dev server

# Production build
npm run build:win    # Windows installer
npm run build:mac    # macOS DMG
npm run build:linux  # Linux AppImage/DEB
```

**Distribution**: Installers for each platform

---

## 🎯 Development Priorities

### Phase 13: Mobile App (React Native)
**Priority**: HIGH  
**Timeline**: 2-3 weeks  
**Why**: Production floor operators need mobile access for scanning and QC

**Key Screens**:
1. Login
2. Dashboard
3. QC Scanner (barcode/QR)
4. Work Order List
5. Kanban Board
6. Inventory Scanner
7. Notifications

### Phase 14: Desktop App (Electron)
**Priority**: MEDIUM  
**Timeline**: 1 week  
**Why**: Office users prefer native desktop apps

**Tasks**:
1. Design app icons
2. Test builds on Windows/Mac/Linux
3. Configure auto-updater
4. Create installers

---

## 🔗 API Integration

All UI applications connect to the same backend:

**Backend API**: http://localhost:8000  
**Endpoints**: 104 REST APIs  
**Authentication**: JWT tokens  
**WebSocket**: ws://localhost:8000/ws

### Shared API Client
- Frontend: `src/api/client.ts` (Axios)
- Mobile: `src/api/client.ts` (Axios)
- Desktop: Uses frontend's API client

---

## 📊 Comparison

| Feature | Web (Frontend) | Mobile | Desktop |
|---------|---------------|--------|---------|
| Platform | Browser | iOS/Android | Win/Mac/Linux |
| Status | ✅ Complete | 🚧 Planned | 🚧 Ready |
| Offline | Limited | ✅ Yes | ✅ Yes |
| Camera | ❌ No | ✅ Yes | ❌ No |
| Scanning | ❌ No | ✅ Yes | ❌ No |
| Performance | Good | Excellent | Excellent |
| Updates | Auto | Store approval | Auto-update |
| Installation | None | Store download | Installer |

---

## 🚀 Getting Started

### For Web Development
```bash
cd frontend
npm install
npm run dev
```

### For Mobile Development
```bash
cd mobile
npm install
# iOS
npm run ios
# Android
npm run android
```

### For Desktop Development
```bash
cd desktop
npm install
npm run dev
```

---

## 📝 Notes

1. **Frontend** is the main application - fully functional
2. **Mobile** structure is created but needs implementation
3. **Desktop** wraps the frontend and is ready to build
4. All apps share the same backend API
5. Mobile app is priority for production floor users

---

**Last Updated**: January 20, 2026  
**Session**: Session 10 - Structure Reorganization
