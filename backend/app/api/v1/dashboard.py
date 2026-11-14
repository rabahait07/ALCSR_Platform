from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardMetricsResponse
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def read_dashboard_metrics(
    current_user: CurrentUser, db: DbSession
) -> DashboardMetricsResponse:
    """Progress metrics and recent activity for the logged-in user."""
    return await dashboard_service.get_dashboard_metrics(db, current_user)
