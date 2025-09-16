# BudConnect Admin Panel

A modern React-based administration interface for managing BudConnect resources including models, providers, licenses, and engines.

## Features

- **Dashboard**: Overview of system status and statistics
- **License Management**: Full CRUD operations for licenses with suitability ratings
- **Model Management**: View and manage AI models compatible with LiteLLM and TensorZero
- **Provider Management**: Manage model providers and their configurations (Coming Soon)
- **Engine Management**: View and configure engine compatibility (Coming Soon)

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **TanStack Query** for server state management
- **React Router v6** for navigation
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- npm or yarn
- BudConnect backend running on port 8000

### Installation

1. Navigate to the admin directory:
```bash
cd admin
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The admin panel will be available at http://localhost:3000

### Backend Connection

The admin panel is configured to proxy API requests to the backend running on http://localhost:8000. Make sure your BudConnect backend is running before starting the admin panel.

To start the backend:
```bash
# From the root directory
./deploy/start_dev.sh
```

## Project Structure

```
admin/
├── src/
│   ├── api/           # API client and service modules
│   ├── components/    # Reusable UI components
│   │   ├── ui/       # Base UI components (Button, Card, etc.)
│   │   └── layout/   # Layout components
│   ├── lib/          # Utilities and helpers
│   ├── pages/        # Page components
│   │   ├── dashboard/
│   │   ├── licenses/
│   │   └── models/
│   └── types/        # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The admin panel communicates with the BudConnect backend API through a configured proxy. All API calls to `/api/*` are forwarded to the backend server.

### API Endpoints Used

- `/api/licenses` - License management
- `/api/model/get-compatible-models` - Model compatibility
- `/api/engine/get-compatible-engines` - Engine compatibility
- `/api/engine/get-latest-engine-version` - Engine version info

## Features Implementation Status

- ✅ Dashboard with system overview
- ✅ License CRUD operations
- ✅ Model listing and filtering
- ⏳ Provider management (In Progress)
- ⏳ Engine compatibility viewer (In Progress)
- ⏳ Settings page (Planned)

## Development

### Adding New Pages

1. Create a new directory under `src/pages/`
2. Add the page component
3. Register the route in `src/App.tsx`
4. Add navigation link in `src/components/layout/main-layout.tsx`

### Adding API Services

1. Create a new service file in `src/api/`
2. Define the API methods
3. Export from `src/api/index.ts`

### Styling

The project uses Tailwind CSS with custom theme configuration. Design tokens are defined in `src/index.css` using CSS variables for easy theming.

## Contributing

Please ensure all TypeScript types are properly defined and follow the existing code structure when adding new features.

## License

Copyright (c) 2024 Bud Ecosystem Inc. Licensed under the Apache License, Version 2.0.
