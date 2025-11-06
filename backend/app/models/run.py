from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any
from datetime import datetime
from app.models.enums import FinalStatus


class StepLog(BaseModel):
    step_type: str
    order: int
    passed: bool
    computed_values: Dict[str, Any]
    message: str


class TerminalRuleLog(BaseModel):
    condition: str
    outcome: FinalStatus
    order: int
    evaluated: bool
    matched: bool
    reason: str


class RunRequest(BaseModel):
    application_id: int = Field(..., gt=0)
    pipeline_id: int = Field(..., gt=0)


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    pipeline_id: int
    step_logs: List[StepLog]
    terminal_rule_logs: List[TerminalRuleLog]
    final_status: FinalStatus
    executed_at: datetime
