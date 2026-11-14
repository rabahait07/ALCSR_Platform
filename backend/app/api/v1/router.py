from fastapi import APIRouter

from app.api.v1 import auth, dashboard, syllabus

# Aggregates every v1 endpoint router; mounted at /api/v1 in app.main.
api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(syllabus.router)
api_router.include_router(dashboard.router)
