import SHAPExplanation from "../components/SHAPExplanation";
import RecommendationSection from "../components/RecommendationSection";

function Analysis({ predictionResult }) {
  return (
    <main className="dashboard">

      {/* Page heading */}
      <div className="dashboard-title">
        <p className="section-label">DETAILED ANALYSIS</p>

        <h2>Machine Analysis</h2>

        <p>
          Detailed analysis of machine health, failure risk, and abnormal
          operating conditions.
        </p>
      </div>


      {/* Show this when no machine has been analyzed yet */}
      {!predictionResult && (
        <section className="machine-card">

          <h3>No Analysis Available</h3>

          <p className="machine-card-description">
            Run an analysis from the Dashboard to view detailed machine
            results.
          </p>

        </section>
      )}


      {/* Show prediction information when a result exists */}
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
                {(predictionResult.failure_prediction.probability * 100).toFixed(0)}%
              </p>
            </div>


            <div>
              <p className="result-label">Risk Level</p>

              <p className="analysis-value">
                {predictionResult.failure_prediction.risk_level}
              </p>
            </div>


            <div>
              <p className="result-label">Anomaly Status</p>

              <p className="analysis-value">
                {predictionResult.anomaly.is_anomaly
                  ? "Anomaly Detected"
                  : "Normal"}
              </p>
            </div>

          </div>


          <SHAPExplanation
  explanations={predictionResult.shap_explanations || []}
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