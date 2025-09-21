from loguru import logger
from src.api.models.analysis.responses import AnalysisStatus
from src.api.services.database_service import DatabaseService
from src.llm.agent import generate_research_agent, ResearchContext
from src.exceptions import ExitProgramException


async def run_analysis(analysis_id: str, query: str, db_service: DatabaseService) -> dict:
    data = db_service.get_analysis(analysis_id)
    if not data:
        logger.error(f"Analysis {analysis_id} not found in database")
        return {"error": "Analysis not found"}

    product_name = query
    status = data["status"]
    if status == AnalysisStatus.COMPLETED or status == AnalysisStatus.FAILED:
        return data

    db_service.update_analysis(analysis_id, status=AnalysisStatus.RUNNING)

    logger.info(f"Running analysis for product '{product_name}'")
    agent = generate_research_agent()
    research_context = ResearchContext()
    try:
        logger.info(f"Running analysis for product '{product_name}'")
        _ = await agent.run(f"conduct a comprehensive analysis for the product '{product_name}'", deps=research_context)
    except ExitProgramException:
        logger.info("Analysis Finished")
    finally:
        from datetime import datetime

        result = research_context.to_dict()
        report_path = result.get("report_path")
        logger.info(f"Report path: {report_path}")

        db_service.update_analysis(analysis_id, status=AnalysisStatus.COMPLETED, completed_at=datetime.now(), report=report_path)
        logger.info(f"Database updated for analysis {analysis_id}")

        return result
