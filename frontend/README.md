# Predictive Maintenance — Frontend

React + Vite web dashboard for the Predictive Maintenance Agent.

Displays machine health predictions, anomaly detection results, SHAP explanations, risk levels, and maintenance recommendations — sourced from the FastAPI backend.

---

## Prerequisites

- Node.js 18+
- npm 9+
- Backend running at `http://localhost:8000`

---

## Setup

```bash
npm install
```

---

## Commands

| Command | Description |
|---|---|
| `npm run dev` | Start development server at `http://localhost:5173` |
| `npm run build` | Build production bundle to `dist/` |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview the production build locally |

---

## Running with the Backend

Start the backend first (see root [README](../README.md)), then:

```bash
npm run dev
```

The Vite dev server proxies `/api/*` requests to `http://localhost:8000` automatically — no CORS configuration needed during development.

---

## Environment Variables

Create or edit `frontend/.env.development`:

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL |
| `VITE_USE_MOCK_API` | `false` | `true` = mock mode (no backend needed) |

**Real API mode (default):**
```
VITE_USE_MOCK_API=false
VITE_API_BASE_URL=http://localhost:8000
```

**Mock mode:**
```
VITE_USE_MOCK_API=true
```

---

## Project Structure

```
src/
├── components/
│   ├── MachineInputForm.jsx       # 6-field machine parameter form
│   ├── RiskSummary.jsx            # Failure probability + risk level card
│   ├── AnomalyCard.jsx            # Anomaly detection status card
│   ├── FailurePredictionCard.jsx  # ML prediction result card
│   ├── SHAPExplanation.jsx        # SHAP top-factors bar chart
│   ├── RecommendationSection.jsx  # Structured maintenance recommendations
│   ├── Header.jsx
│   ├── LoadingState.jsx
│   └── ErrorMessage.jsx
├── pages/
│   ├── Dashboard.jsx              # Main prediction + results page
│   ├── Analysis.jsx               # Detailed SHAP + recommendation view
│   ├── History.jsx                # Saved analyses (localStorage)
│   ├── Welcome.jsx
│   └── About.jsx
└── services/
    └── api.js                     # API client, response mapping, error formatting
```

---

## API Integration

All backend communication goes through `src/services/api.js`.

- **Request:** 6-field machine parameters sent as JSON to `POST /api/v1/predict`
- **Response mapping:** flat backend response → nested shape expected by UI components (centralised in `mapApiResponse()`)
- **Error handling:** FastAPI 422 validation errors are converted to field-specific, user-friendly messages
- **Mock mode:** returns a realistic mock response with the same structure as the real backend
