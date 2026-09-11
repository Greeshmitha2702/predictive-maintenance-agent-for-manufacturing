# Cognizant - HLD DOC

Created by: Greeshmitha Bingumalla
Created time: September 9, 2026 5:55 PM
Last edited by: Greeshmitha Bingumalla
Last updated time: September 9, 2026 6:03 PM

# 📘 HLD — Predictive Maintenance Agent with Anomaly Detection & Explainable AI

---

# 1. Project Title

## **Predictive Maintenance Agent with Anomaly Detection & Explainable AI**

**Hackathon:** Cognizant Hackathon

**Team Size:** 8

**Project Duration:** 10–11 September 2026

**Document:** High-Level Design (HLD)

---

# 2. Project Objective

Build an AI-powered predictive maintenance system that analyzes machine operating parameters to:

- Detect abnormal machine behavior.
- Predict the probability of machine failure.
- Identify the major factors contributing to the predicted failure.
- Provide potential root-cause indicators.
- Recommend preventive maintenance actions.
- Present all results through an interactive web dashboard.

The system will use a **Predictive Maintenance Agent** to coordinate anomaly detection, failure prediction, explainability, risk assessment, and recommendations.

---

# 3. Problem Statement

Traditional maintenance approaches often rely on:

- Fixed maintenance schedules.
- Manual inspection.
- Reactive maintenance after failure.

These approaches may result in unnecessary maintenance or unexpected machine downtime.

The proposed system uses historical machine data and machine-learning techniques to provide an intelligent, data-driven assessment of machine condition.

The system should answer:

> **"Given the current machine operating conditions, is the machine behaving abnormally, how likely is it to fail, what factors are contributing to that risk, and what maintenance action should be considered?"**
> 

---

# 4. Proposed Solution

The system consists of four major analytical capabilities:

### 1. Anomaly Detection

Detect whether the current machine operating conditions are unusual.

**Method:** Isolation Forest

---

### 2. Failure Prediction

Predict whether the machine is likely to experience failure.

**Problem type:** Binary classification

**Candidate models considered:**

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost

Random Forest was selected as the final failure prediction classifier through
experimental evaluation of preprocessing and class-imbalance strategies.

The final pipeline uses:

- Domain feature engineering
- One-Hot Encoding for `Type`
- StandardScaler for numerical features
- Random Forest with class balancing (`class_weight="balanced"`)

The final classification threshold was tuned to **0.49** using out-of-fold
validation data.

---

### 3. Explainable AI

Explain why the failure prediction model produced its result.

**Method:** SHAP

The system will identify the most influential features contributing to the prediction.

These should be interpreted as **potential contributing factors**, not guaranteed physical root causes.

---

### 4. Maintenance Recommendation

Generate preventive maintenance suggestions using:

- Machine operating values
- Anomaly result
- Failure probability
- Important SHAP contributors
- Predefined maintenance rules

**Approach:** Rule-based recommendation engine

---

# 5. Scope

## In Scope — MVP

- Machine parameter input.
- Data preprocessing.
- Feature engineering.
- Binary failure prediction.
- Anomaly detection.
- SHAP-based explanation.
- Risk classification.
- Rule-based recommendations.
- Predictive Maintenance Agent.
- REST API.
- React dashboard.
- End-to-end integration.
- Basic testing.
- Deployment/demo.

## Out of Scope — MVP

- User authentication.
- Complex database infrastructure.
- Real-time IoT sensor streaming.
- Automated maintenance execution.
- Multi-agent architecture.
- LLM-based autonomous decision making.
- Production-grade industrial control.
- Guaranteed physical root-cause diagnosis.

These can be considered future enhancements.

---

# 6. High-Level Architecture

