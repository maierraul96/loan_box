import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PipelineCreate, PipelineUpdate, PipelineResponse
from app.db_models import Pipeline

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineResponse, status_code=201)
def create_pipeline(
    pipeline: PipelineCreate,
    db: Session = Depends(get_db)
):
    """Create a new pipeline"""
    db_pipeline = Pipeline(
        name=pipeline.name,
        description=pipeline.description,
        steps_config=json.dumps([step.model_dump() for step in pipeline.steps]),
        terminal_rules=json.dumps([rule.model_dump() for rule in pipeline.terminal_rules])
    )
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)

    # Convert back to response model
    return _pipeline_to_response(db_pipeline)


@router.get("", response_model=List[PipelineResponse])
def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all pipelines"""
    pipelines = db.query(Pipeline).offset(skip).limit(limit).all()
    return [_pipeline_to_response(p) for p in pipelines]


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific pipeline"""
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return _pipeline_to_response(pipeline)


@router.put("/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(
    pipeline_id: int,
    pipeline_update: PipelineUpdate,
    db: Session = Depends(get_db)
):
    """Update a pipeline"""
    db_pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not db_pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Update fields if provided
    if pipeline_update.name is not None:
        db_pipeline.name = pipeline_update.name
    if pipeline_update.description is not None:
        db_pipeline.description = pipeline_update.description
    if pipeline_update.steps is not None:
        db_pipeline.steps_config = json.dumps([step.model_dump() for step in pipeline_update.steps])
    if pipeline_update.terminal_rules is not None:
        db_pipeline.terminal_rules = json.dumps([rule.model_dump() for rule in pipeline_update.terminal_rules])

    db.commit()
    db.refresh(db_pipeline)
    return _pipeline_to_response(db_pipeline)


def _pipeline_to_response(pipeline: Pipeline) -> PipelineResponse:
    """Convert Pipeline DB model to PipelineResponse"""
    return PipelineResponse(
        id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        steps=json.loads(pipeline.steps_config),
        terminal_rules=json.loads(pipeline.terminal_rules),
        created_at=pipeline.created_at
    )
