function About() {
  return (
    <main className="dashboard">
      <div className="dashboard-title">
        <h2>System Overview</h2>

        <p>
          Understand how the Predictive Maintenance Agent analyzes machine
          health and identifies potential failures.
        </p>
      </div>

      <section className="overview-grid">
        <div className="overview-card">
          <h3>1. Machine Monitoring</h3>
          <p>
            The system collects important machine parameters such as
            temperature, rotational speed, torque, and tool wear.
          </p>
        </div>

        <div className="overview-card">
          <h3>2. Anomaly Detection</h3>
          <p>
            Anomaly detection identifies unusual machine behavior that may
            indicate abnormal operating conditions.
          </p>
        </div>

        <div className="overview-card">
          <h3>3. Failure Prediction</h3>
          <p>
            A machine learning model estimates the probability of machine
            failure based on the current operating parameters.
          </p>
        </div>

        <div className="overview-card">
          <h3>4. Explainability</h3>
          <p>
            The system identifies the factors that contribute most to the
            predicted failure risk.
          </p>
        </div>

        <div className="overview-card">
          <h3>5. Maintenance Recommendation</h3>
          <p>
            Based on the detected risk and contributing factors, the system
            provides actionable maintenance recommendations.
          </p>
        </div>

        <div className="overview-card">
          <h3>Technology Stack</h3>
          <p>
            React.js, FastAPI, Python, Pandas, NumPy, Scikit-learn, Isolation
            Forest, and machine learning models.
          </p>
        </div>
      </section>
    </main>
  );
}

export default About;