```
                         ┌──────────────────────┐
                         │        USER          │
                         │ Machine Parameters   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Frontend     │
                         │ Input + Dashboard    │
                         └──────────┬───────────┘
                                    │
                              REST / JSON
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │      API Layer       │
                         └──────────┬───────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────┐
              │     PREDICTIVE MAINTENANCE AGENT       │
              │          Orchestration Layer            │
              └───────────────────┬─────────────────────┘
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
                    ▼             ▼              ▼
             ┌────────────┐ ┌────────────┐ ┌────────────┐
             │  Anomaly   │ │  Failure   │ │    SHAP    │
             │ Detection  │ │ Prediction │ │ Explainer  │
             │            │ │            │ │            │
             │ Isolation  │ │ Binary ML  │ │ Feature    │
             │  Forest    │ │ Classifier │ │Contribution│
             └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                   │              │              │
                   └──────────────┼──────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Recommendation      │
                       │ Engine               │
                       │ Rule Based           │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Final Assessment    │
                       │                     │
                       │ • Anomaly Status    │
                       │ • Failure Risk      │
                       │ • Risk Level        │
                       │ • Factors           │
                       │ • Recommendations   │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ React Dashboard     │
                       └─────────────────────┘
```

---

# 7. High-Level System Flow

```
User enters machine parameters
              ↓
Frontend validates input
              ↓
Request sent to FastAPI
              ↓
Predictive Maintenance Agent
              ↓
       ┌──────┴──────┐
       ↓             ↓
Anomaly Detection  Failure Prediction
       │             │
       │             ↓
       │            SHAP
       │             │
       └──────┬──────┘
              ↓
       Risk Assessment
              ↓
    Recommendation Engine
              ↓
       Final Assessment
              ↓
       Frontend Dashboard
```

---

# 8. Major System Components

| Component | Responsibility |
| --- | --- |
| React Frontend | Collect input and display results |
| FastAPI | Expose backend services |
| Predictive Maintenance Agent | Coordinate analytical components |
| Anomaly Detector | Detect unusual machine behavior |
| Failure Prediction Model | Predict failure probability |
| SHAP Explainer | Explain model predictions |
| Risk Assessment | Convert probability into risk category |
| Recommendation Engine | Generate preventive actions |
| ML Pipeline | Preprocess data and execute model inference |

---

# 9. AI/ML Architecture

## 9.1 Failure Prediction

### Input

Machine operating parameters:

- Machine/Product Type
- Air Temperature
- Process Temperature
- Rotational Speed
- Torque
- Tool Wear

### Target

```
Machine Failure

0 → No Failure
1 → Failure
```

### Approach


Replace with:

```markdown
Binary classification.

Candidate models considered:

```text
Logistic Regression
Decision Tree
Random Forest
XGBoost
```

The final model will be selected based on experimental evaluation.

---

# 10. Anomaly Detection

### Objective

Identify machine conditions that deviate from learned normal operating patterns.

### Primary algorithm

**Isolation Forest**

### Output

Conceptually:

```
Anomaly Status
+
Anomaly Score
```

Anomaly detection and failure prediction are **separate analytical tasks**.

An anomaly does not automatically mean that machine failure will occur.

---

# 11. Explainable AI

The selected failure prediction model will be explained using **SHAP**.

High-level flow:

```
Machine Parameters
       ↓
Failure Prediction
       ↓
Failure Probability
       ↓
SHAP
       ↓
Important Contributing Features
```

Example output:

```
Failure Probability: HIGH

Major contributing factors:
• Tool Wear
• Torque
• Rotational Speed
• Temperature Difference
```

The system will present these as **model contributing factors/potential root-cause indicators**.

---

# 12. Recommendation Engine

The recommendation engine converts analytical results into preventive maintenance suggestions.

### Inputs

```
Machine Parameters
       +
Anomaly Result
       +
Failure Probability
       +
SHAP Contributors
```

### Output

```
Preventive Maintenance Recommendations
```

Example:

```
High tool wear + strong SHAP contribution
        ↓
