from sqlalchemy import Column, String, Text, DateTime
from src.database.models.base import BaseModel


class AnalysisHistory(BaseModel):
    __tablename__ = "analysis_history"

    id = Column(String, primary_key=True)
    query = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    report_path = Column(String)
    error = Column(Text)

    def __repr__(self):
        return f"<AnalysisHistory(id='{self.id}', query='{self.query}', status='{self.status}')>"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_running(self) -> bool:
        return self.status in ["pending", "running"]
