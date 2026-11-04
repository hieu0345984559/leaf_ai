# LEAF_AI — Frontend Application

React 18 + TypeScript single-page application crafted with a Dark Glassmorphism visual design system, WebGL canvas shaders, real-time bounding box visualization, and interactive pathogen guides.

---

## 1. Prerequisites

- Node.js 18+ (Tested on Node v24.21.0)
- npm 9+ (Tested on npm 11.19.0)

---

## 2. Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

---

## 3. Environment Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

Ensure `VITE_API_BASE_URL` points to your running FastAPI backend:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## 4. Development Server

Start Vite in development mode with HMR:

```bash
npm run dev
```

The application will be accessible at: [http://localhost:5173](http://localhost:5173).

---

## 5. Production Build

Compile TypeScript and build the optimized production assets:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

---

## 6. Application Architecture & Routing

| Route | Component | Access | Description |
| :--- | :--- | :--- | :--- |
| `/login` | `LoginPage` | Public | Email and password authentication with password toggle |
| `/register` | `RegisterPage` | Public | User onboarding with password confirmation |
| `/dashboard` | `DashboardPage` | Protected | Diagnostic metrics, disease distribution charts, quick scan hero |
| `/diagnose` | `DiagnosePage` | Protected | Drag-and-drop, camera capture, real-time YOLO bounding box viewer |
| `/diseases` | `DiseasesPage` | Protected | Searchable library of detected leaf diseases with modal details |
| `/history` | `HistoryPage` | Protected | User diagnosis audit trail with status filters, zoom, and deletion |

---

## 7. Common Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `Network Error` or `Cannot connect to API` | Backend is not running on port 8000 | Verify FastAPI backend is running via `uvicorn app.main:app` |
| `Failed to load resource: 401 Unauthorized` | JWT token expired or missing | Sign in again through `/login`. Tokens automatically refresh user sessions. |
| Camera capture not opening | Browser permissions or HTTP origin | Ensure camera permissions are granted. Modern browsers require `localhost` or HTTPS for camera APIs. |
