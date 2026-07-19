from fastapi import APIRouter
from app.api.v1 import auth, dashboard, documents, simulator, simulations, subjects, twin, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(subjects.router)
api_router.include_router(documents.router)
api_router.include_router(dashboard.router)
api_router.include_router(twin.router)
api_router.include_router(simulator.router)
api_router.include_router(simulations.router)


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
