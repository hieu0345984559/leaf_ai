import time
import uuid
import shutil
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from app.services.model_service import model_service
from app.models.diagnosis import DiagnosisHistory
from app.models.detection import DetectionResult
from app.core.config import settings, map_disease_label

logger = logging.getLogger(__name__)

# Distinct colors matching the reference UI palette (teal, purple, amber, cyan, pink, lime)
BOX_PALETTE = [
    {"stroke": (34, 211, 238), "bg": (34, 211, 238, 220), "text": (10, 15, 10)},    # Cyan
    {"stroke": (192, 132, 252), "bg": (192, 132, 252, 220), "text": (10, 15, 10)}, # Purple
    {"stroke": (52, 211, 153), "bg": (52, 211, 153, 220), "text": (10, 15, 10)},   # Emerald
    {"stroke": (251, 191, 36), "bg": (251, 191, 36, 220), "text": (10, 15, 10)},   # Amber
    {"stroke": (248, 113, 113), "bg": (248, 113, 113, 220), "text": (10, 15, 10)}, # Coral Red
    {"stroke": (244, 114, 182), "bg": (244, 114, 182, 220), "text": (10, 15, 10)}, # Pink
]

def clean_class_display(name: str) -> str:
    """Format label to standard customer display."""
    mapped = map_disease_label(name)
    return mapped.replace("Tomato___", "").replace("_", " ")

