# Cognizant - LLD doc

Created by: Greeshmitha Bingumalla
Created time: September 9, 2026 6:09 PM
Last edited by: Greeshmitha Bingumalla
Last updated time: September 9, 2026 6:33 PM

# 📕 LLD — Predictive Maintenance Agent with Anomaly Detection & Explainable AI

**Hackathon:** Cognizant Hackathon

**Duration:** 10–11 September 2026

**Team Size:** 8

**Document:** Low-Level Design (LLD)

**Version:** 1.0

---

# 1. Purpose of This Document

This document defines the detailed implementation design for the Predictive Maintenance system.

It specifies:

- Input and output data structures
- Data preprocessing
- Feature engineering
- Failure prediction pipeline
- Anomaly detection pipeline
- SHAP implementation
- Risk classification
- Recommendation logic
- Agent workflow
- Backend APIs
- Frontend interaction
- Model artifacts
- Module responsibilities
- Error handling
- Testing
- Team handoffs

The implementation should follow this document unless the team explicitly agrees to a change.

---

# 2. End-to-End Implementation Flow

```
                         USER
                           │
                           ▼
                   React Input Form
                           │
                           │ JSON
                           ▼
                    POST /api/v1/predict
                           │
                           ▼
                    FastAPI Validation
                           │
                           ▼
                    Preprocessing Layer
                           │
                           ▼
              Predictive Maintenance Agent
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
       Anomaly Detection        Failure Prediction
       Isolation Forest         Selected Classifier
               │                       │
               │                       ▼
               │                      SHAP
               │                       │
               └───────────┬───────────┘
                           ▼
                    Risk Assessment
                           │
                           ▼
                 Recommendation Engine
                           │
                           ▼
                    Final Response
                           │
                           ▼
                  React Dashboard
```

---

# 3. Input Data Specification

The model will initially use the following machine parameters.

| Feature | Type | Description |
| --- | --- | --- |
| `type` | Categorical | Machine/product quality variant |
| `air_temperature` | Numerical | Air temperature |
| `process_temperature` | Numerical | Process temperature |
| `rotational_speed` | Numerical | Rotational speed |
| `torque` | Numerical | Torque |
| `tool_wear` | Numerical | Tool wear |

Target during training:

```
machine_failure

0 → No failure
1 → Failure
```

The target is **not supplied by the user during prediction**.

---

# 4. Feature Engineering

The final preprocessing pipeline creates the following derived features.

## 4.1 Temperature Difference

```text
temperature_difference =
    process_temperature - air_temperature
```

Purpose:

Capture the difference between operating/process temperature and
ambient/air temperature.

```text
mechanical_power_W =
    torque × rotational_speed × (2π / 60)
```

This converts rotational speed from revolutions per minute to angular
velocity and produces a mechanical-power-related feature.

```text
overstrain_index =
    tool_wear × torque
```

This combines accumulated tool wear with mechanical load.
---

# 5. Features Excluded From Prediction

The following fields should not be used as ordinary predictive features:

```
UID
Product ID
```

because they are identifiers rather than meaningful machine operating parameters.

The failure-mode columns:

```
TWF
HDF
PWF
OSF
RNF
```

will also be excluded from the main prediction feature set because they describe specific failure modes and can introduce target leakage or information that would not necessarily be available at prediction time.

---

# 6. Preprocessing Pipeline

The same preprocessing used during training must be used during inference.

```
Raw Input
    ↓
Validation
    ↓
Feature Selection
    ↓
Feature Engineering
    ↓
Categorical Encoding
    ↓
Scaling where required
    ↓
Model Input
```

## Categorical processing

`type`:

```
One-Hot Encoding
```

Example conceptually:

```
type_L
type_M
type_H
```

---

## Numerical processing

Numerical features will be processed according to the requirements of the selected algorithms.

The preprocessing must be fitted **only on training data**.

At inference time, the saved preprocessing pipeline is reused.

---

# 7. Training/Test Strategy

Dataset:

```
10,000 records
```

Split:

```
80% → Training
20% → Test
```

The split must be **stratified by `Machine failure`**.

```
Dataset
   │
   ├──────────────┐
   ▼              ▼
Training        Test
  80%            20%
   │
   ▼
Stratified K-Fold CV
   │
   ▼
Model Selection
   │
   ▼
Final Model
   │
   ▼
Test Evaluation
```

The test set should not be repeatedly used for model tuning.

---

# 8. Failure Prediction Pipeline

## 8.1 Problem

Binary classification.

