# ECHO Frontend

Next.js frontend for ECHO. It provides the user interface for document upload and analysis, digital twin visualization, dashboard insights, and what-if simulation.

## Stack

- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS
- Recharts
- Framer Motion

## App Routes

- /: Landing page and product entry
- /dashboard: Live dashboard overview
- /documents: Document upload, processing, and detail workflow
- /twin: Digital twin snapshot and graph-oriented views
- /simulator: Study-scenario simulation UI

Note: src/app/mentor folder exists but currently has no active page implementation.

## Key Components

- components/landing-nav.tsx: Landing navigation
- components/dashboard-sidebar.tsx: Shared sidebar and topbar shell
- components/live-dashboard.tsx: Dashboard rendering layer
- components/document-manager.tsx: Upload, list, detail, reprocess, topic management
- components/twin-view.tsx: Twin profile and knowledge display
- components/simulator-panel.tsx: Prediction form and result panel

## API Integration

All API calls are centralized in src/lib/api.ts.

Primary wrappers:

- fetchDashboard
- fetchTwin
- fetchDocuments
- fetchDocumentDetail
- uploadDocument
- reprocessDocument
- addManualTopic
- deleteDocument
- simulateScenario

Behavior notes:

- Base URL comes from NEXT_PUBLIC_API_URL.
- Upload uses XMLHttpRequest to provide progress callbacks.
- Optional bearer token can be passed through helper methods.

## Environment

Create .env.local from .env.local.example.

Required variable:

- NEXT_PUBLIC_API_URL

Default:

- http://localhost:8000/api/v1

## Local Development

1. npm install
2. copy .env.local.example .env.local
3. npm run dev

Useful scripts:

- npm run dev
- npm run build
- npm run start
- npm run lint
- npm run typecheck

## Docker

frontend/Dockerfile runs the app in development mode with npm run dev.

When started via docker-compose, frontend is exposed on port 3000 and connected to backend on port 8000.

## UX Characteristics

- Dark visual shell with motion-enhanced transitions.
- Shared dashboard shell across authenticated/product pages.
- Componentized architecture with reusable UI primitives in src/components/ui.
