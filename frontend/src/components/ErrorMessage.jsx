function ErrorMessage({ message }) {
  if (!message) {
    return null;
  }

  return (
    <section className="machine-card error-card">
      <h3>Analysis Error</h3>

      <p className="error-message">
        {message}
      </p>
    </section>
  );
}

export default ErrorMessage;