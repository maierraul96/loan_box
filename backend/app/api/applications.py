from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LoanApplicationCreate, LoanApplicationResponse
from app.db_models import LoanApplication

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=LoanApplicationResponse, status_code=201)
def create_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new loan application"""
    db_application = LoanApplication(
        applicant_name=application.applicant_name,
        amount=application.amount,
        monthly_income=application.monthly_income,
        declared_debts=application.declared_debts,
        country=application.country,
        loan_purpose=application.loan_purpose,
        status="PENDING"
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("", response_model=List[LoanApplicationResponse])
def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all loan applications"""
    applications = db.query(LoanApplication).offset(skip).limit(limit).all()
    return applications


@router.get("/{application_id}", response_model=LoanApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific loan application"""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
