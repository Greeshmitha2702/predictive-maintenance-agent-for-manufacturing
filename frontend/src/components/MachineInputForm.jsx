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

  // Update the corresponding field whenever the user types.
  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });

    // Remove the old error when the user changes a value.
    setError("");
  };

  // Handle form submission.
  const handleSubmit = async (event) => {
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

    // Check for invalid negative values.
    if (
      machineData.rotational_speed <= 0 ||
      machineData.torque <= 0 ||
      machineData.tool_wear < 0
    ) {
      setError("Please enter valid positive machine values.");
      return;
    }

    // Clear previous errors.
    setError("");
    onError("");

    try {
      // Tell the Dashboard that analysis has started.
      onLoading(true);

      // Send machine data to the prediction service.
      const result = await predictMachine(machineData);

      // Send the prediction result back to the Dashboard.
      onAnalyze(result);
    } catch (error) {
      // Show an error if the prediction request fails.
      setError("Unable to analyze the machine.");
      onError("Unable to analyze the machine.");
    } finally {
      // Stop the loading state after the request finishes.
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
            min="1"
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
            value={formData.tool_wear}
            onChange={handleChange}
            placeholder="e.g. 120"
          />
        </div>

      </div>


      {/* Analyze button */}
      <div className="form-actions">
        <button type="submit" className="analyze-button">
          Analyze Machine
        </button>
      </div>


      {/* Display validation error */}
      {error && <p className="error-message">{error}</p>}
    </form>
  );
}

export default MachineInputForm;