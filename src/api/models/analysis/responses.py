from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class AnalysisStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisResponse(BaseModel):
    analysis_id: str = Field(description="Unique identifier for the analysis", example="abc123")
    status: AnalysisStatus = Field(description="Current status of the analysis", example="completed")
    created_at: datetime = Field(description="When the analysis was created", example="2024-01-01T12:00:00Z")
    completed_at: datetime | None = Field(None, description="When the analysis was completed", example="2024-01-01T12:05:00Z")
    report: str | None = Field(None, description="Report file path (only present when completed)", example="/path/to/report.html")
    error: str | None = Field(None, description="Error message (only present when failed)", example="Analysis not found")