Inspect tool condition / consider replacement
```

The recommendations are intended as **prototype decision-support suggestions**, not certified engineering instructions.

---

# 13. Predictive Maintenance Agent

The Predictive Maintenance Agent acts as the orchestration layer.

### Responsibilities

- Receive the machine-analysis request.
- Coordinate anomaly detection.
- Coordinate failure prediction.
- Trigger SHAP explanation.
- Determine risk level.
- Invoke recommendation logic.
- Combine results into a single assessment.
- Return the final structured result.

### Conceptual architecture

```
                Predictive Maintenance Agent
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Anomaly Tool     Prediction Tool    SHAP Tool
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                  Recommendation Tool
                           │
                           ▼
                     Final Result
```

The project does **not require an LLM** for the core agent.

---

# 14. Data Processing Strategy

## Input Features

```
Type
Air Temperature
Process Temperature
Rotational Speed
Torque
Tool Wear
```

## Feature Engineering

The final failure prediction pipeline uses the following engineered features:

### 1. Temperature Difference

```text
temperature_difference
= Process Temperature − Air Temperature

mechanical_power_W
= Torque × Rotational speed × (2π / 60)

overstrain_index
= Tool wear × Torque
```

## Encoding

Categorical `Type`:

**One-Hot Encoding**

## Scaling

Scaling will be applied where required by the selected algorithms and maintained consistently between training and inference.

---

# 15. Data Leakage Strategy

The following failure-type columns will not be used as ordinary input features for the primary failure prediction model:

```
TWF
HDF
PWF
OSF
RNF
```

Reason:

These fields describe specific failure modes and could introduce information that would not necessarily be available before failure prediction.

Identifier fields such as:

```
UID
Product ID
```

will also be excluded unless experimentation establishes a valid predictive purpose.

---

# 16. Model Validation Strategy

Dataset will be divided into:

```
80% → Training
20% → Test
```

The split will be stratified based on the failure target.

Training data will use:

**Stratified K-Fold Cross-Validation**

for model comparison and tuning.

The test set will be used for final evaluation.

---

# 17. Class Imbalance Strategy

Machine failures represent a minority class.

Therefore, accuracy alone will not determine model quality.

Primary evaluation metrics:

- Recall
- Precision
- F1-score
- PR-AUC
- ROC-AUC
- Confusion Matrix

### Class Imbalance Strategy

Class imbalance was addressed through experimental comparison of:

- Class-balanced Random Forest
- SMOTE + Random Forest

The final selected approach uses:

**Random Forest with `class_weight="balanced"`**

SMOTE-based configurations were evaluated but were not selected because they
provided higher recall in some configurations while substantially reducing
precision, F1-score and PR-AUC.

---

# 18. Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React |
| Backend | Python + FastAPI |
| API Validation | Pydantic |
| Data Processing | Pandas, NumPy |
| ML | Scikit-learn |
| Advanced ML | XGBoost, if selected |
| Anomaly Detection | Isolation Forest |
| Explainability | SHAP |
| Imbalance Handling | Imbalanced-learn, if required |
| Visualization | React charting + ML visualization libraries |
| Version Control | Git + GitHub |
| Deployment | To be finalized during implementation |

---

# 19. Team Structure

With only **2 days**, the team will be divided into four functional groups.

## Team A — Data, ML & Anomaly Detection

**3 members**

Responsibilities:

- Dataset analysis
- Data cleaning
- EDA
- Feature engineering
- Preprocessing
- Failure prediction models
- Anomaly detection
- Model evaluation
- Model selection
- Model artifacts

---

## Team B — Explainability, Risk & Recommendations

**2 members**

Responsibilities:

- SHAP
- Feature contribution extraction
- Risk classification
- Recommendation rules
- Integration with ML outputs
- Agent logic support

---

## Team C — Backend & Agent Integration

**1 member**

Responsibilities:

- FastAPI
- API contracts
- Request/response validation
- Agent orchestration
- Model integration
- Backend testing

---

## Team D — Frontend

**2 members**

Responsibilities:

- React application
- Input form
- Dashboard
- Result visualization
- SHAP visualization
- Recommendation display
- API integration

---

# 20. Team Dependencies

```
                    DATA
                      │
                      ▼
                ML / ANOMALY
                 │         │
                 ▼         ▼
               SHAP      BACKEND
                 │         │
                 └────┬────┘
                      ▼
                   FRONTEND
                      │
                      ▼
                 INTEGRATION
