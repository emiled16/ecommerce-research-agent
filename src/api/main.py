from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn

from src.api.routes import analysis, health
from src.config import settings
from src.database.database import get_database_info

app = FastAPI(
    title="E-commerce Research Agent API",
    description="AI-powered market analysis and research agent",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(health.router)


@app.get("/favicon.ico")
async def favicon():
    return Response(content="", media_type="image/x-icon")


@app.get("/")
async def root():
    db_info = get_database_info()
    return {
        "message": "E-commerce Research Agent API",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "database": db_info["database_type"],
        "docs": "/docs",
        "health": "/health",
    }


def start_server():
    uvicorn.run("src.api.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.API_RELOAD)


if __name__ == "__main__":
    start_server()
