# System Architecture — LEAF_AI

## 1. System Overview

**LEAF_AI** is an enterprise-grade full-stack computer vision system engineered for rapid identification, localization, and management of plant foliar diseases using deep learning object detection.

```
┌────────────────────────────────────────────────────────┐
│               Frontend (React 18 + TypeScript)         │
│  - Dark Glassmorphism UI (Tailwind CSS v4 + WebGL)     │
│  - Diagnoses, Interactive Bounding Box Viewer          │
│  - Pathogen Encyclopedia & Treatment Routing           │
│  - Historical Diagnostic Audit Trail                   │
└───────────────────────────▲────────────────────────────┘
                            │ REST / JSON (Axios + JWT)
                            │ Multipart/form-data (Uploads)
┌───────────────────────────▼────────────────────────────┐
│              Backend API Gateway (FastAPI)             │
│  - Lifespan Model Preloading (Singleton Service)       │
│  - JWT Bearer Authentication & Bcrypt Hashing          │
│  - Multi-tenant User Data Isolation (SQLite ORM)       │
│  - Pillow Image Verification & Path Traversal Defense  │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  YOLO Inference Engine   │  │  Persistent Storage      │
│  - Ultralytics YOLOv8    │  │  - SQLite (leafai.db)    │
│  - `model/best.pt`       │  │  - `originals/` storage  │
│  - 640x640 Input Tensor  │  │  - `results/` annotated  │
│  - 6 Disease Classes     │  │    rendered JPEG clones  │
└──────────────────────────┘  └──────────────────────────┘
```

---

## 2. Model Inspection & Verification

The pre-trained model `model/best.pt` is an **Ultralytics YOLO Detection Model** trained with PyTorch:
- **Architecture**: `cultralytics.tasks.DetectionModel`
- **Trained Input Size**: `640x640`
- **Output**: Multi-class bounding boxes `(x1, y1, x2, y2)`, confidence scores `(0.00 – 1.00)`, and class indices `(0 – 5)`
- **Class Registry (YOLO model.names)**:
  0. `0: Algal Leaf Spot` (Bệnh Đốm Tảo Chè - Cephaleuros virescens)
  1. `1: Brown Blight` (Bệnh Đốm Nâu Chè - Colletotrichum camelliae)
  2. `2: Gray Blight` (Bệnh Đốm Xám Chè - Pestalotiopsis theae)
  3. `3: Healthy` (Lá chè khỏe mạnh)
  4. `4: Helopeltis` (Bọ xít muỗi hại chè - Helopeltis theivora)
  5. `5: Red Leaf Spot` (Bệnh Đốm Lá Đỏ Chè)

- **Foliar Disease Knowledge Catalog (Camellia sinensis)**:
  1. `Bacterial Leaf and Shoot Blight` (Cháy Lá & Khô Búp Do Vi Khuẩn)
  2. `Grey Blight` (Bệnh Đốm Xám / Thối Búp Xám Chè)
  3. `Brown Blight` (Bệnh Đốm Nâu / Thối Búp Nâu Chè)
  4. `White Scab` (Bệnh Sẹo Trắng / Đốm Sẹo Trắng Chè)
  5. `Blister Blight` (Bệnh Phồng Lá Chè / Đốm Phồng)
  6. `Algal Leaf Spot` (Bệnh Đốm Tảo / Rỉ Đỏ Do Tảo Chè)

> **Inference Status**: When disease symptoms or insect damage lesions are identified, the diagnosis status is `detected`. When no bounding boxes meet the confidence threshold, the status is reported as `no_detection`.

---

## 3. End-to-End Prediction Workflow

```
[User Browser]
      │
      │ 1. POST /api/predict (multipart/form-data)
      ▼
[FastAPI Gateway]
      │
      │ 2. Authenticate JWT Bearer Token
      │ 3. Validate MIME type, file size (<10MB), and verify Pillow stream
      ▼
[Image Storage Pipeline]
      │
      │ 4. Persist uncompressed source image to `storage/originals/{uuid}_orig.jpg`
      ▼
[ModelService (Singleton)]
      │
      │ 5. Execute `predict(source, conf=0.25, imgsz=640)`
      │ 6. Extract bounding boxes, confidence values, and class names
      ▼
[Annotation Service]
      │
      │ 7. If detections found:
      │    - Draw 3px colored bounding rectangles and corner brackets
      │    - Render high-contrast label badges: `#{index} | {disease} ({conf}%)`
      │    - Save composite image to `storage/results/{uuid}_annotated.jpg`
      ▼
[Persistence Layer (SQLite)]
      │
      │ 8. Insert record in `diagnosis_history` (foreign key to `users.id`)
      │ 9. Insert records in `detection_results` (foreign key to `diagnosis_history.id`)
      ▼
[Client Response]
      │
      │ 10. Return JSON payload with image URLs, status, latency, and detections
      ▼
[React UI]
      - Display side-by-side or toggled Original vs Annotated view
      - Render interactive spot map, zoom controls, and treatment plan
```

---

## 4. Database Schema & Entity Relationships

The relational model is maintained using **SQLAlchemy 2.0 ORM** on **SQLite**:

```
 ┌──────────────────────┐
 │        users         │
 ├──────────────────────┤
 │ id (PK, INT)         │
 │ email (VARCHAR, UNQ) │
 │ password_hash (STR)  │
 │ created_at (DATETIME)│
 │ updated_at (DATETIME)│
 └──────────┬───────────┘
            │ 1:N
            ▼
 ┌───────────────────────────────┐
 │       diagnosis_history       │
 ├───────────────────────────────┤
 │ id (PK, INT)                  │
 │ user_id (FK -> users.id)      │
 │ original_image_path (VARCHAR) │
 │ result_image_path (VARCHAR)   │
 │ status (VARCHAR)              │
 │ inference_time (FLOAT)        │
 │ created_at (DATETIME)         │
 └──────────┬────────────────────┘
            │ 1:N (CASCADE)
            ▼
 ┌──────────────────────────────────┐        ┌─────────────────────────┐
 │        detection_results         │        │        diseases         │
 ├──────────────────────────────────┤        ├─────────────────────────┤
 │ id (PK, INT)                     │        │ id (PK, INT)            │
 │ history_id (FK -> diagnosis.id)  │        │ class_name (VARCHAR)    │
 │ class_name (VARCHAR)             │        │ display_name (VARCHAR)  │
 │ confidence (FLOAT)               │        │ description (TEXT)      │
 │ x1, y1, x2, y2 (FLOAT)           │        │ symptoms (TEXT)         │
 │ created_at (DATETIME)            │        │ prevention (TEXT)       │
 └──────────────────────────────────┘        │ treatment (TEXT)        │
                                             │ image_path (VARCHAR)    │
                                             │ created_at (DATETIME)   │
                                             │ updated_at (DATETIME)   │
                                             └─────────────────────────┘
```

---

## 5. Security & Isolation Architecture

1. **Authentication**:
   - Passwords hashed using `bcrypt` with salt rounds.
   - JWT tokens signed with `HS256` containing `sub` (User ID), `email`, and `exp`.
2. **Multi-Tenant Isolation**:
   - All `/api/history` and `/api/dashboard/stats` queries filter strictly by `current_user.id`.
   - Records cannot be accessed or deleted across tenant boundaries.
3. **Safe Storage & Path Traversal Prevention**:
   - Files are stored in `storage/originals/` and `storage/results/`.
   - Streaming endpoints validate that target paths resolve within the permitted storage directory.
   - User uploads cannot execute code or access server filesystem hierarchies.
