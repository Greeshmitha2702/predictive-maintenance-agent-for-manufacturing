# Predictive Maintenance Agent for Manufacturing

An AI-powered Predictive Maintenance solution for manufacturing equipment. This system predicts failure probabilities, detects anomalies, identifies root causes using Explainable AI (XAI), and provides prescriptive maintenance recommendations.

## Project Structure

```
predictive-maintenance/
├── frontend/          # Web dashboard / User interface
├── backend/           # FastAPI backend application
│   ├── app/
│   │   ├── api/       # API routes and endpoints
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── agent/     # Predictive maintenance agent logic
│   │   ├── services/  # Business logic & ML inference integration
│   │   └── models/    # Database / ORM models
│   └── requirements.txt
├── ml/                # Machine learning pipeline
│   ├── notebooks/     # Exploratory Data Analysis & experiments
│   ├── src/           # Preprocessing, training & evaluation scripts
│   └── models/        # Trained model artifacts & scalers
├── data/              # Dataset directory
├── docs/              # High-Level & Low-Level Design documentation
│   ├── HLD.md
│   └── LLD.md
└── README.md
```
