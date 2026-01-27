from fastapi import APIRouter
from .endpoints.health import router as health_router

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
)

router.include_router(health_router)