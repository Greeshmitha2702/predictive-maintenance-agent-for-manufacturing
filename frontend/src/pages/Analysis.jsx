import SHAPExplanation from "../components/SHAPExplanation";
import RecommendationSection from "../components/RecommendationSection";

function Analysis({ predictionResult }) {
  return (
    <main className="dashboard">

      {/* =====================================================
          PAGE TITLE
          ===================================================== */}
      <div className="dashboard-title">
        <p className="section-label">DETAILED ANALYSIS</p>

        <h2>Machine Analysis</h2>

        <p>
          Detailed analysis of machine health, failure risk, and abnormal
          operating conditions.
        </p>
      </div>


      {/* =====================================================
          NO ANALYSIS
          ===================================================== */}
      {!predictionResult && (
        <section className="machine-card">
          <h3>No Analysis Available</h3>

          <p className="machine-card-description">
            Run an analysis from the Dashboard to view detailed machine
            results.
          </p>
        </section>
      )}


      {/* =====================================================
          ANALYSIS RESULTS
          ===================================================== */}
      {predictionResult && (
        <section className="machine-card">

          <h3>Analysis Results</h3>

          <p className="machine-card-description">
            Detailed results for the latest machine analysis.
          </p>


          {/* =================================================
              MACHINE INFORMATION
              ================================================= */}
          <div className="machine-info-row">

            <div>
              <p className="result-label">Machine ID</p>

              <p className="analysis-value">
                {predictionResult.machine_id || "Not specified"}
              </p>
            </div>

            <div>
              <p className="result-label">Machine Type</p>

              <p className="analysis-value">
                {predictionResult.machine_type ||
                  predictionResult.type ||
                  "Not specified"}
              </p>
            </div>

          </div>


          {/* =================================================
              PREDICTION SUMMARY
              ================================================= */}
          <div className="analysis-summary">

            {/* Failure Probability */}
            <div>
              <p className="result-label">
                Failure Probability
              </p>

              <p className="analysis-value">
                {(predictionResult.failure_probability * 100).toFixed(0)}%
              </p>
            </div>


            {/* Failure Prediction */}
            <div>
              <p className="result-label">
                Failure Prediction
              </p>

              <p className="analysis-value">
                {predictionResult.failure_predicted
                  ? "Failure Predicted"
                  : "No Failure Predicted"}
              </p>
            </div>


            {/* Anomaly Status */}
            <div>
              <p className="result-label">
                Anomaly Status
              </p>

              <p className="analysis-value">
                {predictionResult.is_anomaly
                  ? "Anomaly Detected"
                  : "Normal"}
              </p>
            </div>

          </div>


          {/* =================================================
              ANOMALY SCORE
              ================================================= */}
          {predictionResult.anomaly_score !== undefined && (
            <div className="analysis-extra">

              <p className="result-label">
                Anomaly Score
              </p>

              <p className="analysis-value">
                {Number(predictionResult.anomaly_score).toFixed(4)}
              </p>

            </div>
          )}


          {/* =================================================
              MODEL VERSION
              ================================================= */}
          {predictionResult.model_version && (
            <div className="analysis-extra">

              <p className="result-label">
                Model
              </p>

              <p className="analysis-value">
                {predictionResult.model_version}
              </p>

            </div>
          )}


          {/* =================================================
              SHAP EXPLANATION
              ================================================= */}
          <SHAPExplanation
            explanations={
              predictionResult.explanation?.top_factors || []
            }
          />


          {/* =================================================
              MAINTENANCE RECOMMENDATIONS
              ================================================= */}
          <RecommendationSection
            recommendations={
              predictionResult.recommendations?.recommendations || []
            }

            urgency={
              predictionResult.recommendations?.urgency
            }

            rootCauseIndicators={
              predictionResult.recommendations?.root_cause_indicators || []
            }
          />

        </section>
      )}

    </main>
  );
}

export default Analysis;