```
0 → No Failure
1 → Failure
```

---

## 8.2 Candidate Algorithms

The following classification algorithms were considered during model
selection:

1. Logistic Regression
2. Decision Tree
3. Random Forest
4. XGBoost

The final implemented classifier is **Random Forest**.

The final selected pipeline uses:

```text
Domain Feature Engineering
        ↓
One-Hot Encoding
        ↓
StandardScaler
        ↓
Random Forest
        ↓
class_weight="balanced"
```

# 9. Model Selection Criteria

Because failure is a minority class, accuracy alone is insufficient.

Metrics:

```
Precision
Recall
F1-score
ROC-AUC
PR-AUC
Confusion Matrix
```

### Priority

The team should pay particular attention to:

**Recall + F1 + PR-AUC**

because missing an actual machine failure can be more costly than generating a false alarm.

The final selection should consider both performance and generalization.

### Final Selection

The selected configuration was:

**One-Hot Encoding + StandardScaler + Balanced Random Forest**

This configuration provided the strongest overall balance across PR-AUC,
F1-score, precision and recall in the cross-validation comparison.

The final classification threshold was subsequently tuned to **0.49** using
out-of-fold validation.

---

# 10. Class Imbalance Handling

The dataset contains substantially fewer failure cases than normal cases.

Two imbalance-handling strategies were experimentally evaluated:

### 1. Class-balanced Random Forest

The Random Forest classifier uses:

```text
class_weight="balanced"
```

# 11. Failure Prediction Output

The model should produce:

```
failure_probability
```

and:

```
predicted_failure
```

Conceptually:

```
{
  "predicted_failure":true,
  "failure_probability":0.82
}
```

The exact model threshold can be tuned during validation.

The default classification threshold may begin at `0.5`, but the team should evaluate whether another threshold provides a better precision/recall trade-off.

---

# 12. Anomaly Detection Pipeline

## Objective

Determine whether the machine's current operating state is unusual.

### Algorithm

**Isolation Forest**

---

## Flow

```
Machine Parameters
       ↓
Anomaly Preprocessing
       ↓
Isolation Forest
       ↓
Anomaly Score
       ↓
Threshold
       ↓
Normal / Anomaly
```

---

# 13. Anomaly Training Strategy

The anomaly detector is unsupervised and does not require the `Machine failure` target for training.

The team should primarily model normal operating behavior.

A preferred implementation strategy is to train the detector using records representing **normal machine operation**, while keeping the failure label out of the anomaly model's feature input.

The exact training subset and contamination/threshold configuration should be validated experimentally.

---

# 14. Anomaly Output

Conceptually:

```
{
  "is_anomaly":true,
  "anomaly_score":-0.31
}
```

Important:

> Anomaly score interpretation depends on the selected implementation. The frontend should primarily rely on `is_anomaly` and use the score as supporting information.
> 

---

# 15. SHAP Implementation

SHAP explains the **failure prediction model**.

Flow:

```
Machine Input
      ↓
Failure Model
      ↓
Failure Probability
      ↓
SHAP Explainer
      ↓
Feature Contributions
      ↓
Top Contributors
```

Example internal result:

```
{
  "top_factors": [
    {
      "feature":"tool_wear",
      "contribution":0.24
    },
    {
      "feature":"torque",
      "contribution":0.18
    }
  ]
}
```

---

# 16. SHAP Interpretation

The system should distinguish between:

### Positive contribution

Feature pushes the prediction toward failure.

### Negative contribution

Feature pushes the prediction away from failure.

Therefore the UI can display:

```
Tool Wear       → increases failure risk
Torque          → increases failure risk
Temperature     → decreases failure risk
```

The exact wording should be generated from the SHAP contribution direction.

---

# 17. Risk Classification

Failure probability will be converted into a human-readable risk category.

Initial prototype:

```
0–30%     → LOW
30–70%    → MEDIUM
70–100%   → HIGH
```

These are **decision-support thresholds**, not industrial safety thresholds.

They can be adjusted after testing.

---

# 18. Recommendation Engine

The recommendation engine is rule-based.

### Inputs

```
Machine Parameters
Anomaly Status
Failure Probability
Risk Level
Top SHAP Contributors
```

### Processing

```
Inputs
  ↓
Rule Evaluation
  ↓
Matching Maintenance Rules
  ↓
Recommendations
```

---

# 19. Example Recommendation Rules

## Tool Wear

```
IF tool_wear is high
AND tool_wear is a major positive SHAP contributor

THEN
recommend tool inspection/replacement.
```

