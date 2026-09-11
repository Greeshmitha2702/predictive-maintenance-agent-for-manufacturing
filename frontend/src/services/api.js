const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function predictMachine(machineData) {
  if (USE_MOCK_API) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          failure_probability: 0.82,
          failure_predicted: true,
          is_anomaly: true,
          anomaly_score: -0.31,
          model_version: "mock-v1",
          explanation: {
            top_factors: [
              {
                feature: "Torque [Nm]",
                contribution: 0.1199,
                direction: "increases_failure_risk",
              },
              {
                feature: "Tool wear [min]",
                contribution: -0.0821,
                direction: "decreases_failure_risk",
              },
            ],
            disclaimer: "Mock explanation for local frontend development.",
          },
          recommendations: [
            "Inspect tool condition and consider tool replacement.",
          ],
        });
      }, 1000);
    });
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(machineData),
  });

  if (!response.ok) {
    throw new Error("Prediction request failed.");
  }

  return response.json();
}