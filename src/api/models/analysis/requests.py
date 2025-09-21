from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    query: str = Field(description="Product name or market to analyze", example="iPhone 15 Pro")