## Torque

```
IF torque is high
AND torque strongly contributes to failure prediction

THEN
recommend inspection of mechanical load and related components.
```

## Temperature

```
IF temperature-related features strongly contribute

THEN
recommend checking thermal/process conditions.
```

## Anomaly

```
IF anomaly = TRUE
AND risk = HIGH

THEN
recommend prompt inspection and monitoring.
```

These rules should be treated as prototype preventive-maintenance suggestions.

---

# 20. Agent Implementation

The `PredictiveMaintenanceAgent` is responsible for orchestration.

### Input

Validated machine parameters.

### Internal operations

```
1. Preprocess input
2. Run anomaly detector
3. Run failure prediction
4. Generate SHAP explanation
5. Determine risk
6. Generate recommendations
7. Combine outputs
```

### Output

One structured prediction result.

---

# 21. Agent Decision Logic

Conceptually:

```
                    INPUT
                      │
                      ▼
                 VALIDATE
                      │
                      ▼
                   AGENT
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       ANOMALY                FAILURE
       DETECTOR               MODEL
          │                       │
          │                       ▼
          │                      SHAP
          │                       │
          └───────────┬───────────┘
                      ▼
                RISK ASSESSMENT
                      │
                      ▼
              RECOMMENDATION RULES
                      │
                      ▼
                  RESPONSE
```

The agent is primarily an **orchestration layer**, while the individual models/tools perform the actual analytical work.

---

# 22. Backend API

## `POST /api/v1/predict`

### Purpose

Perform complete machine analysis.

### Request

```
{
  "type":"M",
  "air_temperature":298.5,
  "process_temperature":308.6,
  "rotational_speed":1550,
  "torque":42.3,
  "tool_wear":120
}
```

---

# 23. Request Validation

FastAPI/Pydantic will validate:

### `type`

Allowed:

```
L
M
H
```

### Numerical fields

Must:

- Exist.
- Be numeric.
- Be within reasonable accepted ranges.
- Not contain invalid values such as NaN/infinite values.

Exact domain ranges can be established from the dataset during implementation.

---

# 24. API Response

```
{
  "machine": {
    "type":"M"
  },
  "anomaly": {
    "is_anomaly":true,
    "score":-0.31
  },
  "failure_prediction": {
    "predicted_failure":true,
    "probability":0.82,
    "risk_level":"HIGH"
  },
  "explanation": {
    "top_factors": [
      {
        "feature":"tool_wear",
        "contribution":0.24,
        "direction":"increases_risk"
      },
      {
        "feature":"torque",
        "contribution":0.18,
        "direction":"increases_risk"
      }
    ]
  },
  "recommendations": ["Inspect tool condition and consider tool replacement.","Inspect mechanical load and related components."
  ]
}
```

---

# 25. API Status Codes

| Status | Meaning |
| --- | --- |
| `200` | Successful prediction |
| `400` | Invalid request |
| `422` | Validation error |
| `500` | Internal server error |

---

# 26. Health Check API

## `GET /api/v1/health`

Purpose:

Verify that the backend is running.

Example response:

```
{
  "status":"healthy"
}
```

---

# 27. Backend Processing Flow

```
HTTP Request
     ↓
Pydantic Validation
     ↓
Prediction Route
     ↓
PredictiveMaintenanceAgent
     ↓
Model Services
     ├── Anomaly Service
     ├── Prediction Service
     ├── SHAP Service
     └── Recommendation Service
     ↓
Response Schema
     ↓
JSON Response
```

---

# 28. Backend Module Responsibilities

```
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   └── routes.py
    │
    ├── schemas/
    │   └── prediction.py
    │
    ├── agent/
    │   └── predictive_agent.py
    │
    ├── services/
    │   ├── anomaly.py
    │   ├── prediction.py
    │   ├── shap_service.py
    │   └── recommendation.py
    │
    ├── models/
    │
    └── config.py
```

### Responsibilities

**routes.py**

Receives HTTP requests and returns responses.

**prediction.py**

Loads and executes the failure prediction pipeline.

**anomaly.py**

Loads and executes the anomaly detector.

**shap_service.py**

Generates model explanations.

**recommendation.py**

Evaluates recommendation rules.

**predictive_agent.py**

Coordinates all services.

---

# 29. Model Artifact Management

ML team provides:

```
models/
├── failure_pipeline.pkl
└── anomaly_pipeline.pkl
```

Potential additional files:

```
feature_schema.json
model_metadata.json
```

### `feature_schema.json`

Can document:

