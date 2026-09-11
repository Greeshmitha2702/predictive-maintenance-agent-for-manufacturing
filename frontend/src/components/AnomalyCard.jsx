function AnomalyCard({ anomaly }) {
  if (!anomaly) {
    return null;
  }

  return (
    <section className="result-card">
      <div className="result-card-header">
        <h3>Anomaly Detection</h3>

        <span
          className={`anomaly-badge ${
            anomaly.is_anomaly ? "anomaly" : "normal"
          }`}
        >
          {anomaly.is_anomaly ? "ANOMALY DETECTED" : "NORMAL"}
        </span>
      </div>

      <div className="anomaly-content">
        <div>
          <p className="result-label">Status</p>

          <p className="result-value">
            {anomaly.is_anomaly
              ? "Unusual machine behavior detected"
              : "Machine behavior is normal"}
          </p>
        </div>

        <div>
          <p className="result-label">Anomaly Score</p>

          <p className="result-value">
            {anomaly.score}
          </p>
        </div>
      </div>
    </section>
  );
}

export default AnomalyCard;