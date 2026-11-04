from pydantic import BaseModel
from typing import Optional

class RecentDiagnosisItem(BaseModel):
    id: int
    status: str
    created_at: str
    detection_count: int
    primary_disease: Optional[str] = None
    original_image_url: str

class DashboardStats(BaseModel):
    total_diagnoses: int = 0
    detected_count: int = 0
    no_detection_count: int = 0
    disease_distribution: dict[str, int] = {}
    recent_diagnoses: list[RecentDiagnosisItem] = []
