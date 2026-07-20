# ECHO Backend

FastAPI backend for ECHO. This service owns authentication, document ingestion and analysis, digital twin materialization, dashboard aggregation, and simulation persistence.

## Feature Overview

- JWT authentication with Argon2 password hashing
- Subject and document management for student academic data
- Document upload, extraction, and structured analysis pipeline
- Digital twin updates driven by analysis results and manual topic additions
- Dashboard and twin aggregation endpoints for frontend consumption
- Immediate simulation endpoints for what-if academic scenarios

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Pydantic
- JWT auth with Argon2 password hashing

## Folder Map

- app/main.py: FastAPI app startup, CORS, router mounting
- app/api: Route handlers and request dependencies
- app/core: Settings and security helpers
- app/db: Engine/session setup and demo seed
- app/models: SQLAlchemy models for digital twin domain
- app/schemas: Pydantic request and response contracts
- app/services: Document pipeline, analysis, timeline, prediction, dashboard/twin aggregation

## Runtime Behavior

1. Service boots with app lifespan hook.
2. Tables are created automatically in development.
3. Demo data is seeded for local usage.
4. API is exposed under /api/v1.

Note: Auto-create and seeding are development conveniences. Production should use migration tooling.

## Authentication Model

- Register and login endpoints issue JWT bearer tokens.
- Passwords are hashed with Argon2.
- When no bearer token is provided, dependency layer falls back to a demo user for local/demo mode.

## API Endpoints

### Health

- GET /api/v1/health: Basic service health check.

### Auth

- POST /api/v1/auth/register: Create user and return access token.
- POST /api/v1/auth/login: Validate credentials and return access token.

### User

- GET /api/v1/users/me: Return current user profile.

### Subjects

- GET /api/v1/subjects: List subjects for current user.
- POST /api/v1/subjects: Create a subject.

### Documents

- GET /api/v1/documents: List user documents with processing status.
- GET /api/v1/documents/{document_id}: Get full detail, extracted text, and analysis payload.
- POST /api/v1/documents: Register metadata-only document row.
- POST /api/v1/documents/upload: Upload file, extract text, run analysis, update twin.
- POST /api/v1/documents/{document_id}/reprocess: Re-run extraction/analysis for stored file.
- POST /api/v1/documents/{document_id}/topics: Add manual topic and rematerialize twin data.
- DELETE /api/v1/documents/{document_id}: Delete document and stored file.

### Dashboards and Twin

- GET /api/v1/dashboard: Aggregated student dashboard snapshot.
- GET /api/v1/twin: Digital twin snapshot.

### Simulation

- POST /api/v1/simulate: Run immediate what-if scenario prediction and persist it.
- POST /api/v1/simulations: Persist a simulation request and generated prediction.

## Document Pipeline

Upload processing path:

1. Validate extension and save binary into backend/uploads/{user_id}.
2. Extract text and page metadata from file.
3. Produce structured analysis payload.
4. Upsert subject signals and twin entities.
5. Save analysis in document insight row.
6. Return parsed response for frontend rendering.

Supported document extensions:

- .pdf
- .docx
- .txt
- .png
- .jpg
- .jpeg

## Configuration

Primary settings are loaded from .env.

- APP_NAME
- ENVIRONMENT
- DATABASE_URL
- SECRET_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES
- CORS_ORIGINS

See .env.example for defaults.

Optional LLM environment variables used by analysis service:

- OPENAI_API_KEY
- OPENAI_MODEL

## Local Development

1. python -m venv .venv
2. .venv\Scripts\activate
3. pip install -e .[dev]
4. copy .env.example .env
5. uvicorn app.main:app --reload

OpenAPI docs:

- http://localhost:8000/docs

## Docker

Service image is defined in backend/Dockerfile and run through docker-compose from repo root.

## Current Limitations

- No Alembic migration workflow yet.
- Demo-user fallback is enabled by default for local UX.
- SQLite is default development datastore; production deployment should use managed database and hardened secrets.

## How Copilot and Codex Were Used

- Copilot helped draft the API documentation structure, endpoint summaries, and deployment notes.
- Codex-style assistance helped trace the backend startup path, CORS behavior, and Render deployment settings.
- The resulting documentation was checked against the actual FastAPI app in app/main.py and the settings in app/core/config.py.
