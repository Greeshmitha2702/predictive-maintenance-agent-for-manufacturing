import { useState } from "react";
import { predictMachine } from "../services/api";

function MachineInputForm({ onAnalyze, onLoading, onError }) {
  // Store all values entered by the user.
  const [formData, setFormData] = useState({
    type: "M",
    air_temperature: "",
    process_temperature: "",
    rotational_speed: "",
    torque: "",
    tool_wear: "",
  });

  // Store validation error messages.
  const [error, setError] = useState("");

  // Store whether a prediction request is running.
  const [loading, setLoading] = useState(false);

  // Update the corresponding field whenever the user types.
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });

    // Clear both form and Dashboard errors when the user changes a value.
    setError("");
    onError("");
  };

  // Handle form submission.
  const handleSubmit = async (event) => {
    // Prevent another submission while a request is running.
    if (loading) {
      return;
    }

    // Prevent the browser from refreshing the page.
    event.preventDefault();

    // Check whether all fields are filled.
    if (
      formData.air_temperature === "" ||
      formData.process_temperature === "" ||
      formData.rotational_speed === "" ||
      formData.torque === "" ||
      formData.tool_wear === ""
    ) {
      setError("Please fill in all machine parameters.");
      onError("Please fill in all machine parameters.");
      return;
    }

    // Convert input values from strings to numbers.
    const machineData = {
      type: formData.type,
      air_temperature: Number(formData.air_temperature),
      process_temperature: Number(formData.process_temperature),
      rotational_speed: Number(formData.rotational_speed),
      torque: Number(formData.torque),
      tool_wear: Number(formData.tool_wear),
    };

    // Check that every numeric value is finite and positive.
    const numericValues = [
      machineData.air_temperature,
      machineData.process_temperature,
      machineData.rotational_speed,
      machineData.torque,
      machineData.tool_wear,
    ];

    if (numericValues.some((value) => !Number.isFinite(value) || value <= 0)) {
      setError("Please enter valid positive machine values.");
      onError("Please enter valid positive machine values.");
      return;
    }

    // Clear previous errors.
    setError("");
    onError("");

    try {
      // Prevent another submission while prediction is running.
      setLoading(true);

      // Tell the Dashboard that analysis has started.
      onLoading(true);

      // Send machine data to the prediction service.
      const result = await predictMachine(machineData);

      // Send the prediction result back to the Dashboard.
      onAnalyze(result);
    } catch {
      // Show an error if the prediction request fails.
      setError("Unable to analyze the machine.");
      onError("Unable to analyze the machine.");
    } finally {
      // Stop the loading state after the request finishes.
      setLoading(false);
      onLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-grid">

        {/* Machine type */}
        <div className="form-field">
          <label htmlFor="type">Machine Type</label>

          <select
            id="type"
            name="type"
            value={formData.type}
            onChange={handleChange}
          >
            <option value="L">L</option>
            <option value="M">M</option>
            <option value="H">H</option>
          </select>
        </div>

        {/* Air temperature */}
        <div className="form-field">
          <label htmlFor="air_temperature">
            Air Temperature (K)
          </label>

          <input
            id="air_temperature"
            name="air_temperature"
            type="number"
            min="0"
            step="any"
            value={formData.air_temperature}
            onChange={handleChange}
            placeholder="e.g. 298.5"
          />
        </div>

        {/* Process temperature */}
        <div className="form-field">
          <label htmlFor="process_temperature">
            Process Temperature (K)
          </label>

          <input
            id="process_temperature"
            name="process_temperature"
            type="number"
            min="0"
            step="any"
            value={formData.process_temperature}
            onChange={handleChange}
            placeholder="e.g. 308.6"
          />
        </div>

        {/* Rotational speed */}
        <div className="form-field">
          <label htmlFor="rotational_speed">
            Rotational Speed (rpm)
          </label>

          <input
            id="rotational_speed"
            name="rotational_speed"
            type="number"
            min="0"
            step="any"
            value={formData.rotational_speed}
            onChange={handleChange}
            placeholder="e.g. 1550"
          />
        </div>

        {/* Torque */}
        <div className="form-field">
          <label htmlFor="torque">Torque (Nm)</label>

          <input
            id="torque"
            name="torque"
            type="number"
            min="0"
            step="any"
            value={formData.torque}
            onChange={handleChange}
            placeholder="e.g. 42.3"
          />
        </div>

        {/* Tool wear */}
        <div className="form-field">
          <label htmlFor="tool_wear">Tool Wear (min)</label>

          <input
            id="tool_wear"
            name="tool_wear"
            type="number"
            min="0"
            step="any"
            value={formData.tool_wear}
            onChange={handleChange}
            placeholder="e.g. 120"
          />
        </div>

      </div>

      {/* Analyze button */}
      <div className="form-actions">
        <button
          type="submit"
          className="analyze-button"
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Machine"}
        </button>
      </div>

      {/* Display validation error */}
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}

export default MachineInputForm;