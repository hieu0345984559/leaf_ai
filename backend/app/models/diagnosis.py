from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_image_path = Column(String(500), nullable=False)
    result_image_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="no_detection")
    inference_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    user = relationship("User", back_populates="diagnoses")
    detections = relationship("DetectionResult", back_populates="diagnosis", cascade="all, delete-orphan", lazy="joined")
