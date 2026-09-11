function FailurePredictionCard({ failurePrediction }) {
  // Don't display anything until prediction data exists.
  if (!failurePrediction) {
    return null;
  }

  const { predicted_failure } = failurePrediction;

  return (
    <article className="result-card">

      <div className="result-card-header">
        <div>
          <p className="result-card-label">ML PREDICTION</p>
          <h3>Failure Prediction</h3>
        </div>

        {/* Badge changes depending on the prediction */}
        <span
          className={`prediction-badge ${
            predicted_failure ? "failure" : "safe"
          }`}
        >
          {predicted_failure ? "FAILURE RISK" : "SAFE"}
        </span>
      </div>

      {/* Main prediction result */}
      <div className="prediction-status">
        {predicted_failure
          ? "Potential machine failure detected"
          : "No machine failure predicted"}
      </div>

      <p className="result-description">
        The machine learning model evaluates the current operating conditions
        and predicts whether a failure condition is likely.
      </p>

    </article>
  );
}

export default FailurePredictionCard;