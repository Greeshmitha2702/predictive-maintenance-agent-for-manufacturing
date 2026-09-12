# Predictive Maintenance Agent for Manufacturing

An AI-powered predictive maintenance solution for manufacturing equipment.
The system predicts failure probabilities, detects anomalies, identifies root causes using Explainable AI (SHAP), assesses risk, and provides deterministic prescriptive maintenance recommendations — all served through a React dashboard backed by a FastAPI ML pipeline.

---

## Architecture

```
React Frontend (Vite)
    ↓  POST /api/v1/predict
FastAPI Backend
    ↓
PredictiveMaintenanceAgent
    ├── AnomalyDetectionService      (Isolation Forest)
    ├── FailurePredictionService     (Balanced Random Forest, threshold 0.49)
    ├── ShapExplainabilityService    (SHAP TreeExplainer)
    ├── RiskAssessmentService        (deterministic thresholds)
    └── RecommendationEngine         (deterministic rules)
```

---

## Project Structure

```
predictive-maintenance/
├── frontend/                  # React + Vite web dashboard
│   ├── src/
│   │   ├── components/        # UI components (cards, form, SHAP, recommendations)
│   │   ├── pages/             # Dashboard, Analysis, History, Welcome, About
│   │   └── services/api.js    # API client + response mapping layer
│   ├── .env.development       # Dev environment variables
│   └── vite.config.js
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── api/               # Routes (/health, /predict)
│   │   ├── agent/             # PredictiveMaintenanceAgent orchestration
│   │   ├── services/          # ML inference services + RecommendationEngine
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   └── models/            # Risk config and domain models
│   ├── tests/                 # Unit + E2E tests
│   └── requirements.txt
├── ml/                        # Machine learning pipeline
│   ├── notebooks/             # EDA, model training, evaluation notebooks
│   ├── src/                   # Feature engineering, preprocessing scripts
│   └── models/                # Trained model artifacts (.pkl / .joblib)
├── data/                      # Dataset directory
└── docs/
    ├── HLD.md                 # High-Level Design
    └── LLD.md                 # Low-Level Design
```

---

## Prerequisites

| Tool | Minimum version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

## Quick Start

### 1 — Clone the repository

```bash
git clone <repository-url>
cd predictive-maintenance
```

---

### 2 — Backend Setup

```bash
cd backend
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Start the development server**

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.

**Verify the backend is running**

```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"ok","version":"0.4.0"}
```

---

### 3 — Frontend Setup

Open a **new terminal**, then:

```bash
cd frontend
```

**Install dependencies**

```bash
npm install
```

**Start the development server**

```bash
npm run dev
```

The dashboard opens at `http://localhost:5173`.

> The frontend is pre-configured to connect to the backend at `http://localhost:8000`.
> The Vite dev server proxies `/api/*` requests to the backend automatically.

---

## Running Both Together

```
Terminal 1 — Backend
──────────────────────────────────────────────────
cd predictive-maintenance/backend
python -m uvicorn app.main:app --reload --port 8000

Terminal 2 — Frontend
──────────────────────────────────────────────────
cd predictive-maintenance/frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## API Reference

### Health Check

```
GET /api/v1/health
```

Response:
```json
{ "status": "ok", "version": "0.4.0" }
```

---

### Predict Machine Health

```
POST /api/v1/predict
Content-Type: application/json
```

Request body:

```json
{
  "type": "M",
  "air_temperature": 298.1,
  "process_temperature": 308.6,
  "rotational_speed": 1551,
  "torque": 42.8,
  "tool_wear": 120
}
```

| Field | Type | Constraints |
|---|---|---|
| `type` | string | `"L"`, `"M"`, or `"H"` |
| `air_temperature` | float | > 0 K |
| `process_temperature` | float | > 0 and ≤ 400 K |
| `rotational_speed` | float | > 0 rpm |
| `torque` | float | ≥ 0 Nm |
| `tool_wear` | float | ≥ 0 min |

Response:

```json
{
  "failure_probability": 0.0,
  "failure_predicted": false,
  "is_anomaly": false,
  "anomaly_score": 0.11,
  "risk_level": "LOW",
  "model_version": "Balanced Random Forest (Threshold: 0.4900)",
  "explanation": {
    "top_factors": [
      {
        "feature": "mechanical_power_W",
        "contribution": -0.109,
        "direction": "decreases_failure_risk"
      }
    ],
    "disclaimer": "SHAP feature attributions describe statistical model risk contributions, not guaranteed physical root causes."
  },
  "recommendations": {
    "risk_level": "LOW",
    "urgency": "Continue standard preventive maintenance schedule",
    "root_cause_indicators": [],
    "recommendations": [
      {
        "id": "REC-LOW-000",
        "category": "INSPECTION",
        "severity": "INFO",
        "title": "Continue Standard Maintenance",
        "action": "Failure risk is LOW. Continue standard inspection and shift logging."
      }
    ]
  }
}
```

Interactive API docs (Swagger UI): `http://localhost:8000/docs`

---

## Environment Variables

### Frontend — `frontend/.env.development`

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL |
| `VITE_USE_MOCK_API` | `false` | Set to `true` to use mock data without a backend |

**Real API mode (default):**

```
VITE_USE_MOCK_API=false
VITE_API_BASE_URL=http://localhost:8000
```

**Mock mode (no backend required):**

```
VITE_USE_MOCK_API=true
```

---

## Tests

### Backend — Unit tests

```bash
cd backend
python tests/test_recommendation_engine.py
```

Expected: `Ran 23 tests … OK`

### Backend — End-to-end tests

Requires the backend server running on port 8000.

```bash
cd backend
python tests/test_e2e.py
```

Expected: `Ran 20 tests … OK`

### Frontend — Lint

```bash
cd frontend
npm run lint
```

### Frontend — Production build

```bash
cd frontend
npm run build
```

---

## ML Models

| Artifact | Algorithm | Purpose |
|---|---|---|
| `ml/models/failure_pipeline.pkl` | Balanced Random Forest (threshold 0.49) | Failure probability prediction |
| `ml/models/anomaly_pipeline.pkl` | Isolation Forest | Anomaly detection |

Models are pre-trained and loaded at startup as singletons. Do not retrain or replace them.

---

## Risk Levels

| Failure Probability | Risk Level |
|---|---|
| < 0.30 | **LOW** |
| 0.30 – 0.70 | **MEDIUM** |
| > 0.70 | **HIGH** |

Anomaly detection and failure prediction are **independent signals**.
A machine can be anomalous with LOW failure risk, or have HIGH failure risk without being anomalous.
