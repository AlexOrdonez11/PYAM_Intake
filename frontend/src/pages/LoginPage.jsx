import { useState } from "react";
import { BrandLogo } from "../components/layout/BrandLogo";

export function LoginPage({ needsFirstAdmin, onLogin, onRegister, onContinuePatient, message, error }) {
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  return (
    <section className="view active" aria-label="Access">
      <div className="access-layout">
        <section className="panel access-panel" aria-label="Sign in or continue">
          <BrandLogo tone="light" subtitle="Clinic intake platform" />

          <form className="auth-card inline-auth-card" onSubmit={(event) => {
            event.preventDefault();
            onLogin(form);
          }}>
            <div className="field">
              <label htmlFor="auth-email">Email</label>
              <input id="auth-email" className="field-control" value={form.email} onChange={(event) => update("email", event.target.value)} type="email" autoComplete="email" required />
            </div>
            <div className="field">
              <label htmlFor="auth-password">Password</label>
              <input id="auth-password" className="field-control" value={form.password} onChange={(event) => update("password", event.target.value)} type="password" autoComplete="current-password" minLength="8" required />
            </div>
            {needsFirstAdmin ? (
              <div className="field">
                <label htmlFor="auth-name">Name</label>
                <input id="auth-name" className="field-control" value={form.name} onChange={(event) => update("name", event.target.value)} type="text" autoComplete="name" placeholder="Only needed for first admin" />
              </div>
            ) : null}
            <div className="form-footer access-actions">
              {needsFirstAdmin ? (
                <button className="secondary-button" type="button" onClick={() => onRegister(form)}>Create First Admin</button>
              ) : null}
              <button className="primary-button" type="submit">Log in</button>
            </div>
            <div className={`message${error ? " error" : ""}`} role="status">{message}</div>
          </form>

          <div className="patient-entry">
            <div>
              <h2>Here as a patient?</h2>
              <p>No login needed. Continue to answer a few visit questions and find the right forms.</p>
            </div>
            <button className="secondary-button" onClick={onContinuePatient} type="button">Continue as patient</button>
          </div>
        </section>
      </div>
    </section>
  );
}
