# ECHO

ECHO is an academic intelligence platform that turns student documents into a living digital twin, then uses that twin for dashboards and study outcome simulation.

## Feature Overview

- Document ingestion for syllabus and study files in PDF, DOCX, TXT, PNG, JPG, and JPEG formats
- Text extraction and structured academic analysis for topics, modules, concepts, assignments, and exam dates
- Digital twin materialization at the user and subject level
- Dashboard and twin snapshots for progress, confidence, and study signals
- What-if simulation for study habits, attendance, sleep, and revision patterns
- Modern Next.js frontend for document management, dashboard, twin view, and simulation

## What This Project Does

- Ingests uploaded syllabus and study documents (PDF, DOCX, TXT, PNG, JPG, JPEG)
- Extracts text and builds structured academic insights (topics, modules, concepts, deadlines)
- Updates a user-level digital twin in the database
- Exposes dashboard and twin snapshots through API endpoints
- Runs what-if simulation for study habits and attendance
- Provides a modern Next.js frontend for document management, dashboard, twin view, and simulator

## Monorepo Structure

- [backend](backend): FastAPI application, digital twin models, document pipeline, prediction logic
- [frontend](frontend): Next.js 15 application and product UI
- [docker-compose.yml](docker-compose.yml): Local two-service orchestration

## Architecture Summary

Backend flow:

1. Client uploads a document to the backend.
2. Backend extracts text via the extraction pipeline.
3. Structured analysis is generated from extracted text.
4. Subject/topic/task signals are materialized into digital twin entities.
5. Dashboard and twin endpoints aggregate these signals for the frontend.

Frontend flow:

1. User navigates pages for Documents, Dashboard, Twin, and Simulator.
2. UI calls API wrappers from [frontend/src/lib/api.ts](frontend/src/lib/api.ts).
3. Responses are rendered in feature components.

## Quick Start

### Option A: Docker Compose

1. Run docker compose up --build from the repo root.
2. Open http://localhost:3000 for frontend.
3. Backend API is on http://localhost:8000 and docs on http://localhost:8000/docs.

### Option B: Local Development

Backend (Python 3.12+):

1. cd backend
2. python -m venv .venv
3. .venv\Scripts\activate
4. pip install -e .[dev]
5. copy .env.example .env
6. uvicorn app.main:app --reload

Frontend (Node 20+):

1. cd frontend
2. npm install
3. copy .env.local.example .env.local
4. npm run dev

## Deploying to a Live Server

### Frontend on Vercel

1. Create a new Vercel project and import this repository.
2. Set the project root to the repository root so the provided Vercel config can build the frontend from the [frontend](frontend) folder.
3. Add this environment variable in Vercel:
   - NEXT_PUBLIC_API_URL=https://your-backend-url/api/v1
4. Deploy.

### Frontend on Netlify

1. Create a new site from this repository.
2. Set the build command to: `cd frontend && npm install && npm run build`
3. Set the publish directory to: `frontend/.next`
4. Add the same environment variable:
   - NEXT_PUBLIC_API_URL=https://your-backend-url/api/v1
5. Deploy.

### Backend on Render, Railway, Fly.io, or similar

1. Create a web service from the [backend](backend) folder.
2. Use Python 3.12.
3. Set the build command to: `pip install .`
4. Set the start command to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add these environment variables:
   - SECRET_KEY=change-this-to-a-long-random-value
   - CORS_ORIGINS=https://your-frontend-domain.com
   - DATABASE_URL=sqlite:///./echo.db
6. Deploy.

> SQLite is fine for demos and small deployments, but a managed Postgres database is the better long-term choice for production.

## API Snapshot

Base URL: /api/v1

- GET /health
- POST /auth/register
- POST /auth/login
- GET /users/me
- GET, POST /subjects
- GET, POST /documents
- POST /documents/upload
- GET /documents/{document_id}
- POST /documents/{document_id}/reprocess
- POST /documents/{document_id}/topics
- DELETE /documents/{document_id}
- GET /dashboard
- GET /twin
- POST /simulate
- POST /simulations

## Important Behavior Notes

- On startup, backend currently creates tables automatically and seeds demo data for development.
- If no bearer token is sent, backend falls back to a demo user account for easier local testing.
- The frontend currently uses public API URL configuration and can operate in demo mode with token-less calls.

## Environment Variables

- Backend env example: [backend/.env.example](backend/.env.example)
- Frontend env example: [frontend/.env.local.example](frontend/.env.local.example)
- Optional OpenAI integration keys are used by document analysis service when provided.

## Detailed Service Documentation

- Backend details: [backend/README.md](backend/README.md)
- Frontend details: [frontend/README.md](frontend/README.md)

## How Copilot and Codex Were Used

- GitHub Copilot was used to draft and refine repository documentation, deployment instructions, and environment variable guidance.
- Codex-style assistance was used to inspect the backend/frontend wiring, identify deployment issues, and suggest exact config values for Vercel and Render.
- Both were used as implementation aids, while the actual code and configuration changes were verified against the workspace files and build output.
