import pytest
from pydantic import ValidationError
from datetime import datetime

from src.api.models.analysis.requests import AnalysisRequest
from src.api.models.analysis.responses import AnalysisResponse, AnalysisStatus


def test_analysis_request_validation_success():
    request_data = {"query": "iPhone 15 Pro"}

    request = AnalysisRequest(**request_data)

    assert request.query == "iPhone 15 Pro"


def test_analysis_request_validation_failure():
    request_data = {}

    with pytest.raises(ValidationError) as exc_info:
        AnalysisRequest(**request_data)

    assert "query" in str(exc_info.value)


def test_analysis_response_validation():
    response_data = {
        "analysis_id": "test-123",
        "status": AnalysisStatus.RUNNING,
        "created_at": datetime.now(),
        "completed_at": None,
        "report": None,
        "error": None,
    }

    response = AnalysisResponse(**response_data)

    assert response.analysis_id == "test-123"
    assert response.status == AnalysisStatus.RUNNING
