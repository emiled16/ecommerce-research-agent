from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid

from src.api.models.analysis.requests import AnalysisRequest
from src.api.models.analysis.responses import AnalysisResponse
from src.api.models.analysis.responses import AnalysisStatus
from src.api.services.research import run_analysis
from src.api.services.database_service import db_service

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    try:
        analysis_id = str(uuid.uuid4())
        output = {
            "analysis_id": analysis_id,
            "query": request.query,
            "status": AnalysisStatus.RUNNING,
            "created_at": datetime.now(),
            "completed_at": None,
            "report": None,
            "error": None,
        }
        db_service.add_analysis(**output)
        background_tasks.add_task(run_analysis, analysis_id, request.query, db_service)
        return AnalysisResponse(**output)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analyze/{analysis_id}")
async def get_analysis(analysis_id: str) -> FileResponse:
    try:
        data = db_service.get_analysis(analysis_id)
        if not data:
            raise HTTPException(status_code=404, detail="Analysis not found")

        if data["status"] == AnalysisStatus.COMPLETED and data["report"]:
            return FileResponse(data["report"])

        return FileResponse("template/analysis_still_running.html")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/analyze", response_model=list[AnalysisResponse])
async def list_analyses() -> list[AnalysisResponse]:
    try:
        analyses = []
        for data in db_service.get_all_analyses():
            analyses.append(
                AnalysisResponse(
                    analysis_id=data["analysis_id"],
                    status=data["status"],
                    created_at=data["created_at"],
                    completed_at=data["completed_at"],
                    report=data["report"],
                    error=data["error"],
                )
            )
        return analyses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
