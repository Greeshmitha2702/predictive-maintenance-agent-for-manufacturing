const USE_MOCK_API =
  import.meta.env.VITE_USE_MOCK_API !== "false";
// Use the environment variable if available.
// Otherwise, use localhost for development.
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Check that the real backend returned the fields we expect.
function validatePredictionResponse(data) {
  if (!data || typeof data !== "object") {
    throw new Error("Invalid prediction response.");
  }

  const requiredFields = [
    "failure_probability",
    "failure_predicted",
    "is_anomaly",
    "anomaly_score",
    "model_version",
  ];

  const hasAllFields = requiredFields.every(
    (field) => Object.prototype.hasOwnProperty.call(data, field)
  );

  if (!hasAllFields) {
    throw new Error("Invalid prediction response.");
  }

  return data;
}
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

  const data = await response.json();

  return validatePredictionResponse(data);
}
