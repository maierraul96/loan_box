from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.enums import FinalStatus, StepType


class PipelineStepConfig(BaseModel):
    step_type: StepType
    order: int = Field(..., ge=1)
    params: Dict[str, Any] = Field(default_factory=dict)


class TerminalRule(BaseModel):
    condition: str = Field(..., min_length=1)
    outcome: FinalStatus
    order: int = Field(..., ge=1)


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    steps: List[PipelineStepConfig] = Field(..., min_length=1)
    terminal_rules: List[TerminalRule] = Field(..., min_length=1)


class PipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    steps: Optional[List[PipelineStepConfig]] = Field(None, min_length=1)
    terminal_rules: Optional[List[TerminalRule]] = Field(None, min_length=1)


class PipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    steps: List[PipelineStepConfig]
    terminal_rules: List[TerminalRule]
    created_at: datetime
