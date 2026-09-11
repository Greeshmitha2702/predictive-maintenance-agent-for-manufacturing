const USE_MOCK_API = true;

const API_BASE_URL = "http://localhost:8000";

export async function predictMachine(machineData) {
  if (USE_MOCK_API) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          machine: {
            type: machineData.type,
          },
          anomaly: {
            is_anomaly: true,
            score: -0.31,
          },
          failure_prediction: {
            predicted_failure: true,
            probability: 0.82,
            risk_level: "HIGH",
          },
          explanation: {
            top_factors: [
              {
                feature: "tool_wear",
                contribution: 0.24,
                direction: "increases_risk",
              },
            ],
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