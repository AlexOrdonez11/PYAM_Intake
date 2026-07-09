import { BrandLogo } from "./BrandLogo";

export function AppShell({
  children,
  view,
  mode,
  user,
  health,
  onViewChange,
  onRefresh,
  onStaffMode,
  onPatientMode,
  onLogout,
  onStartOver
}) {
  const isAdmin = user?.role === "admin";
  const title =
    view === "login"
      ? "Welcome"
      : view === "submissions"
        ? "Submission Review"
        : view === "staff"
          ? "Staff Access"
          : view === "templates"
            ? "Template Library"
            : view === "welcome"
              ? "Start Intake"
              : "Patient Intake";

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <BrandLogo tone="dark" subtitle="Clinic intake platform" />

        <nav className="nav-tabs" aria-label="Views">
          <button className={`nav-button ${view === "welcome" ? "active" : ""}`} onClick={() => onViewChange("welcome")} type="button">Welcome</button>
          <button className={`nav-button ${view === "intake" ? "active" : ""}`} onClick={() => onViewChange("intake")} type="button">Intake</button>
          <button className={`nav-button ${view === "submissions" ? "active" : ""}`} onClick={() => onViewChange("submissions")} data-staff-only type="button">Submissions</button>
          <button className={`nav-button ${view === "templates" ? "active" : ""}`} onClick={() => onViewChange("templates")} data-staff-only type="button">Templates</button>
          {isAdmin ? (
            <button className={`nav-button ${view === "staff" ? "active" : ""}`} onClick={() => onViewChange("staff")} data-admin-only type="button">Staff</button>
          ) : null}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="topbar-title">
            <BrandLogo tone="light" compact />
            <div className="topbar-heading-copy">
              <p className="eyebrow">Prototype</p>
              <h1>{title}</h1>
            </div>
          </div>
          <div className="topbar-actions">
            <span className="pill" id="view-mode-pill">{mode === "staff" ? "Staff view" : "Patient view"}</span>
            <span className="pill" data-staff-only>{health}</span>
            {user ? <span className="pill" data-staff-only>{user.email} - {user.role}</span> : null}
            <button className="ghost-button" id="start-over-button" onClick={onStartOver} type="button">Start over</button>
            <button className="ghost-button" id="patient-mode-button" onClick={onPatientMode} data-staff-only type="button">Patient view</button>
            <button className="ghost-button" id="staff-mode-button" onClick={onStaffMode} type="button">Staff login</button>
            {user ? <button className="ghost-button" id="logout-button" onClick={onLogout} data-staff-only type="button">Log out</button> : null}
            <button className="ghost-button" onClick={onRefresh} data-staff-only type="button">Refresh</button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
