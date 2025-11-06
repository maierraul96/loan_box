from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.models.enums import FinalStatus


class LoanApplicationCreate(BaseModel):
    applicant_name: str = Field(..., min_length=1)
    amount: int = Field(..., gt=0)
    monthly_income: int = Field(..., gt=0)
    declared_debts: int = Field(..., ge=0)
    country: str = Field(..., min_length=2, max_length=10)
    loan_purpose: str = Field(..., min_length=1)


class LoanApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    applicant_name: str
    amount: int
    monthly_income: int
    declared_debts: int
    country: str
    loan_purpose: str
    status: FinalStatus
    created_at: datetime
