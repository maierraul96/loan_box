from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class LoanApplication(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    monthly_income = Column(Integer, nullable=False)
    declared_debts = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    loan_purpose = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED, NEEDS_REVIEW
    created_at = Column(DateTime(timezone=True), server_default=func.now())
