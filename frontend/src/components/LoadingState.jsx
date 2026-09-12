function LoadingState() {
  return (
    <section
      className="machine-card loading-card"
      role="status"
      aria-live="polite"
    >
      <div className="loading-spinner"></div>

      <h3>Analyzing Machine...</h3>

      <p>
        Please wait while the machine is being analyzed.
      </p>
    </section>
  );
}

export default LoadingState;