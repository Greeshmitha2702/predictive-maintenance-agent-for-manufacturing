# Claude Prompts — Predictive Maintenance Agent

## GLOBAL INSTRUCTION — INCLUDE THIS WITH EVERY PROMPT

> Work only on the requested phase. Use the existing repository and frozen architecture. Keep the implementation simple and hackathon-ready. Do not add unrequested features or redesign the architecture.
>
> **IMPORTANT:** Do NOT execute terminal commands, install packages, create environments, start servers, run tests, train models, or run scripts yourself. Instead, give me the exact commands I should run manually, explain what each command does, and wait for me to run them. Do not claim that a command was run unless I provide its output.
>
> When code is generated, show the files changed/created and the complete relevant code. Keep dependencies minimal.

---

# 0. REPOSITORY SETUP

## Phase 0 — Create Project Structure

### Prompt

> Set up the initial repository structure for our Predictive Maintenance Agent. Do not write application logic yet.
>
> Create:
>
> ```text
> predictive-maintenance/
> ├── frontend/
> ├── backend/
> │   ├── app/
> │   │   ├── api/
> │   │   ├── schemas/
> │   │   ├── agent/
> │   │   ├── services/
> │   │   └── models/
> │   └── requirements.txt
> ├── ml/
> │   ├── notebooks/
> │   ├── src/
> │   └── models/
> ├── data/
> ├── docs/
> │   ├── HLD.md
> │   └── LLD.md
> └── README.md
> ```
>
> Add only minimal placeholder files needed for Git to track empty directories.
>
> Do NOT install anything or run terminal commands. At the end, give me the Git commands for `git init`, first commit, adding the remote, and pushing to GitHub, but do not execute them.

---

# 1. MODEL TRAINING / ML

## ML-1 — Dataset Inspection & Cleaning

### Prompt

> Implement only dataset inspection and cleaning.
>
> Dataset: 10,000 machine records. Target: `Machine failure` (0/1). Candidate features: `Type`, `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]`.
>
> Exclude identifiers and do not use `TWF`, `HDF`, `PWF`, `OSF`, `RNF` as predictive features.
>
> Do:
> - load CSV,
> - inspect shape/types/missing values/duplicates/class distribution/statistics,
> - identify invalid values,
> - define features/target,
> - clean data without blindly removing meaningful operating outliers,
> - save a clean artifact if useful.
>
> Do not train models. Keep code concise and reproducible. At the end, list files changed and commands I should run manually.

---

## ML-2 — Feature Engineering & Preprocessing

### Prompt

> Implement feature engineering and preprocessing only.
>
> Use the agreed features. Exclude IDs and leakage-prone failure-mode columns. One-hot encode `Type`.
>
> Create/evaluate:
> - `temperature_difference = process_temperature - air_temperature`
> - optional mechanical-power-related feature from torque × rotational speed; retain only if experiments justify it.
>
> Build a reusable scikit-learn `Pipeline`/`ColumnTransformer`. Fit preprocessing only on training data and make it reusable for inference. Preserve recoverable feature names for SHAP.
>
> Do not train final models. Report final features, changed files, and manual run commands.

---

## ML-3 — Train 4 Failure Models

### Prompt

> Implement failure-model experimentation.
>
> Target: `Machine failure` binary classification.
>
> Train:
> 1. Logistic Regression
> 2. Decision Tree
> 3. Random Forest
> 4. XGBoost
>
> Use:
> - 80/20 stratified train/test split,
> - Stratified K-Fold CV on training data,
> - existing preprocessing pipeline,
> - class weights where supported,
> - fixed random seeds,
> - modest tuning only.
>
> Never tune using the test set. Produce comparable results for all four models.
>
> Do not execute commands. Give me the exact commands to run manually.

---

## ML-4 — Metrics & Model Selection

### Prompt

> Evaluate the four failure models using Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC and confusion matrix.
>
> Compare cross-validation results, select the best model with emphasis on Recall/F1/PR-AUC and generalization, then evaluate it once on the untouched test set.
>
> If class weighting is inadequate, briefly assess whether SMOTE or threshold tuning is justified. Never apply SMOTE to test data.
>
> Save the final model + preprocessing as a reusable inference artifact and save metrics/metadata.
>
> Return the model comparison table, final model, test metrics, artifact names and manual commands. Do not run anything yourself.

---

## ML-5 — Isolation Forest

### Prompt

