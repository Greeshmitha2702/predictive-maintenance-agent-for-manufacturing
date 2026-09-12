const SEVERITY_CLASS = {
  CRITICAL: "severity-critical",
  WARNING: "severity-warning",
  INFO: "severity-info",
};

const RecommendationSection = ({
  recommendations = [],
  urgency,
  rootCauseIndicators = [],
}) => {
  return (
    <section className="recommendation-section">
      <h2>Recommendations</h2>

      {urgency && (
        <p className="recommendation-urgency">{urgency}</p>
      )}

      {rootCauseIndicators.length > 0 && (
        <div className="root-cause-indicators">
          <p className="result-label">Potential Contributing Factors</p>
          <ul>
            {rootCauseIndicators.map((indicator, index) => (
              <li key={index}>{indicator}</li>
            ))}
          </ul>
        </div>
      )}

      {recommendations.length === 0 ? (
        <p>No recommendations available.</p>
      ) : (
        <div className="recommendation-list">
          {recommendations.map((recommendation, index) => {
            const isObject =
              recommendation !== null &&
              typeof recommendation === "object";

            // Plain-string fallback (mock mode / legacy)
            if (!isObject) {
              return (
                <div className="recommendation-card" key={index}>
                  <p>{String(recommendation)}</p>
                </div>
              );
            }

            const severityClass =
              SEVERITY_CLASS[recommendation.severity] || "severity-info";

            return (
              <div className="recommendation-card" key={recommendation.id || index}>
                <div className="recommendation-card-header">
                  {recommendation.title && (
                    <h3>{recommendation.title}</h3>
                  )}
                  <div className="recommendation-badges">
                    {recommendation.severity && (
                      <span className={`recommendation-severity ${severityClass}`}>
                        {recommendation.severity}
                      </span>
                    )}
                    {recommendation.category && (
                      <span className="recommendation-category">
                        {recommendation.category}
                      </span>
                    )}
                  </div>
                </div>

                {recommendation.action && (
                  <p className="recommendation-action">{recommendation.action}</p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};

export default RecommendationSection;