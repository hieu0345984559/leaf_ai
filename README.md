# LEAF_AI — Tea & Plant Leaf Disease Detection System

An enterprise-ready, full-stack AI web application designed for agricultural diagnosis, foliar pathogen detection, and agronomic management using deep learning computer vision.

![LEAF_AI Visual Theme](frontend/public/leaf.svg)

---

## 1. Project Overview

**LEAF_AI** enables growers, agronomists, and researchers to detect disease-affected leaf regions with high precision. Users register, authenticate, upload or capture leaf imagery, inspect detected disease regions with confidence percentages and pixel-level bounding boxes, explore disease profiles and treatments in the Disease Library, and review their historical diagnostic scans.

### Core Features

- **Deep Vision Inference**: Integrates an Ultralytics YOLO model (`model/best.pt`) running 640×640 multi-class object detection.
- **Interactive Bounding Box Inspection**: Visualizer allowing instant switching between original and annotated imagery, box coordinates display, zoom controls, and lesion summaries.
- **Dark Glassmorphism UI/UX**: Sleek interface inspired by precision agriculture dashboards with glowing accents, subtle WebGL canvas background shaders, and responsive desktop/mobile layouts.
- **Enterprise Security & Tenant Isolation**: Bcrypt password hashing, JWT bearer tokens, and strict user-level database query scoping.
- **Complete Pathogen Encyclopedia**: Structured knowledge base detailing etiology, visual symptoms, cultural prevention, and IPM chemical treatments.
- **Audit History & Reporting**: Persistent diagnostic log with filtering by status, search by disease, detailed modal views, and safe record cleanup.

---

## 2. Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Bundler & Tooling**: Vite 6, `@tailwindcss/vite`
- **Styling**: Tailwind CSS v4, custom glassmorphism design tokens, CSS keyframe animations
- **Effects**: Custom WebGL Canvas fragment shader for ambient emerald glow
- **Routing**: React Router DOM v6
- **HTTP Client**: Axios with request/response authorization interceptors
- **Icons**: Lucide React
- **Data Visualization**: Recharts

### Backend
- **Framework**: FastAPI (Python 3.12 / 3.10+)
- **ASGI Server**: Uvicorn
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (`backend/data/leafai.db`)
- **Computer Vision**: Ultralytics YOLO, PyTorch, Pillow
- **Security**: PyJWT, Bcrypt
- **Testing**: PyTest with Starlette TestClient

---

## 3. Verified AI Model Specification

The application leverages the existing model weights preserved strictly at:

```
model/best.pt
```

- **Model Format**: Ultralytics YOLO Object Detection Model (Tea Plant - *Camellia sinensis*)
- **Input Resolution**: `640x640`
- **Model Training Classes (6)**:
  0. `Algal Leaf Spot` (Bệnh Đốm Tảo Chè - Cephaleuros virescens)
  1. `Brown Blight` (Bệnh Đốm Nâu Chè - Colletotrichum camelliae)
  2. `Gray Blight` (Bệnh Đốm Xám Chè - Pestalotiopsis theae)
  3. `Healthy` (Lá chè khỏe mạnh)
  4. `Helopeltis` (Bọ xít muỗi hại chè - Helopeltis theivora)
  5. `Red Leaf Spot` (Bệnh Đốm Lá Đỏ Chè)

- **Foliar Disease Knowledge Catalog (6)**:
  1. `Bacterial Leaf and Shoot Blight` (Cháy Lá & Khô Búp Do Vi Khuẩn)
  2. `Grey Blight` (Bệnh Đốm Xám / Thối Búp Xám Chè)
  3. `Brown Blight` (Bệnh Đốm Nâu / Thối Búp Nâu Chè)
  4. `White Scab` (Bệnh Sẹo Trắng / Đốm Sẹo Trắng Chè)
  5. `Blister Blight` (Bệnh Phồng Lá Chè / Đốm Phồng)
  6. `Algal Leaf Spot` (Bệnh Đốm Tảo / Rỉ Đỏ Do Tảo Chè)

*Note on Status Determination*: When disease symptoms or lesions are identified, the diagnosis status is `detected`. When no bounding boxes meet the confidence threshold or the foliage is clear, the status is reported as `no_detection` or clear.

