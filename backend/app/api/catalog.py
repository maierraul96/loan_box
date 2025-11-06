from fastapi import APIRouter
from app.steps.registry import get_step_catalog

router = APIRouter(prefix="/api/steps", tags=["catalog"])


@router.get("/catalog")
def get_catalog():
    """Get catalog of available pipeline steps with their default parameters"""
    return {
        "steps": get_step_catalog()
    }