> Implement anomaly detection using Isolation Forest.
>
> Requirements:
> - do not use `Machine failure` as an input,
> - use agreed machine operating features,
> - use appropriate preprocessing,
> - train using normal-operating data strategy,
> - output `is_anomaly` and anomaly score,
> - choose/document an initial threshold or contamination setting,
> - sanity-check detected anomalies,
> - do not equate anomaly with failure,
> - save a reusable anomaly pipeline.
>
> Known failure labels may be used only for external sanity checking, not training.
>
> Do not execute commands. Give me manual run commands and expected outputs.

---

## ML-6 — Package & Handoff

### Prompt

> Prepare the ML artifacts for backend integration.
>
> Provide:
> - final failure pipeline,
> - anomaly pipeline,
> - feature/input schema,
> - model metadata,
> - evaluation metrics,
> - sample input/output,
> - dependency/version requirements.
>
> Verify that the artifacts can be loaded in a fresh Python process and that preprocessing and SHAP feature names are recoverable.
>
> Do not execute commands. Give me verification commands to run manually and a concise handoff note for Backend.

---

# 2. BACKEND + AGENT

## BE-1 — FastAPI Foundation

### Prompt

> Implement the FastAPI foundation for the frozen architecture.
>
> Endpoints:
> - `GET /api/v1/health`
> - `POST /api/v1/predict`
>
> Prediction fields:
> `type`, `air_temperature`, `process_temperature`, `rotational_speed`, `torque`, `tool_wear`.
>
> Implement:
> - Pydantic request/response schemas,
> - validation,
> - HTTP error handling,
> - CORS,
> - temporary mock response for `/predict`.
>
> Do not integrate real ML yet. Do not run/install anything. Give me exact manual commands to install dependencies, start the server and test both endpoints.

---

## BE-2 — ML Integration

### Prompt

> Replace the mock ML layer with the actual model artifacts.
>
> Create separate services for:
> - failure prediction,
> - anomaly detection.
>
> Load artifacts at startup or through caching; never retrain in the API. Convert validated request data into the exact model input. Return failure probability/prediction and anomaly score/status.
>
> Keep model logic separate from routes and handle missing/corrupt artifacts clearly.
>
> Do not implement SHAP or recommendations yet. Do not execute commands; give me manual verification commands.

---

## BE-3 — Predictive Maintenance Agent

### Prompt

> Implement the `PredictiveMaintenanceAgent` orchestration layer.
>
> Workflow:
> 1. receive validated input,
> 2. run anomaly detection,
> 3. run failure prediction,
> 4. pass failure result to SHAP,
> 5. determine risk,
> 6. call recommendation engine,
> 7. build final response.
>
> The agent is a deterministic Python orchestrator, not an LLM agent. Anomaly and failure prediction are independent signals. Keep orchestration separate from services.
>
> Do not add LangGraph/CrewAI/LLM. Do not run commands. Give me manual commands for testing.

---

## BE-4 — SHAP

### Prompt

> Integrate SHAP with the selected failure model.
>
> Return:
> - top contributing features,
> - contribution values,
> - direction: increases/decreases failure risk.
>
> Recover readable feature names after preprocessing. Do not describe SHAP as proven physical causation. Handle explanation failure without fabricating results.
>
> Keep the existing API request unchanged. Do not run commands; give me manual test commands.

---

## BE-5 — Risk + Recommendations

### Prompt

> Implement configurable LOW/MEDIUM/HIGH risk classification from failure probability and the rule-based recommendation engine.
>
> Recommendation inputs:
> machine values, anomaly result, failure probability/risk and SHAP contributors.
>
> Add transparent rules for high tool wear, high torque, temperature-related contributors and anomalous + high-risk conditions.
>
> Recommendations are preventive suggestions, not guaranteed physical diagnoses or automated machine-control commands. Keep rules modular and deterministic.
>
> Do not execute commands. Give me manual tests.

---

## BE-6 — Backend Testing

### Prompt

> Test and stabilize the backend end to end.
>
> Test:
> - health,
> - valid prediction,
> - missing fields,
> - invalid machine type,
> - invalid numeric values,
> - model loading failure,
> - normal,
> - anomalous,
> - high-risk,
> - anomalous + high-risk.
>
> Verify:
> FastAPI → Agent → anomaly + failure prediction → SHAP → risk → recommendations → response.
>
> Do not change the API contract unless necessary. Do not execute tests or commands. Give me the exact commands and expected checks to run manually.

---

# 3. FRONTEND

## FE-1 — Dashboard Foundation

### Prompt