---

## 4. Repository Structure

```text
LEAF_AI/
├── model/
│   └── best.pt                  # Pre-trained YOLO detection weights (preserved)
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & lifespan
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic BaseSettings & path resolution
│   │   │   ├── security.py      # Bcrypt & JWT token utilities
│   │   │   └── dependencies.py  # User authorization dependency
│   │   ├── db/
│   │   │   ├── base.py          # SQLAlchemy DeclarativeBase
│   │   │   ├── session.py       # Engine & SessionLocal
│   │   │   └── init_db.py       # Table schema generation & disease seeding
│   │   ├── models/
│   │   │   ├── user.py          # User authentication entity
│   │   │   ├── diagnosis.py     # DiagnosisHistory entity
│   │   │   ├── detection.py     # DetectionResults entity
│   │   │   └── disease.py       # Disease encyclopedia entity
│   │   ├── schemas/
│   │   │   ├── auth.py          # Auth validation schemas
│   │   │   ├── diagnosis.py     # Prediction & history schemas
│   │   │   ├── disease.py       # Disease library schemas
│   │   │   └── dashboard.py     # Analytics & metric schemas
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py      # /api/auth routes
│   │   │       ├── predict.py   # /api/predict route
│   │   │       ├── history.py   # /api/history routes
│   │   │       ├── diseases.py  # /api/diseases routes
│   │   │       └── dashboard.py # /api/dashboard routes
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── model_service.py # Singleton YOLO loader
│   │   │   ├── prediction_service.py # Inference & annotation pipeline
│   │   │   ├── history_service.py
│   │   │   └── disease_service.py
│   │   ├── utils/
│   │   │   └── image_utils.py   # Upload sanitization & validation
│   │   ├── storage/
│   │   │   ├── originals/       # Unaltered uploaded images
│   │   │   └── results/         # Rendered bounding box images
│   │   ├── data/                # SQLite database directory (leafai.db)
│   │   └── tests/
│   │       └── test_api.py      # Comprehensive pytest test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/                 # Typed Axios API clients
│   │   ├── components/          # Reusable glassmorphic UI components
│   │   ├── contexts/            # React AuthContext
│   │   ├── layouts/             # AppLayout with Sidebar & WebGL
│   │   ├── pages/               # Login, Register, Dashboard, Diagnose, etc.
│   │   ├── types/               # TypeScript data definitions
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css            # Tailwind CSS & glassmorphic tokens
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── README.md
├── docs/
│   └── architecture.md          # Architectural blueprints & flows
├── .gitignore
└── README.md
```

---

## 5. Quick Start Guide

### Step 1: Clone & Prerequisites
Ensure Python 3.10+ and Node.js 18+ are available on your system.

### Step 2: Backend Setup & Launch

```bash
cd backend

# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies (CPU PyTorch + requirements)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 3. Setup environment configuration
cp .env.example .env

# 4. Launch FastAPI server
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend starts at `http://127.0.0.1:8000`. Database tables and initial disease entries are automatically seeded on startup.

### Step 3: Frontend Setup & Launch

Open a separate terminal:

```bash
cd frontend

# 1. Install Node dependencies
npm install

# 2. Setup environment configuration
cp .env.example .env

# 3. Launch Vite dev server
npm run dev
```

Open your browser at: **[http://localhost:5173](http://localhost:5173)**.

---

## 6. Testing & Quality Verification

Run backend integration tests:

```bash
cd backend
venv/bin/pytest app/tests/test_api.py -v
```

Run frontend production compilation check:

```bash
cd frontend
npm run build
```

---

## 7. Security Highlights

- **Strict Access Control**: Every protected endpoint validates Bearer JWT tokens. Users can only access and modify their own records.
- **Safe Image Processing**: Uploaded files undergo MIME type verification, extension checks, size validation (<10MB), and Pillow stream decoding before reaching the disk.
- **Path Traversal Shield**: The image serving route strictly verifies that file paths resolve within permitted storage folders.
- **Credential Protection**: Passwords are encrypted with `bcrypt` salts. Plaintext passwords are never logged or stored.


Email: testuser@leafai.dev
Mật khẩu: SecurePassword123

