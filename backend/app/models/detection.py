from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class DetectionResult(Base):
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(Integer, ForeignKey("diagnosis_history.id", ondelete="CASCADE"), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    diagnosis = relationship("DiagnosisHistory", back_populates="detections")
