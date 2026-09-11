import { useState } from "react";

function History() {
  // Read saved analyses from localStorage.
  const [history, setHistory] = useState(
    JSON.parse(localStorage.getItem("predictionHistory")) || []
  );

  // Delete all saved history.
  const clearHistory = () => {
    localStorage.removeItem("predictionHistory");
    setHistory([]);
  };

  return (
    <main className="dashboard">

      {/* Page heading */}
      <div className="dashboard-title">
        <p className="section-label">SAVED ANALYSES</p>

        <h2>Prediction History</h2>

        <p>
          View previously saved machine analysis results.
        </p>
      </div>


      {/* Show message when there is no history */}
      {history.length === 0 && (
        <section className="machine-card">
          <h3>No Saved Analyses</h3>

          <p className="machine-card-description">
            Save an analysis from the Dashboard to see it here.
          </p>
        </section>
      )}


      {/* Display saved analyses */}
      {history.length > 0 && (
        <section className="history-list">

          {history.map((item) => (
            <div className="history-card" key={item.id}>

              <div>
                <p className="history-date">
                  {item.date}
                </p>

                <h3>
                  Machine Type: {item.result.machine.type}
                </h3>
              </div>


              <div className="history-details">

                <div>
                  <span>Failure Probability</span>

                  <strong>
                    {(item.result.failure_prediction.probability * 100).toFixed(0)}%
                  </strong>
                </div>


                <div>
                  <span>Risk Level</span>

                  <strong>
                    {item.result.failure_prediction.risk_level}
                  </strong>
                </div>


                <div>
                  <span>Anomaly</span>

                  <strong>
                    {item.result.anomaly.is_anomaly
                      ? "Detected"
                      : "Normal"}
                  </strong>
                </div>

              </div>

            </div>
          ))}

        </section>
      )}


      {/* Clear entire history */}
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