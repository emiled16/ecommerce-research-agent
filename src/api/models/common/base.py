from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    error: str = Field(description="Error message", example="Analysis not found")
    error_code: str | None = Field(None, description="Error code for programmatic handling", example="ANALYSIS_NOT_FOUND")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred", example="2024-01-01T12:00:00Z")
