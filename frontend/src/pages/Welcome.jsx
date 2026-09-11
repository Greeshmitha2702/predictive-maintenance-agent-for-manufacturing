import { Link } from "react-router-dom";

function Welcome() {
  return (
    <main className="welcome-page">
      <section className="welcome-hero">
        <p className="welcome-label">AI-POWERED MANUFACTURING</p>

        <h2>Predict. Detect. Prevent.</h2>

        <p className="welcome-description">
          An intelligent predictive maintenance system that analyzes machine
          operating conditions, detects abnormal behavior, and estimates
          potential failure risk.
        </p>

        <Link to="/dashboard" className="welcome-button">
          Analyze Machine
        </Link>
      </section>

      <section className="welcome-features">
        <div className="welcome-feature">
          <h3>Monitor</h3>
          <p>
            Analyze temperature, speed, torque, and tool wear parameters.
          </p>
        </div>

        <div className="welcome-feature">
          <h3>Predict</h3>
          <p>
            Estimate the probability of machine failure using machine learning.
          </p>
        </div>

        <div className="welcome-feature">
          <h3>Prevent</h3>
          <p>
            Identify potential risks early and support maintenance decisions.
          </p>
        </div>
      </section>
    </main>
  );
}

export default Welcome;