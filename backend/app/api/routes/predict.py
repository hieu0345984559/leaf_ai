from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.image_utils import validate_and_save_upload
from app.services.prediction_service import run_prediction
from app.services.model_service import model_service
from app.schemas.diagnosis import PredictResponse, DetectionResponse
from app.core.config import map_disease_label
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Prediction"])

@router.post("/predict", response_model=PredictResponse)
async def predict(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI model service is unavailable: {model_service.load_error or 'Model not initialized'}"
        )
        
    # Validate and buffer image safely
    temp_path = await validate_and_save_upload(file)
    
    try:
        diagnosis = run_prediction(temp_path, current_user.id, db)
    except Exception as e:
        logger.error(f"Prediction failed for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )
    finally:
        # Cleanup temporary upload if it still exists
        if Path(temp_path).exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
    detection_items = [
        DetectionResponse(
            id=d.id,
            class_name=map_disease_label(d.class_name),
            confidence=d.confidence,
            x1=d.x1,
            y1=d.y1,
            x2=d.x2,
            y2=d.y2
        )
        for d in diagnosis.detections
    ]
    
    # Formulate friendly diagnosis summary
    if len(detection_items) == 0:
        healthy_conf = getattr(diagnosis, "healthy_confidence", None)
        unclear_suppressed = getattr(diagnosis, "unclear_disease_suppressed", False)
        
        if healthy_conf and healthy_conf > 0:
            if unclear_suppressed:
                summary = f"Mô hình xác nhận lá chè khỏe mạnh với độ tin cậy {healthy_conf*100:.1f}%. Các triệu chứng nghi ngờ mờ nhạt hoặc không đủ rõ ràng để xác nhận bệnh hại."
            else:
                summary = f"Mô hình xác nhận lá chè khỏe mạnh (Healthy) với độ tin cậy {healthy_conf*100:.1f}%. Không phát hiện dấu hiệu bệnh hại."
        else:
            summary = "Không phát hiện dấu hiệu bệnh hại trên lá ở ngưỡng độ tin cậy hiện tại. Lá chè khỏe mạnh."
    else:
        top_det = max(detection_items, key=lambda x: x.confidence)
        cls_clean = map_disease_label(top_det.class_name).replace("Tomato___", "").replace("_", " ")
        summary = f"Phát hiện dấu hiệu {cls_clean} với độ tin cậy {top_det.confidence*100:.1f}% trên {len(detection_items)} vùng tổn thương."
        
    return PredictResponse(
        id=diagnosis.id,
        original_image_url=f"/api/images/{diagnosis.original_image_path}",
        result_image_url=f"/api/images/{diagnosis.result_image_path}" if diagnosis.result_image_path else None,
        status=diagnosis.status,
        inference_time=diagnosis.inference_time,
        created_at=diagnosis.created_at,
        detections=detection_items,
        summary=summary
    )
