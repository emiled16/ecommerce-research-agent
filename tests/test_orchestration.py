import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.api.services.research import run_analysis
from src.api.models.analysis.responses import AnalysisStatus
from src.exceptions import ExitProgramException


@pytest.mark.asyncio
@patch("src.api.services.research.generate_research_agent")
@patch("src.api.services.database_service.DatabaseService")
async def test_run_analysis_orchestration(mock_db_service, mock_generate_agent):
    analysis_id = "test-analysis-123"
    query = "iPhone 15 Pro"

    mock_db_service.get_analysis.return_value = {"analysis_id": analysis_id, "status": AnalysisStatus.RUNNING, "query": query}
    mock_db_service.update_analysis = Mock()

    mock_agent = Mock()
    mock_agent.run = AsyncMock(side_effect=ExitProgramException())
    mock_generate_agent.return_value = mock_agent

    result = await run_analysis(analysis_id, query, mock_db_service)

    mock_db_service.get_analysis.assert_called_once_with(analysis_id)
    mock_db_service.update_analysis.assert_called()
    mock_agent.run.assert_called_once()

    assert isinstance(result, dict)
    assert "product_name" in result or result.get("error") is None