```

### Dependency Table

| Team | Depends On | Main Handoff | Potentially Blocks |
| --- | --- | --- | --- |
| Data/ML | Dataset | Clean data + model artifacts | SHAP, Backend |
| SHAP/Recommendation | ML outputs | SHAP + recommendation logic | Backend |
| Backend | API contract + ML artifacts | Working API | Frontend integration |
| Frontend | API contract | Dashboard | Final integration |
| Integration | All teams | Complete system | Demo |

---

# 21. Parallel Development Strategy

Because the project has only two days, teams should **not wait for one another unnecessarily**.

### Backend

Start with mock ML responses.

### Frontend

Start using the agreed API contract and mock JSON.

### ML

Develop models independently.

### SHAP

Begin as soon as a viable failure model is available.

### Integration

Replace mock components with real implementations progressively.

This allows multiple teams to work simultaneously.

---

# 22. Major Blockers & Mitigation

| Blocker | Impact | Mitigation |
| --- | --- | --- |
| ML model not finalized | Backend/SHAP integration delayed | Use initial viable model and refine later |
| API contract changes | Frontend integration breaks | Freeze API contract on Day 1 |
| Model artifact incompatible with backend | Prediction fails | ML provides model + preprocessing + feature schema |
| SHAP integration delay | Explainability unavailable | Start SHAP immediately after first viable model |
| Late integration | Demo failure risk | Perform first E2E integration on Sep 10 |
| Frontend waiting for backend | UI development delayed | Use mock API responses |
| Recommendation rules incomplete | Final result incomplete | Define basic rules alongside SHAP development |
| Deployment issues | Demo unavailable | Maintain a local working version as backup |

---

# 23. Two-Day Development Timeline

## 📅 September 10 — Foundation & Component Completion

### Morning

**Data / ML / Anomaly**

- Dataset cleaning
- EDA
- Feature selection
- Feature engineering
- Preprocessing
- Baseline models
- Isolation Forest

**Backend**

- FastAPI setup
- API contract
- Agent skeleton

**Frontend**

- React setup
- Input form
- Dashboard skeleton

### Afternoon

**ML**

- Model comparison
- Cross-validation
- Class imbalance handling
- Select best viable model
- Finalize anomaly detector

**Explainability**

- SHAP integration
- Extract top contributing factors
- Initial recommendation rules

**Backend**

- Integrate ML outputs
- Agent workflow

**Frontend**

- Result dashboard
- Mock API integration

### 🔥 EOD Sep 10 Deliverables

- [ ]  Cleaned dataset
- [ ]  EDA completed
- [ ]  Feature set finalized
- [ ]  Preprocessing pipeline ready
- [ ]  Failure prediction model selected
- [ ]  Anomaly detector working
- [ ]  Model evaluation metrics available
- [ ]  SHAP working
- [ ]  Recommendation rules available
- [ ]  API contract frozen
- [ ]  FastAPI skeleton working
- [ ]  Agent skeleton working
- [ ]  React dashboard skeleton working
- [ ]  Mock end-to-end flow working

### **Day 1 Success Criteria**

> Every major component exists independently, and a mocked end-to-end flow can run from frontend → backend → agent → result → frontend.
> 

---

# 24. September 11 — Integration, Testing & Demo

### Morning

- Integrate final ML model.
- Integrate anomaly detector.
- Integrate SHAP.
- Integrate recommendation engine.
- Complete agent workflow.
- Connect frontend to real backend.

### Afternoon

- End-to-end testing.
- UI improvements.
- Error handling.
- Visualization improvements.
- Deployment.
- HLD/LLD completion.
- README.
- Presentation.
- Demo preparation.

### 🔥 EOD Sep 11 Deliverables

- [ ]  Complete working application
- [ ]  Failure prediction
- [ ]  Anomaly detection
- [ ]  SHAP explanation
- [ ]  Risk classification
- [ ]  Recommendations
- [ ]  Predictive Maintenance Agent
- [ ]  React dashboard
- [ ]  FastAPI backend
- [ ]  End-to-end integration
- [ ]  Testing completed
- [ ]  Deployment/demo environment
- [ ]  HLD completed
- [ ]  LLD completed
- [ ]  README completed
- [ ]  Presentation completed
- [ ]  Demo ready

### **Day 2 Success Criteria**

> A judge can enter machine parameters, click **Analyze**, and receive anomaly status, failure probability, risk level, contributing factors, and maintenance recommendations through a complete working interface.
> 

---

# 25. Deliverables & Ownership

| Deliverable | Owner | Deadline |
| --- | --- | --- |
| Clean Dataset | Data/ML | Sep 10 AM |
| EDA | Data/ML | Sep 10 AM |
| Feature Set | Data/ML | Sep 10 PM |
| Failure Model | ML | Sep 10 PM |
| Anomaly Model | ML | Sep 10 PM |
| Model Metrics | ML | Sep 10 PM |
| SHAP | Explainability | Sep 10 PM |
| Recommendation Rules | Explainability | Sep 10 PM |
| API Contract | Backend | Sep 10 AM |
| Agent Skeleton | Backend | Sep 10 PM |
| Frontend Skeleton | Frontend | Sep 10 PM |
| API Integration | Backend + Frontend | Sep 11 AM |
| E2E Integration | All | Sep 11 AM |
| Testing | All | Sep 11 PM |
| HLD | Documentation | Sep 11 |
| LLD | Documentation | Sep 11 |
| Presentation | All | Sep 11 |
| Demo | All | Sep 11 |

---

# 26. MVP Definition

The project will be considered **MVP-complete** when the following flow works:

```
User
 ↓
