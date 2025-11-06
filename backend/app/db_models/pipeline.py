from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    steps_config = Column(Text, nullable=False)  # JSON string
    terminal_rules = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