- Feature names
- Feature types
- Expected order
- Encoding information
- Model version

This helps Backend integrate safely.

---

# 30. Frontend Architecture

React will contain the following logical sections.

```
Dashboard
│
├── MachineInputForm
│
├── RiskSummary
│
├── AnomalyCard
│
├── FailurePredictionCard
│
├── SHAPChart
│
└── RecommendationPanel
```

---

# 31. Frontend Flow

```
User enters values
       ↓
Client-side validation
       ↓
Click "Analyze Machine"
       ↓
POST /api/v1/predict
       ↓
Loading state
       ↓
Receive response
       ↓
Update dashboard
```

---

# 32. Dashboard Output

The dashboard should clearly display:

### Machine status

```
LOW / MEDIUM / HIGH
```

### Failure probability

```
82%
```

### Anomaly

```
ANOMALY DETECTED
```

### Contributing factors

Visual SHAP representation.

### Recommendations

Readable maintenance suggestions.

---

# 33. Frontend Error States

The frontend should handle:

```
Invalid input
API unavailable
Prediction failure
Unexpected response
Loading state
```

Example:

> Unable to analyze machine. Please verify the input and try again.
> 

---

# 34. API Contract Between Teams

This is a **critical integration contract**.

Frontend assumes:

```
POST /api/v1/predict
```

and receives:

```
anomaly
failure_prediction
explanation
recommendations
```

Backend must maintain this structure once integration begins.

If the response structure needs to change, Backend must communicate the change to Frontend before implementation.

---

# 35. Mock Integration Strategy

Teams should not wait for each other.

Before the actual ML models are ready:

### Backend

Return mock prediction data.

### Frontend

Use the agreed response structure.

Example:

```
{
  "anomaly": {
    "is_anomaly":true,
    "score":-0.31
  },
  "failure_prediction": {
    "predicted_failure":true,
    "probability":0.82,
    "risk_level":"HIGH"
  },
  "explanation": {
    "top_factors": []
  },
  "recommendations": []
}
```

Then replace mock data with real model outputs.

---

# 36. Repository Structure

```
predictive-maintenance/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── agent/
│   │   ├── services/
│   │   └── models/
│   └── requirements.txt
│
├── ml/
│   ├── notebooks/
│   ├── src/
│   └── models/
│
├── data/
│
├── docs/
│   ├── HLD.md
│   └── LLD.md
│
└── README.md
```

---

# 37. Model-to-Backend Handoff

ML Team must provide:

```
✓ Final model
✓ Preprocessing pipeline
✓ Feature list
✓ Expected input format
✓ Output format
✓ Evaluation metrics
✓ Model version
✓ Sample prediction
```

Backend Team must verify the model locally before integration.

---

# 38. SHAP-to-Backend Handoff

Explainability Team must provide:

```
✓ SHAP integration
✓ Feature contribution format
✓ Positive/negative contribution interpretation
✓ Top-N contributor logic
✓ Sample output
```

Backend consumes this output rather than recreating SHAP logic.

---

# 39. Backend-to-Frontend Handoff

Backend provides:

```
✓ API endpoint
✓ Request schema
✓ Response schema
✓ Example JSON
✓ Error responses
✓ Local API URL
```

Frontend uses the same contract for integration.

---

# 40. Integration Order

To minimize integration problems:

```
STEP 1
Frontend ↔ Mock Backend
        ↓
STEP 2
Backend ↔ Mock ML
        ↓
STEP 3
Backend ↔ Actual ML
        ↓
STEP 4
SHAP integration
        ↓
STEP 5
Recommendation integration
        ↓
STEP 6
Complete Agent
        ↓
STEP 7
Frontend ↔ Complete Backend
        ↓
STEP 8
End-to-End Testing
```

---

# 41. Testing Strategy

## 41.1 Data Testing

Check:

- Missing values
- Invalid types
- Duplicate rows
- Unexpected categories
- Extreme values

---

## 41.2 Model Testing

Evaluate:

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Confusion matrix

---

## 41.3 API Testing

Test:

```
Valid request
Invalid request
Missing field
Invalid machine type
Negative/impossible values
Server failure
```

---

# 42. End-to-End Test Cases

### Test Case 1 — Normal Machine

```
Expected:
Anomaly = FALSE
Low failure risk
```

---

### Test Case 2 — High Failure Risk

```
Expected:
High failure probability
HIGH risk
Relevant SHAP factors
Recommendations
```

---

### Test Case 3 — Anomalous but Low Failure Risk

