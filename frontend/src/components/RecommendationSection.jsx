const RecommendationSection = ({ recommendations = [] }) => {
  return (
    <section className="recommendation-section">
      <h2>Recommendations</h2>

      {recommendations.length === 0 ? (
        <p>No recommendations available.</p>
      ) : (
        <div className="recommendation-list">
          {recommendations.map((recommendation, index) => {
            const isObject =
              recommendation !== null &&
              typeof recommendation === "object";

            const text =
              typeof recommendation === "string"
                ? recommendation
                : recommendation?.description ||
                  recommendation?.title ||
                  "";

            return (
              <div className="recommendation-card" key={index}>
                {isObject && recommendation.title && (
                  <h3>{recommendation.title}</h3>
                )}

                {text && <p>{text}</p>}

                {isObject && recommendation.priority && (
                  <span className="recommendation-priority">
                    Priority: {recommendation.priority}
                  </span>
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