def draw_bounding_boxes(image_path: str, detections: list[dict], output_path: str) -> str:
    """Draw clear, modern bounding boxes with stylized tags matching reference UI."""
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try system fonts, fall back gracefully
    font = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ]:
        if Path(font_path).exists():
            try:
                font = ImageFont.truetype(font_path, 16)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()
        
    width, height = img.size
    
    for i, det in enumerate(detections):
        palette = BOX_PALETTE[i % len(BOX_PALETTE)]
        stroke_color = palette["stroke"]
        
        # Clamp coordinates
        x1 = max(0, min(float(det["x1"]), width - 1))
        y1 = max(0, min(float(det["y1"]), height - 1))
        x2 = max(0, min(float(det["x2"]), width - 1))
        y2 = max(0, min(float(det["y2"]), height - 1))
        
        # Draw bounding rectangle with 3px border
        for offset in range(3):
            draw.rectangle(
                [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                outline=(*stroke_color, 255)
            )
            
        # Draw translucent corner accents
        corner_len = min(20, (x2 - x1) / 3, (y2 - y1) / 3)
        if corner_len > 5:
            # Top-left, top-right, bottom-left, bottom-right accents
            accent_color = (255, 255, 255, 200)
            draw.line([(x1, y1), (x1 + corner_len, y1)], fill=accent_color, width=4)
            draw.line([(x1, y1), (x1, y1 + corner_len)], fill=accent_color, width=4)
            draw.line([(x2, y1), (x2 - corner_len, y1)], fill=accent_color, width=4)
            draw.line([(x2, y1), (x2, y1 + corner_len)], fill=accent_color, width=4)
            
        # Label text: e.g. "#1 | Bacterial Spot (88%)"
        cls_clean = clean_class_display(det["class_name"])
        conf_pct = det["confidence"] * 100
        label_text = f"#{i+1} | {cls_clean} ({conf_pct:.0f}%)"
        
        bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Place label above box if space permits, otherwise inside
        label_y1 = y1 - text_h - 10
        if label_y1 < 0:
            label_y1 = y1 + 4
        label_y2 = label_y1 + text_h + 8
        label_x1 = max(0, x1)
        label_x2 = min(width, label_x1 + text_w + 16)
        
        # Draw label background badge (rounded rect)
        draw.rounded_rectangle(
            [label_x1, label_y1, label_x2, label_y2],
            radius=4,
            fill=palette["bg"]
        )
        draw.text(
            (label_x1 + 8, label_y1 + 4),
            label_text,
            fill=palette["text"],
            font=font
        )
        
    # Composite overlay
    composed = Image.alpha_composite(img, overlay).convert("RGB")
    composed.save(output_path, "JPEG", quality=92)
    return output_path

def run_prediction(image_path: str, user_id: int, db: Session) -> DiagnosisHistory:
    """Execute complete inference pipeline and persist results."""
    start_time = time.time()
    
    # Generate unique ID and relative paths
    uid = uuid.uuid4().hex[:12]
    ext = Path(image_path).suffix.lower()
    if not ext:
        ext = ".jpg"
        
    orig_filename = f"{uid}_orig{ext}"
    orig_dest = settings.originals_dir / orig_filename
    
    # Securely copy source image to permanent originals storage
    shutil.copy2(image_path, str(orig_dest))
    
    # Execute inference
    results = model_service.predict(str(orig_dest))
    inference_time = time.time() - start_time
    
    healthy_boxes: list[dict] = []
    disease_boxes: list[dict] = []
    
    if results and len(results) > 0:
        res = results[0]
        if res.boxes is not None and len(res.boxes) > 0:
            boxes = res.boxes
            for idx in range(len(boxes)):
                box = boxes[idx]
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                conf = float(box.conf[0].cpu().numpy())
                cls_idx = int(box.cls[0].cpu().numpy())
                
                raw_class_name = model_service.class_names.get(cls_idx, f"Class_{cls_idx}")
                
                # Kiểm tra nếu đây là nhãn Healthy từ model
                is_healthy_cls = raw_class_name.strip().lower() == "healthy" or cls_idx == 3
                
                if is_healthy_cls:
                    healthy_threshold = settings.CLASS_CONFIDENCE_THRESHOLDS.get("Healthy", 0.35)
                    if conf >= healthy_threshold:
                        healthy_boxes.append({
                            "class_name": "Healthy",
                            "confidence": round(conf, 4),
                            "x1": round(xyxy[0], 2),
                            "y1": round(xyxy[1], 2),
                            "x2": round(xyxy[2], 2),
                            "y2": round(xyxy[3], 2)
                        })
                    continue
                
                # Phân loại và lọc ngưỡng đối với nhãn bệnh hại
                final_label = map_disease_label(raw_class_name)
                class_threshold = settings.CLASS_CONFIDENCE_THRESHOLDS.get(
                    raw_class_name,
                    settings.CLASS_CONFIDENCE_THRESHOLDS.get(
                        final_label,
                        settings.DEFAULT_CLASS_CONFIDENCE
                    )
                )
                if conf < class_threshold:
                    continue  # Bỏ qua ứng viên dưới ngưỡng độ tin cậy của phân lớp
                
                disease_boxes.append({
                    "class_name": final_label,
                    "confidence": round(conf, 4),
                    "x1": round(xyxy[0], 2),
                    "y1": round(xyxy[1], 2),
                    "x2": round(xyxy[2], 2),
                    "y2": round(xyxy[3], 2)
                })
                
    # Đánh giá Healthy vs Bệnh hại:
    # Nếu bệnh không quá rõ ràng (unclear / faint) hoặc nhãn Healthy chiếm ưu thế
    max_healthy_conf = max((b["confidence"] for b in healthy_boxes), default=0.0)
    max_disease_conf = max((b["confidence"] for b in disease_boxes), default=0.0)
    
    is_leaf_healthy = False
    unclear_disease = False
    
    if len(disease_boxes) == 0:
        is_leaf_healthy = True
    elif max_healthy_conf > 0:
        # Khi model đồng thời nhận diện vùng lá Healthy:
        # 1. Độ tin cậy Healthy cao hơn hoặc bằng độ tin cậy bệnh hại
        # 2. Hoặc Healthy >= 0.50 trong khi bệnh hại còn mờ nhạt (< 0.45)
        if max_healthy_conf >= max_disease_conf or (max_healthy_conf >= 0.50 and max_disease_conf < 0.45):
            is_leaf_healthy = True
            unclear_disease = True
            logger.info(
                f"Suppressed unclear disease ({max_disease_conf:.2f}) in favor of Healthy ({max_healthy_conf:.2f})"
            )
            
    if is_leaf_healthy:
        status = "no_detection"
        detections = []
    else:
        status = "detected"
        detections = disease_boxes
    
    # Generate annotated image
    result_rel_path = None
    if detections:
        result_filename = f"{uid}_annotated.jpg"
        result_dest = settings.results_dir / result_filename
        draw_bounding_boxes(str(orig_dest), detections, str(result_dest))
        result_rel_path = f"results/{result_filename}"
        
    orig_rel_path = f"originals/{orig_filename}"
    
    # Store records in SQLite
    diagnosis = DiagnosisHistory(
        user_id=user_id,
        original_image_path=orig_rel_path,
        result_image_path=result_rel_path,
        status=status,
        inference_time=round(inference_time, 3)
    )
    db.add(diagnosis)
    db.flush()
    
    for det in detections:
        rec = DetectionResult(
            history_id=diagnosis.id,
            class_name=det["class_name"],
            confidence=det["confidence"],
            x1=det["x1"],
            y1=det["y1"],
            x2=det["x2"],
            y2=det["y2"]
        )
        db.add(rec)
        
    db.commit()
    db.refresh(diagnosis)
    
    # Gắn metadata bổ sung phục vụ response
    setattr(diagnosis, "healthy_confidence", round(max_healthy_conf, 4) if max_healthy_conf > 0 else None)
    setattr(diagnosis, "unclear_disease_suppressed", unclear_disease)
    
    return diagnosis
