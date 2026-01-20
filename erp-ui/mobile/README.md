# Quty Karunia ERP - Mobile App

React Native mobile application for iOS and Android.

## 📱 Features

- Native iOS and Android support
- Barcode/QR code scanning for inventory
- Offline mode with local storage
- Push notifications
- Camera integration for QC inspections
- Optimized for production floor operators

## 🚀 Setup

### Prerequisites
- Node.js 18+
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)

### Installation

```bash
# Install dependencies
npm install

# iOS setup (Mac only)
cd ios && pod install && cd ..

# Run on Android
npm run android

# Run on iOS
npm run ios
```

## 📂 Structure

```
mobile/
├── src/
│   ├── screens/        # App screens
│   ├── components/     # Reusable components
│   ├── navigation/     # Navigation setup
│   ├── api/           # API client
│   ├── store/         # State management
│   ├── utils/         # Utilities
│   └── types/         # TypeScript types
├── android/           # Android native code
├── ios/              # iOS native code
└── package.json      # Dependencies
```

## 🎯 Planned Screens

- Login
- Dashboard
- QC Scanner
- Inventory Scanner
- Work Order List
- Kanban Board
- Notifications

## 🔧 Status

**Current**: Structure created, awaiting implementation
**Next**: Screen development and API integration