> Build the React dashboard for the frozen Predictive Maintenance architecture.
>
> Include:
> - machine input form,
> - Analyze button,
> - loading state,
> - error state,
> - result area.
>
> Inputs:
> Machine Type, Air Temperature, Process Temperature, Rotational Speed, Torque, Tool Wear.
>
> Use reusable components, client-side validation and an API service layer. Use mock response data initially.
>
> Do not add authentication or unnecessary pages. Do not execute commands. Give me manual setup/run commands.

---

## FE-2 — Risk + Anomaly Results

### Prompt

> Add result visualization for:
> - failure probability,
> - predicted failure,
> - LOW/MEDIUM/HIGH risk,
> - anomaly status,
> - anomaly score.
>
> Clearly distinguish anomaly from failure risk. Follow the agreed response schema. Do not hard-code real predictions.
>
> Do not execute commands. Give me manual verification commands.

---

## FE-3 — SHAP Visualization

### Prompt

> Add SHAP visualization showing top contributing features, contribution values and direction.
>
> Use backend SHAP data directly. Do not calculate SHAP in React. Label it as model explanation/contributing factors. Handle unavailable explanations.
>
> Do not execute commands. Give me manual run/test commands only.

---

## FE-4 — Recommendations

### Prompt

> Add the recommendation section using recommendations returned by the backend.
>
> Keep recommendations easy to scan and consistent with risk. Do not generate or modify recommendation text in the frontend.
>
> Do not execute commands.

---

## FE-5 — Real API Integration

### Prompt

> Replace mock data with `POST /api/v1/predict`.
>
> Send exactly the agreed request payload and parse the agreed response. Add loading, validation-error and network/server-error handling.
>
> Do not change the backend contract from the frontend. Do not execute commands. Give me manual run/test commands.

---

## FE-6 — Final Polish

### Prompt

> Polish the dashboard for the hackathon demo: visual hierarchy, readability, spacing, responsiveness, loading/errors, result clarity, SHAP and recommendations.
>
> Do not add new architecture/features. Keep the main flow obvious:
> Enter data → Analyze → Risk → Anomaly → Failure probability → Factors → Recommendations.
>
> Do not execute commands.

---

# 4. RECOMMENDATION ENGINE

## RE-1 — Define Rules

### Prompt

> Design the transparent rule set for the recommendation engine using machine values, anomaly result, failure probability/risk and SHAP contributors.
>
> Cover relevant factors such as tool wear, torque, rotational speed and temperature.
>
> Rules must be deterministic, inspectable and easy to modify. Recommendations are preventive suggestions, not guaranteed physical diagnoses or unsafe automated controls.
>
> Return the rule table first. Do not execute commands.

## RE-2 — Implement Rules

### Prompt

> Implement the approved recommendation rules as a standalone backend service.
>
> Requirements:
> - accept structured analysis results,
> - evaluate rules,
> - return zero or more recommendations,
> - avoid duplicates,
> - remain deterministic,
> - add unit tests for each rule.
>
> Do not execute commands. Give me manual test commands.

## RE-3 — Integrate Rules

### Prompt

> Integrate the recommendation service with the Predictive Maintenance Agent.
>
> Pass machine parameters, anomaly result, failure probability, risk and SHAP contributors. Ensure recommendations appear in `/api/v1/predict`.
>
> Test normal/low-risk, anomalous/low-risk, high-risk, high-tool-wear, high-torque and multiple-contributor cases.
>
> Do not execute commands. Give me manual test commands.

---

# 5. FINAL INTEGRATION

## INT-1 — End-to-End Integration

### Prompt

> Integrate the complete system:
>
> React → POST `/api/v1/predict` → FastAPI → Agent → Isolation Forest + Failure Model → SHAP → Risk → Recommendation Engine → JSON → React.
>
> Use real model artifacts and the frozen API contract. Test at least four meaningful scenarios. Fix integration bugs without redesigning the architecture.
>
> Do not execute commands. Give me exact manual commands and checks.

## INT-2 — Final Testing

### Prompt

> Perform a final test-plan review for input validation, ML, API, frontend and end-to-end behavior.
>
> E2E cases:
> - normal,
> - anomalous/low-risk,
> - high-risk,
> - anomalous/high-risk.
>
> Do not execute tests. Give me the exact commands/test steps I should run manually and a checklist of expected results.

## INT-3 — Demo Readiness

### Prompt

> Prepare the project for the final hackathon demo.
>
> Check startup instructions, model loading, health endpoint, prediction endpoint, dashboard rendering, error handling, README and reliable demo scenarios.
>
> Do not add new features. Do not execute commands. Give me the final manual verification checklist and commands.