Enters machine parameters
 ↓
React
 ↓
FastAPI
 ↓
Predictive Maintenance Agent
 ↓
┌─────────────────────────────┐
│ Anomaly Detection           │
│ Failure Prediction          │
│ SHAP                        │
│ Risk Assessment             │
│ Recommendation              │
└─────────────────────────────┘
 ↓
Final Result
 ↓
React Dashboard
```

The result must contain:

```
✓ Anomaly status
✓ Failure probability
✓ Risk level
✓ Top contributing factors
✓ Preventive recommendations
```

---

# 27. Future Enhancements

The following are intentionally excluded from the two-day MVP but could be added later:

- Real-time IoT sensor integration.
- Historical prediction storage.
- Maintenance history.
- Machine-level monitoring.
- LLM-generated maintenance reports.
- LangGraph-based agent workflow.
- Advanced anomaly detection models.
- Automated alerting.
- User authentication.
- Role-based access.
- Database integration.
- Model monitoring and retraining.
- Integration with enterprise maintenance systems.

---

# 28. Key Technical Decisions

| Decision | Selected Approach | Reason |
| --- | --- | --- |
| Agent | Custom Python orchestrator | Simple and fast |
| Anomaly Detection | Isolation Forest | Designed for unsupervised anomaly detection |
| Failure Prediction | Binary Classification | Target is binary |
| Classifier | Balanced Random Forest | Selected through experimental pipeline comparison |
| Explainability | SHAP | Feature-level model explanation |
| Recommendation | Rule-based | Reliable and fast for MVP |
| Encoding | One-Hot | Avoid artificial ordering |
| Scaling | StandardScaler | Selected experimental configuration |
| Validation | Stratified K-Fold | Handles imbalanced target |
| Data Split | 80/20 stratified | Reliable final evaluation |
| Database | Not required | Not needed for MVP |
| LLM | Not required | Adds complexity without being essential |
| Architecture | Single-agent orchestration | Appropriate for 2-day implementation |
| API | REST | Simple frontend/backend integration |