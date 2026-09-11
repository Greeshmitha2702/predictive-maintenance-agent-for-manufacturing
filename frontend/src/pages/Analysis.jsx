import SHAPExplanation from "../components/SHAPExplanation";
import RecommendationSection from "../components/RecommendationSection";

function Analysis({ predictionResult }) {
  return (
    <main className="dashboard">
      <div className="dashboard-title">
        <p className="section-label">DETAILED ANALYSIS</p>

        <h2>Machine Analysis</h2>
        <p>
          Detailed analysis of machine health, failure risk, and abnormal
          operating conditions.
        </p>
      </div>

      {!predictionResult && (
        <section className="machine-card">
          <h3>No Analysis Available</h3>

          <p className="machine-card-description">
            Run an analysis from the Dashboard to view detailed machine
            results.
          </p>
        </section>
      )}

      {predictionResult && (
        <section className="machine-card">
          <h3>Analysis Results</h3>

          <p className="machine-card-description">
            Detailed results for the latest machine analysis.
          </p>

          <div className="analysis-summary">
            <div>
              <p className="result-label">Failure Probability</p>
              <p className="analysis-value">
                {(predictionResult.failure_probability * 100).toFixed(0)}%
              </p>
            </div>

            <div>
              <p className="result-label">Failure Prediction</p>
              <p className="analysis-value">
                {predictionResult.failure_predicted
                  ? "Failure Predicted"
                  : "No Failure Predicted"}
              </p>
            </div>

            <div>
              <p className="result-label">Anomaly Status</p>
              <p className="analysis-value">
                {predictionResult.is_anomaly
                  ? "Anomaly Detected"
                  : "Normal"}
              </p>
            </div>
          </div>

          <SHAPExplanation
            explanations={predictionResult.explanation?.top_factors || []}
          />

          <RecommendationSection
            recommendations={predictionResult.recommendations || []}
          />
        </section>
      )}
    </main>
  );
}

export default Analysis;