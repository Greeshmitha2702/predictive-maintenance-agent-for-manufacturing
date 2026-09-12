const SHAPExplanation = ({ explanations = [] }) => {
  return (
    <section className="shap-explanation">
      <h2>SHAP Explanation</h2>

      {explanations.length === 0 ? (
        <p>No explanation data available.</p>
      ) : (
        <div className="shap-list">
          {explanations.map((item, index) => {
            const contribution = Number(item.contribution);
            const isPositive =
              item.direction === "increases_failure_risk";

            return (
              <div className="shap-item" key={index}>
                <div className="shap-feature">
                  <span>{item.feature}</span>
                  <span>
                    {Number.isFinite(contribution)
                      ? contribution.toFixed(4)
                      : "N/A"}
                  </span>
                </div>

                <div className="shap-bar">
                  <div
                    className={`shap-bar-fill ${
                      isPositive ? "positive" : "negative"
                    }`}
                    style={{
                      width: `${
                        Number.isFinite(contribution)
                          ? Math.min(Math.abs(contribution) * 100, 100)
                          : 0
                      }%`,
                    }}
                  />
                </div>

                <p className="shap-impact">
                  Contribution:{" "}
                  {Number.isFinite(contribution) && contribution > 0
                    ? "+"
                    : ""}
                  {Number.isFinite(contribution)
                    ? contribution.toFixed(4)
                    : "N/A"}
                </p>

                <p className="shap-direction">
                  {isPositive
                    ? "Increases failure risk"
                    : "Decreases failure risk"}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};

export default SHAPExplanation;