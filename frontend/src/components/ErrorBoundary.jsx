import React from "react";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Application error", error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <main className="error-boundary">
        <section className="empty-state">
          <h1>Something went wrong</h1>
          <p>The page could not finish loading. Refresh the page or return to the previous workflow.</p>
          <button className="primary-button" type="button" onClick={() => window.location.reload()}>Refresh</button>
        </section>
      </main>
    );
  }
}
