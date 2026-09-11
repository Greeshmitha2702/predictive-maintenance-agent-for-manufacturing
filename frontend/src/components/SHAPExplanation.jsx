import React from "react";

const SHAPExplanation = ({ explanations = [] }) => {
  return (
    <section className="shap-explanation">
      <h2>SHAP Explanation</h2>

      {explanations.length === 0 ? (
        <p>No explanation data available.</p>
      ) : (
        <div className="shap-list">
          {explanations.map((item, index) => (
            <div className="shap-item" key={index}>
              <div className="shap-feature">
                <span>{item.feature}</span>
                <span>{item.value}</span>
              </div>

              <div className="shap-bar">
                <div
                  className={`shap-bar-fill ${
                    item.impact >= 0 ? "positive" : "negative"
                  }`}
                  style={{
                    width: `${Math.min(Math.abs(item.impact) * 100, 100)}%`,
                  }}
                />
              </div>

              <p className="shap-impact">
                Impact: {item.impact > 0 ? "+" : ""}
                {item.impact}
              </p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default SHAPExplanation;