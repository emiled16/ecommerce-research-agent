from pydantic import BaseModel, Field, model_validator
from datetime import datetime


class HealthResponse(BaseModel):
    status: str | None = Field(description="Overall system health status", example="healthy", default=None)
    timestamp: datetime = Field(description="When the health check was performed", example="2024-01-01T12:00:00Z")
    version: str = Field(default="0.1.0", description="API version", example="0.1.0")
    services: dict[str, str] = Field(
        default_factory=dict, description="Status of individual services", example={"agent": "healthy", "database": "healthy"}
    )

    @model_validator(mode="after")
    def check_status(self):
        if all(service == "healthy" for service in self.services.values()):
            self.status = "healthy"
        else:
            self.status = "degraded"
        return self
