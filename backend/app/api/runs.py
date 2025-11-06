import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RunRequest, RunResponse
from app.db_models import PipelineRun
from app.services import PipelineExecutor

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=201)
def execute_pipeline(
    run_request: RunRequest,
    db: Session = Depends(get_db)
):
    """Execute a pipeline on a loan application"""
    try:
        executor = PipelineExecutor(db)
        run = executor.execute(run_request.application_id, run_request.pipeline_id)
        return _run_to_response(run)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.get("", response_model=List[RunResponse])
def list_runs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all pipeline runs (history)"""
    runs = db.query(PipelineRun).order_by(PipelineRun.executed_at.desc()).offset(skip).limit(limit).all()
    return [_run_to_response(r) for r in runs]


@router.get("/{run_id}", response_model=RunResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific pipeline run"""
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_response(run)


def _run_to_response(run: PipelineRun) -> RunResponse:
    """Convert PipelineRun DB model to RunResponse"""
    return RunResponse(
        id=run.id,
        application_id=run.application_id,
        pipeline_id=run.pipeline_id,
        step_logs=json.loads(run.step_logs),
        terminal_rule_logs=json.loads(run.terminal_rule_logs),
        final_status=run.final_status,
        executed_at=run.executed_at
    )
