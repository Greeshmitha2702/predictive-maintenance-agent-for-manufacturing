import { useNavigate } from "react-router-dom";

function Welcome() {
  const navigate = useNavigate();

  return (
    <main className="welcome-page">

      {/* =====================================================
          HERO SECTION
          ===================================================== */}

      <section className="welcome-hero">

        <div className="hero-content">

          <div className="hero-badge">
            <span className="status-dot"></span>
            AI-POWERED MANUFACTURING
          </div>

          <p className="hero-eyebrow">
            PREDICTIVE MAINTENANCE INTELLIGENCE
          </p>

          <h2>
            Predictive
            <br />
            Maintenance
            <span> Intelligence.</span>
          </h2>

          <p className="hero-description">
            Analyze machine operating conditions, detect abnormal behavior,
            estimate failure risk, and support proactive maintenance
            decisions.
          </p>

          <div className="hero-actions">

            <button
              className="primary-hero-button"
              onClick={() => navigate("/dashboard")}
            >
              Analyze Machine
              <span>→</span>
            </button>

            <button
              className="secondary-hero-button"
              onClick={() => navigate("/about")}
            >
              View System
            </button>

          </div>

          <div className="hero-note">
            <span>●</span>
            Decision-support system for machine health monitoring
          </div>

        </div>


        {/* =====================================================
            MACHINE INTELLIGENCE PANEL
            ===================================================== */}

        <div className="machine-intelligence-panel">

          <div className="panel-top">

            <div>
              <p className="panel-label">
                MACHINE HEALTH
              </p>

              <h3>
                Intelligence Center
              </h3>
            </div>

            <div className="ready-badge">
              <span></span>
              READY
            </div>

          </div>


          <div className="health-display">

            <div className="health-ring">
              <div className="health-ring-inner">
                <strong>AI</strong>
                <span>ACTIVE</span>
              </div>
            </div>

            <div className="health-info">
              <p>System Status</p>

              <h4>Operational</h4>

              <span>
                Ready for machine analysis
              </span>
            </div>

          </div>


          <div className="panel-divider"></div>


          <div className="monitoring-list">

            <div className="monitoring-item">
              <div>
                <span className="item-dot"></span>
                Machine Monitoring
              </div>

              <strong>Active</strong>
            </div>


            <div className="monitoring-item">
              <div>
                <span className="item-dot"></span>
                Anomaly Detection
              </div>

              <strong>Enabled</strong>
            </div>


            <div className="monitoring-item">
              <div>
                <span className="item-dot"></span>
                Failure Prediction
              </div>

              <strong>Enabled</strong>
            </div>


            <div className="monitoring-item">
              <div>
                <span className="item-dot"></span>
                Decision Support
              </div>

              <strong>Ready</strong>
            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          HOW IT WORKS
          ===================================================== */}

      <section className="capability-section">

        <div className="capability-heading">

          <div>

            <p className="section-label">
              HOW IT WORKS
            </p>

            <h3>
              From machine data to
              <span> maintenance decisions</span>
            </h3>

          </div>

          <p>
            The system transforms current machine operating conditions into
            actionable predictive maintenance insights.
          </p>

        </div>


        <div className="capability-grid">

          <div className="capability-card">

            <span className="capability-number">
              01
            </span>

            <h4>
              Monitor
            </h4>

            <p>
              Analyze temperature, rotational speed, torque, and tool wear
              from current machine conditions.
            </p>

          </div>


          <div className="capability-card">

            <span className="capability-number">
              02
            </span>

            <h4>
              Detect
            </h4>

            <p>
              Identify unusual operating behavior that may indicate abnormal
              machine conditions.
            </p>

          </div>


          <div className="capability-card">

            <span className="capability-number">
              03
            </span>

            <h4>
              Predict
            </h4>

            <p>
              Estimate machine failure probability using predictive machine
              learning.
            </p>

          </div>


          <div className="capability-card">

            <span className="capability-number">
              04
            </span>

            <h4>
              Prevent
            </h4>

            <p>
              Explain risk factors and support timely maintenance
              intervention.
            </p>

          </div>

        </div>

      </section>


    

      {/* Why Predictive Maintenance */}
<section className="why-maintenance">

  <div className="why-maintenance-heading">

    <div>
      <p className="section-label">
        WHY PREDICTIVE MAINTENANCE
      </p>

      <h3>
        Make maintenance decisions
        <span> before failure happens.</span>
      </h3>
    </div>

    <p>
      The system uses current machine operating conditions to identify
      abnormal behavior, estimate failure risk, and support proactive
      maintenance decisions.
    </p>

  </div>


  <div className="why-maintenance-cards">

    <div className="why-maintenance-card">

      <span className="why-number">01</span>

      <h4>
        Reduce Unplanned Downtime
      </h4>

      <p>
        Identify machines showing abnormal behavior or elevated failure
        risk before unexpected breakdowns occur.
      </p>

    </div>


    <div className="why-maintenance-card">

      <span className="why-number">02</span>

      <h4>
        Understand Machine Risk
      </h4>

      <p>
        View failure probability and the operating factors contributing
        to the machine's current risk level.
      </p>

    </div>


    <div className="why-maintenance-card">

      <span className="why-number">03</span>

      <h4>
        Support Proactive Maintenance
      </h4>

      <p>
        Convert machine analysis into clear maintenance insights that
        help teams decide when intervention may be required.
      </p>

    </div>

  </div>

</section>

    </main>
  );
}

export default Welcome;