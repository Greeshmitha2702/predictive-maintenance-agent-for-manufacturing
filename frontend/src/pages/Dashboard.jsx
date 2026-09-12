import { useState } from "react";

import MachineInputForm from "../components/MachineInputForm";
import RiskSummary from "../components/RiskSummary";
import AnomalyCard from "../components/AnomalyCard";
import FailurePredictionCard from "../components/FailurePredictionCard";
import LoadingState from "../components/LoadingState";
import ErrorMessage from "../components/ErrorMessage";

function Dashboard({ predictionResult, setPredictionResult }) {
  // Stores loading status.
  const [loading, setLoading] = useState(false);

  // Stores error messages.
  const [error, setError] = useState("");

  // Stores whether the current result has been saved.
  const [saved, setSaved] = useState(false);

  // Receive the prediction result from the form.
  const handleAnalyze = (result) => {
    setPredictionResult(result);
    setSaved(false);
  };

  // Handle loading state.
  const handleLoading = (isLoading) => {
    setLoading(isLoading);

    if (isLoading) {
      setPredictionResult(null);
      setSaved(false);
      setError("");
    }
  };

  // Handle errors.
  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  // Save the current analysis in browser localStorage.
  const handleSave = () => {
  if (!predictionResult || saved) {
    return;
  }

    // Get previous saved analyses.
let history = [];

try {
  const savedHistory = localStorage.getItem("predictionHistory");
  const parsedHistory = savedHistory
    ? JSON.parse(savedHistory)
    : [];

  if (Array.isArray(parsedHistory)) {
    history = parsedHistory;
  }
} catch {
  history = [];
}

    // Add the current analysis to history.
    const newAnalysis = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      result: predictionResult,
    };

    history.push(newAnalysis);

    // Save updated history.
    localStorage.setItem(
      "predictionHistory",
      JSON.stringify(history)
    );

    setSaved(true);
  };

  // Clear the current prediction.
  const handleClear = () => {
    setPredictionResult(null);
    setSaved(false);
    setError("");
  };

  return (
    <main className="dashboard">

      {/* Dashboard heading */}
      <section className="dashboard-title">
        <p className="section-label">MACHINE MONITORING</p>

        <h2>Machine Health Dashboard</h2>

        <p>
          Enter the current operating parameters to analyze machine health,
          detect abnormal behavior, and estimate failure risk.
        </p>
      </section>


      {/* Machine input form */}
      <section className="machine-card">

        <div className="card-heading">
          <div>
            <h3>Machine Parameters</h3>

            <p className="machine-card-description">
              Enter the current values recorded from the machine.
            </p>
          </div>

          <span className="status-indicator">
            Ready for Analysis
          </span>
        </div>

        <MachineInputForm
          onAnalyze={handleAnalyze}
          onLoading={handleLoading}
          onError={handleError}
        />

      </section>


      {/* Loading message */}
      {loading && <LoadingState />}


      {/* Error message */}
      {!loading && <ErrorMessage message={error} />}


      {/* Prediction results */}
      {predictionResult && !loading && !error && (
        <section className="dashboard-results">

          <div className="results-heading">
            <div>
              <p className="section-label">ANALYSIS RESULT</p>

              <h3>Current Machine Status</h3>
            </div>

            <span className="result-status">
              Analysis Complete
            </span>
          </div>


          {/* Result cards */}
          <div className="results-grid">

            <RiskSummary
              failurePrediction={predictionResult.failure_prediction}
            />

            <AnomalyCard
              anomaly={predictionResult.anomaly}
            />

            <FailurePredictionCard
              failurePrediction={predictionResult.failure_prediction}
            />

          </div>


          {/* Save and Clear buttons */}
          <div className="result-actions">

            <button
              className="save-button"
              onClick={handleSave}
              disabled={saved}
            >
              {saved ? "Saved" : "Save Analysis"}
            </button>

            <button
              className="clear-button"
              onClick={handleClear}
            >
              Clear
            </button>

          </div>

        </section>
      )}

    </main>
  );
}

export default Dashboard;