```
Expected:
Anomaly = TRUE
Failure probability may remain LOW/MEDIUM
```

This verifies that anomaly and failure prediction are not incorrectly treated as the same thing.

---

### Test Case 4 — Anomalous + High Risk

```
Expected:
Anomaly = TRUE
HIGH risk
Strong recommendations
```

---

### Test Case 5 — Invalid Input

```
Expected:
Validation error
No model execution
```

---

# 43. Logging

For the MVP, backend should log:

```
Request received
Prediction execution
Anomaly result
Failure prediction
Execution errors
Response generated
```

Do not log sensitive information unnecessarily.

---

# 44. Error Handling

If one analytical component fails, the backend should not silently return incorrect results.

Example:

```
SHAP failure
     ↓
Return prediction result
+
Explanation unavailable
```

if the architecture permits graceful degradation.

However, if the core failure prediction itself fails:

```
Return appropriate server error
```

rather than producing a fabricated result.

---

# 45. Configuration

Configuration should be separated from code where practical.

Examples:

```
Model paths
Risk thresholds
API settings
Recommendation thresholds
```

This allows the team to tune thresholds without changing core logic.

---

# 46. Security Considerations

For the MVP:

- Validate all API inputs.
- Restrict accepted feature values.
- Do not expose internal model files.
- Do not expose stack traces to users.
- Keep model execution server-side.
- Configure CORS appropriately for the deployed frontend.

Authentication is outside MVP scope.

---

# 47. Deployment Flow

High-level:

```
                  GitHub
                 /      \
                /        \
               ▼          ▼
          Frontend      Backend
             │             │
             ▼             ▼
          Hosting       Python Hosting
                           │
                           ▼
                     ML Model Files
```

The exact hosting provider will be selected during implementation based on available free-tier/runtime requirements.

---

# 48. Critical Integration Dependencies

| Dependency | Producer | Consumer | Deadline |
| --- | --- | --- | --- |
| Clean dataset | Data/ML | ML | Sep 10 AM |
| Feature set | ML | Backend/SHAP | Sep 10 PM |
| Failure model | ML | SHAP/Backend | Sep 10 PM |
| Anomaly model | ML | Backend | Sep 10 PM |
| SHAP output | Explainability | Backend | Sep 10 PM |
| Recommendation rules | Explainability | Backend | Sep 10 PM |
| API contract | Backend | Frontend | Sep 10 AM |
| Mock response | Backend | Frontend | Sep 10 |
| Real API | Backend | Frontend | Sep 11 AM |
| E2E system | All | Demo | Sep 11 PM |

---

# 49. Critical Blockers

## Blocker 1 — ML Model Delay

**Impact:** Backend + SHAP integration delayed.

**Mitigation:** Use first viable model and refine after integration.

---

## Blocker 2 — API Contract Changes

**Impact:** Frontend rework.

**Mitigation:** Freeze API schema on September 10.

---

## Blocker 3 — Model Artifact Problems

**Impact:** Backend prediction fails.

**Mitigation:** ML provides preprocessing pipeline + feature schema + model + sample input/output.

---

## Blocker 4 — SHAP Delay

**Impact:** Explainability missing.

**Mitigation:** Begin SHAP as soon as a viable classifier is available.

---

## Blocker 5 — Late Integration

**Impact:** Entire demo may fail.

**Mitigation:**

> First complete mocked E2E flow must work on September 10.
> 

---

# 50. Definition of Done

The project is considered complete when:

```
[✓] User can enter machine parameters
[✓] Frontend validates input
[✓] API receives request
[✓] Agent executes analysis
[✓] Anomaly detection works
[✓] Failure prediction works
[✓] SHAP explanation works
[✓] Risk is calculated
[✓] Recommendations are generated
[✓] API returns structured response
[✓] Frontend displays results
[✓] End-to-end flow tested
[✓] Application is demo-ready
```

---

# 51. Final Implementation Contract

The entire system can be reduced to this implementation contract:

```
INPUT
Machine Parameters
       │
       ▼
API
POST /api/v1/predict
       │
       ▼
AGENT
       │
       ├───────────────┐
       ▼               ▼
 ANOMALY            FAILURE
 DETECTION          PREDICTION
 Isolation Forest   Selected ML Model
       │               │
       │               ▼
       │              SHAP
       │               │
       └───────┬───────┘
               ▼
        RISK ASSESSMENT
               │
               ▼
       RECOMMENDATION
               │
               ▼
           RESPONSE
               │
               ▼
          DASHBOARD
```