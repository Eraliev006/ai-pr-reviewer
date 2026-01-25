from fastapi import FastAPI
from app.core import config
from app.core import setup_logging
from app.api.v1 import router as api_v1_router

setup_logging()

app = FastAPI(
    title=config.PROJECT_NAME,
    version="0.1.0",
    description="AI PR Reviewer",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_v1_router, prefix=config.API_V1_STR)