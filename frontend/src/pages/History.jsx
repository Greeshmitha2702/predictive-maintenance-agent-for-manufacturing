import { useState } from "react";

function History() {
  // Safely read saved analyses from localStorage.
  const [history, setHistory] = useState(() => {
    try {
      const savedHistory = localStorage.getItem("predictionHistory");
      const parsedHistory = savedHistory ? JSON.parse(savedHistory) : [];

      return Array.isArray(parsedHistory) ? parsedHistory : [];
    } catch {
      return [];
    }
  });

  // Delete all saved history.
  const clearHistory = () => {
    localStorage.removeItem("predictionHistory");
    setHistory([]);
  };

  return (
    <main className="dashboard">

      {/* =====================================================
          PAGE HEADING
          ===================================================== */}
      <div className="dashboard-title">
        <p className="section-label">SAVED ANALYSES</p>

        <h2>Prediction History</h2>

        <p>
          View previously saved machine analysis results.
        </p>
      </div>


      {/* =====================================================
          NO HISTORY
          ===================================================== */}
      {history.length === 0 && (
        <section className="machine-card">
          <h3>No Saved Analyses</h3>

          <p className="machine-card-description">
            Save an analysis from the Dashboard to see it here.
          </p>
        </section>
      )}


      {/* =====================================================
          SAVED ANALYSES
          ===================================================== */}
      {history.length > 0 && (
        <section className="history-list">

          {history.map((item) => {
            const result = item.result || {};

            return (
              <div
                className="history-card"
                key={item.id}
              >

                {/* =================================================
                    MACHINE INFORMATION
                    ================================================= */}
                <div>
                  <p className="history-date">
                    {item.date}
                  </p>

                  <h3>
                    Machine ID:{" "}
                    {result.machine_id || "Not specified"}
                  </h3>

                  <p className="history-machine-type">
                    Machine Type:{" "}
                    {result.machine_type ||
                      result.type ||
                      "Not specified"}
                  </p>
                </div>


                {/* =================================================
                    ANALYSIS DETAILS
                    ================================================= */}
                <div className="history-details">

                  {/* Failure Probability */}
                  <div>
                    <span>Failure Probability</span>

                    <strong>
                      {typeof result.failure_probability === "number"
                        ? `${(
                            result.failure_probability * 100
                          ).toFixed(0)}%`
                        : "N/A"}
                    </strong>
                  </div>


                  {/* Failure Prediction */}
                  <div>
                    <span>Failure Prediction</span>

                    <strong>
                      {result.failure_predicted
                        ? "Failure Predicted"
                        : "No Failure Predicted"}
                    </strong>
                  </div>


                  {/* Anomaly */}
                  <div>
                    <span>Anomaly</span>

                    <strong>
                      {result.is_anomaly
                        ? "Detected"
                        : "Normal"}
                    </strong>
                  </div>

                </div>


                {/* =================================================
                    EXTRA DETAILS
                    ================================================= */}
                <div className="history-details">

                  {/* Anomaly Score */}
                  {result.anomaly_score !== undefined && (
                    <div>
                      <span>Anomaly Score</span>

                      <strong>
                        {Number(result.anomaly_score).toFixed(4)}
                      </strong>
                    </div>
                  )}


                  {/* Model Version */}
                  {result.model_version && (
                    <div>
                      <span>Model</span>

                      <strong>
                        {result.model_version}
                      </strong>
                    </div>
                  )}

                </div>

              </div>
            );
          })}

        </section>
      )}


      {/* =====================================================
          CLEAR HISTORY
          ===================================================== */}
      {history.length > 0 && (
        <button
          className="clear-history-button"
          onClick={clearHistory}
        >
          Clear History
        </button>
      )}

    </main>
  );
}

export default History;