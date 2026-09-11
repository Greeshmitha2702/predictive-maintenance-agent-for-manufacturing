function RiskSummary({ failurePrediction }) {
  if (!failurePrediction) {
    return null;
  }

  const { probability, predicted_failure, risk_level } =
    failurePrediction;

  return (
    <section className="result-card">
      <div className="result-card-header">
        <h3>Failure Risk</h3>
        <span className={`risk-badge ${risk_level.toLowerCase()}`}>
          {risk_level}
        </span>
      </div>

      <div className="risk-content">
        <div>
          <p className="result-label">Failure Probability</p>
          <p className="risk-probability">
            {(probability * 100).toFixed(0)}%
          </p>
        </div>

        <div>
          <p className="result-label">Predicted Failure</p>
          <p className="result-value">
            {predicted_failure ? "Yes" : "No"}
          </p>
        </div>
      </div>
    </section>
  );
}

export default RiskSummary;