from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiseaseResponse(BaseModel):
    id: int
    class_name: str
    display_name: str
    description: Optional[str] = None
    symptoms: Optional[str] = None
    prevention: Optional[str] = None
    treatment: Optional[str] = None
    treatment_steps: Optional[str] = None
    recovery_info: Optional[str] = None
    image_path: Optional[str] = None
    
    class Config:
        from_attributes = True

class DiseaseListResponse(BaseModel):
    id: int
    class_name: str
    display_name: str
    description: Optional[str] = None
    symptoms: Optional[str] = None
    prevention: Optional[str] = None
    treatment: Optional[str] = None
    treatment_steps: Optional[str] = None
    recovery_info: Optional[str] = None
    image_path: Optional[str] = None
    
    class Config:
        from_attributes = True
