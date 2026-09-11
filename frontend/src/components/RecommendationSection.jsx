import React from "react";

const RecommendationSection = ({ recommendations = [] }) => {
  return (
    <section className="recommendation-section">
      <h2>Recommendations</h2>

      {recommendations.length === 0 ? (
        <p>No recommendations available.</p>
      ) : (
        <div className="recommendation-list">
          {recommendations.map((recommendation, index) => (
            <div className="recommendation-card" key={index}>
              <h3>{recommendation.title}</h3>

              <p>{recommendation.description}</p>

              {recommendation.priority && (
                <span className="recommendation-priority">
                  Priority: {recommendation.priority}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default RecommendationSection;