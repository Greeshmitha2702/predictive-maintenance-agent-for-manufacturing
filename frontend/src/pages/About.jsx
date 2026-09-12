function About() {
  return (
    <main className="dashboard">
      <div className="dashboard-title">
        <h2>System Overview</h2>

        <p>
          The Predictive Maintenance Agent analyzes machine operating
          conditions to detect abnormal behavior, estimate failure risk,
          explain contributing factors, and support timely maintenance
          decisions.
        </p>
      </div>

      <section className="overview-grid">
        <div className="overview-card">
          <h3>1. Machine Monitoring</h3>
          <p>
            The system analyzes key operating parameters such as air
            temperature, process temperature, rotational speed, torque,
            and tool wear to assess the current condition of the machine.
          </p>
        </div>

        <div className="overview-card">
          <h3>2. Anomaly Detection</h3>
          <p>
            The system identifies operating conditions that differ
            significantly from learned normal machine behavior, helping
            highlight potentially abnormal conditions.
          </p>
        </div>

        <div className="overview-card">
          <h3>3. Failure Risk Prediction</h3>
          <p>
            A machine learning model evaluates the current operating
            conditions and estimates the probability of machine failure.
          </p>
        </div>

        <div className="overview-card">
          <h3>4. Explainable Analysis</h3>
          <p>
            The system highlights the operating factors that contribute
            most to the predicted failure risk, making the analysis easier
            to understand and interpret.
          </p>
        </div>

        <div className="overview-card">
          <h3>5. Risk Assessment</h3>
          <p>
            The predicted failure probability is translated into a clear
            risk assessment, helping users quickly understand the current
            level of machine risk.
          </p>
        </div>

        <div className="overview-card">
          <h3>6. Maintenance Recommendations</h3>
          <p>
            Based on the identified risk and contributing factors, the
            system provides actionable maintenance recommendations to
            support timely intervention.
          </p>
        </div>
      </section>
    </main>
  );
}

export default About;