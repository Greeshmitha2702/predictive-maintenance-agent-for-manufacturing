// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Default to real API mode. Set VITE_USE_MOCK_API=true to use mock data
// (useful for frontend-only development without a running backend).
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";

// Backend base URL. Override with VITE_API_BASE_URL in .env.
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ---------------------------------------------------------------------------
// Response validation
// ---------------------------------------------------------------------------

// All 8 fields that the backend must return for a valid prediction.
const REQUIRED_FIELDS = [
  "failure_probability",
  "failure_predicted",
  "is_anomaly",
  "anomaly_score",
  "risk_level",
  "model_version",
  "explanation",
  "recommendations",
];

function validatePredictionResponse(data) {
  if (!data || typeof data !== "object") {
    throw new Error("Invalid prediction response: not an object.");
  }
  for (const field of REQUIRED_FIELDS) {
    if (!Object.prototype.hasOwnProperty.call(data, field)) {
      throw new Error(`Invalid prediction response: missing field "${field}".`);
    }
  }
  return data;
}

// ---------------------------------------------------------------------------
// Response mapping  (single place — never scatter this across components)
// ---------------------------------------------------------------------------
//
// Converts the flat backend API response into the nested shape expected by
// existing UI components, preserving every field from the original response
// so Analysis.jsx can still read failure_probability, failure_predicted, etc.
// directly off predictionResult.
//
// Backend flat shape  →  Frontend nested additions:
//   failure_probability  →  failure_prediction.probability
//   failure_predicted    →  failure_prediction.predicted_failure
//   risk_level           →  failure_prediction.risk_level
//   is_anomaly           →  anomaly.is_anomaly
//   anomaly_score        →  anomaly.score
//   (machine type comes from the submitted machineData arg)

function mapApiResponse(rawData, machineData) {
  return {
    // --- Pass through every raw backend field so Analysis.jsx still works ---
    ...rawData,

    // --- Nested shape for Dashboard cards ---
    failure_prediction: {
      probability: rawData.failure_probability,
      predicted_failure: rawData.failure_predicted,
      risk_level: rawData.risk_level,
    },
    anomaly: {
      is_anomaly: rawData.is_anomaly,
      score: rawData.anomaly_score,
    },
    // Machine type for History display — sourced from submitted input
    machine: {
      type: machineData?.type ?? "—",
    },
  };
}

// ---------------------------------------------------------------------------
// Mock data  (returned when VITE_USE_MOCK_API=true)
// ---------------------------------------------------------------------------

function getMockResponse(machineData) {
  const raw = {
    failure_probability: 0.82,
    failure_predicted: true,
    is_anomaly: true,
    anomaly_score: -0.31,
    risk_level: "HIGH",
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
    recommendations: {
      risk_level: "HIGH",
      urgency: "Prioritise preventive maintenance before the next operating cycle",
      root_cause_indicators: ["Mock indicator"],
      recommendations: [
        {
          id: "MOCK-001",
          category: "INSPECTION",
          severity: "WARNING",
          title: "Inspect Tool Condition",
          action: "Inspect tool condition and consider tool replacement.",
        },
      ],
    },
  };
  return mapApiResponse(raw, machineData);
}

// ---------------------------------------------------------------------------
// 422 Validation Error Formatting
// ---------------------------------------------------------------------------

// Human-readable names for each backend field used in error messages.
const FIELD_LABELS = {
  type:                "machine type",
  air_temperature:     "air temperature",
  process_temperature: "process temperature",
  rotational_speed:    "rotational speed",
  torque:              "torque",
  tool_wear:           "tool wear",
};

// Capitalise the first letter for use at the start of a sentence.
function capitalise(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Convert a single FastAPI validation error object into a readable sentence.
// Shape: { type, loc: ["body", <field>], msg, ctx? }
function formatSingleError(err) {
  const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : "";
  const label = FIELD_LABELS[field] || String(field).replace(/_/g, " ");

  switch (err.type) {
    case "missing":
      return `Missing required field: Please enter ${label}.`;

    case "enum":
      // e.g. type must be 'L', 'M' or 'H'
      return `Invalid ${label}: Please select L, M, or H.`;

    case "greater_than": {
      // gt constraint — field must be strictly positive
      const gt = err.ctx?.gt ?? 0;
      return `Invalid ${label}: ${capitalise(label)} must be greater than ${gt}.`;
    }

    case "greater_than_equal": {
      // ge constraint — field must be 0 or greater
      const ge = err.ctx?.ge ?? 0;
      return `Invalid ${label}: ${capitalise(label)} must be ${ge} or greater.`;
    }

    case "less_than_equal": {
      // le constraint — field must not exceed the upper bound
      const le = err.ctx?.le;
      if (le !== undefined) {
        return `Invalid ${label}: ${capitalise(label)} must be ${le} or less.`;
      }
      return `Invalid ${label}: Value is out of the allowed range.`;
    }

    case "less_than": {
      // lt constraint — field must be strictly below the upper bound
      const lt = err.ctx?.lt;
      if (lt !== undefined) {
        return `Invalid ${label}: ${capitalise(label)} must be less than ${lt}.`;
      }
      return `Invalid ${label}: Value is out of the allowed range.`;
    }

    case "float_parsing":
    case "int_parsing":
    case "decimal_parsing":
      return `Invalid ${label}: Please enter a valid numeric value.`;

    default:
      // Safe fallback — show the label but not raw Pydantic internals.
      return `Invalid ${label}: Please check the entered value.`;
  }
}

// Convert a FastAPI 422 response body into a single user-readable string.
// Multiple errors are joined with a newline so every issue is surfaced.
function format422Error(body) {
  if (!body || !Array.isArray(body.detail) || body.detail.length === 0) {
    return "Unable to analyze the machine. Please check the entered values and try again.";
  }

  const messages = body.detail.map(formatSingleError);

  // Return all messages (most inputs only produce one, but be safe)
  return messages.join(" ");
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function predictMachine(machineData) {
  // --- Mock mode ---
  if (USE_MOCK_API) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockResponse(machineData)), 1000);
    });
  }

  // --- Real API mode ---
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(machineData),
    });
  } catch {
    // Network error (server unreachable, no internet, etc.)
    throw new Error(
      "Unable to connect to the prediction service. Please make sure the backend is running."
    );
  }

  if (!response.ok) {
    if (response.status === 422) {
      // FastAPI returns structured validation details — convert to readable text.
      let body;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      throw new Error(format422Error(body));
    }

    if (response.status >= 500) {
      throw new Error(
        "Prediction service encountered an error. Please try again."
      );
    }

    // Any other unexpected HTTP error.
    throw new Error(
      "Unable to analyze the machine. Please check the entered values and try again."
    );
  }

  const data = await response.json();

  // Validate all required fields before mapping.
  validatePredictionResponse(data);

  // Map flat backend shape → nested frontend shape.
  return mapApiResponse(data, machineData);
}

