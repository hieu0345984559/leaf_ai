from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DetectionResponse(BaseModel):
    id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    
    class Config:
        from_attributes = True

class DiagnosisResponse(BaseModel):
    id: int
    original_image_url: str
    result_image_url: Optional[str] = None
    status: str
    inference_time: Optional[float] = None
    created_at: datetime
    detections: list[DetectionResponse] = []
    
    class Config:
        from_attributes = True

class DiagnosisListResponse(BaseModel):
    id: int
    original_image_url: str
    result_image_url: Optional[str] = None
    status: str
    inference_time: Optional[float] = None
    created_at: datetime
    detection_count: int = 0
    primary_disease: Optional[str] = None
    max_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True

class PredictResponse(BaseModel):
    id: int
    original_image_url: str
    result_image_url: Optional[str] = None
    status: str
    inference_time: Optional[float] = None
    created_at: datetime
    detections: list[DetectionResponse] = []
    summary: str
