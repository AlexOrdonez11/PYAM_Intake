import { useState } from "react";

export function StaffPage({ staffUsers, isLoading, onCreateStaff, message, error }) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "staff",
    title: "",
    clinicLocation: ""
  });
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  return (
    <section className="view active" aria-label="Staff">
      <div className="staff-layout">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Staff Access</h2>
              <p>Create staff accounts and assign prototype roles.</p>
            </div>
          </div>
          <form className="staff-form" onSubmit={(event) => {
            event.preventDefault();
            onCreateStaff(form, () => setForm({ name: "", email: "", password: "", role: "staff", title: "", clinicLocation: "" }));
          }}>
            <div className="field">
              <label htmlFor="staff-name">Name</label>
              <input id="staff-name" className="field-control" value={form.name} onChange={(event) => update("name", event.target.value)} type="text" required />
            </div>
            <div className="field">
              <label htmlFor="staff-email">Email</label>
              <input id="staff-email" className="field-control" value={form.email} onChange={(event) => update("email", event.target.value)} type="email" required />
            </div>
            <div className="field">
              <label htmlFor="staff-password">Temporary password</label>
              <input id="staff-password" className="field-control" value={form.password} onChange={(event) => update("password", event.target.value)} type="password" minLength="8" required />
            </div>
            <div className="field">
              <label htmlFor="staff-role">Role</label>
              <select id="staff-role" className="field-control" value={form.role} onChange={(event) => update("role", event.target.value)}>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="staff-title">Title</label>
              <input id="staff-title" className="field-control" value={form.title} onChange={(event) => update("title", event.target.value)} type="text" placeholder="Front desk, nurse, manager" />
            </div>
            <div className="field">
              <label htmlFor="staff-location">Clinic location</label>
              <select id="staff-location" className="field-control" value={form.clinicLocation} onChange={(event) => update("clinicLocation", event.target.value)}>
                <option value="">No default</option>
                <option value="eagan">Eagan</option>
                <option value="maplewood">Maplewood</option>
              </select>
            </div>
            <div className="form-footer">
              <button className="primary-button" type="submit">Create User</button>
            </div>
            <div className={`message${error ? " error" : ""}`} role="status">{message}</div>
          </form>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Current Users</h2>
              <p>Admin users can manage staff access.</p>
            </div>
          </div>
          <div className="staff-list">
            {isLoading ? (
              <div className="empty-state compact-empty"><h2>Loading users</h2><p>Checking prototype staff access.</p></div>
            ) : staffUsers.length ? staffUsers.map((user) => (
              <article className="staff-card" key={user.id}>
                <div>
                  <strong>{user.name || user.email}</strong>
                  <span>{user.email}</span>
                </div>
                <div className="staff-card-meta">
                  <span className="status-badge">{user.role}</span>
                  <span>{user.title || "No title"}</span>
                  <span>{user.clinicLocation || "All locations"}</span>
                </div>
              </article>
            )) : (
              <div className="empty-state compact-empty"><h2>No users yet</h2><p>Create the first staff account from the form.</p></div>
            )}
          </div>
        </section>
      </div>
    </section>
  );
}
