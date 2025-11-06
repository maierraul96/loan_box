from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    step_logs = Column(Text, nullable=False)  # JSON string
    terminal_rule_logs = Column(Text, nullable=False, default="[]")  # JSON string
    final_status = Column(String, nullable=False)  # APPROVED, REJECTED, NEEDS_REVIEW
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
