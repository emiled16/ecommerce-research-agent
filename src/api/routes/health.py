from fastapi import APIRouter
from datetime import datetime

from src.api.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    services_status = {"agent": "healthy", "api": "healthy"}

    return HealthResponse(timestamp=datetime.now(), version="0.1.0", services=services_status)
