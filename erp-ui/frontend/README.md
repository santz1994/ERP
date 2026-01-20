README.md

# Quty Karunia ERP - Frontend UI

Manufacturing Execution System frontend built with React, TypeScript, and Tailwind CSS.

## Features

- 🔐 **Role-Based Access Control** - Different views for each department
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **Real-time Updates** - Live status via React Query
- 🎨 **Modern UI** - Clean, operator-friendly interface
- 📊 **Production Dashboard** - Real-time manufacturing metrics

## Prerequisites

- Node.js 16+ 
- npm or yarn

## Setup

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── api/          # API client and endpoints
├── components/   # Reusable components (Navbar, Sidebar, etc.)
├── pages/        # Page components for each module
├── store/        # Zustand state management
├── types/        # TypeScript type definitions
├── App.tsx       # Main app component
├── main.tsx      # Entry point
└── index.css     # Global styles
```

## Key Pages

- **Login** - User authentication
- **Dashboard** - Production overview and metrics
- **PPIC** - Manufacturing order management (Admin only)
- **Cutting** - Cutting department operations
- **Sewing** - Sewing department operations
- **Finishing** - Finishing department operations
- **Packing** - Packing department operations
- **Quality** - QC testing and inspections
- **Warehouse** - Inventory management
- **Admin** - System administration

## API Integration

Frontend connects to backend API at `http://localhost:8000/api/v1`

Key endpoints used:
- `POST /auth/login` - User login
- `GET /ppic/manufacturing-orders` - List manufacturing orders
- `POST /cutting/receive-spk` - Receive cutting SPK
- `POST /quality/lab-test/perform` - Perform quality test
- And more...

## Development

### Adding a New Page

1. Create new file in `src/pages/YourPage.tsx`
2. Add route in `src/App.tsx`
3. Add menu item in `src/components/Sidebar.tsx`

### Using API Client

```tsx
import { apiClient } from '@/api/client'

const data = await apiClient.getManufacturingOrder(moId)
```

### State Management

```tsx
import { useAuthStore, useUIStore } from '@/store'

const { user, logout } = useAuthStore()
const { addNotification } = useUIStore()
```

## Deployment

Build production bundle:
```bash
npm run build
```

Deploy `dist/` folder to your web server or container.

## License

Private - Quty Karunia Only
