import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { api, getStoredToken, storeToken } from "./api/client";
import { AppShell } from "./components/layout/AppShell";
import { buildSubmissionAnswers } from "./features/forms/FormRenderer";
import { demographicAutofillValue, isRepeatedDemographicField } from "./features/forms/fieldMeta";
import { calculateAsqScores } from "./features/scoring/asqScoring";
import { calculateBehavioralScores } from "./features/scoring/behavioralScoring";
import { enrichSubmission } from "./features/submissions/review";
import { IntakePage } from "./pages/IntakePage";
import { LoginPage } from "./pages/LoginPage";
import { StaffPage } from "./pages/StaffPage";
import { SubmissionsPage } from "./pages/SubmissionsPage";
import { TemplatesPage } from "./pages/TemplatesPage";
import { WelcomePage, recommendFormsFromRouting } from "./pages/WelcomePage";

function initialAnswersForForm(form) {
  const answers = {};
  if (!form) return answers;
  for (const section of form.sections || []) {
    for (const field of section.fields || []) {
      if (isRepeatedDemographicField(field, section.title)) continue;
      answers[field.id] = field.type === "multicheck" ? [] : field.type === "checkbox" ? false : "";
    }
  }
  return answers;
}

function addCalculatedScores(formId, answers) {
  const next = { ...answers };
  for (const score of calculateAsqScores(formId, answers)) {
    next[score.totalFieldId] = score.total === null ? "" : String(score.total);
    next[score.summaryFieldId] = score.total === null ? "" : String(score.total);
    next[score.zoneFieldId] = score.zone.value;
  }
  Object.assign(next, calculateBehavioralScores(answers));
  return next;
}

function visibleViewFor(view, { mode, user, routingComplete, showAllForms }) {
  if (view === "staff" && user?.role !== "admin") return mode === "staff" ? "intake" : "welcome";
  if (mode === "patient" && ["submissions", "templates", "staff"].includes(view)) return "welcome";
  if (view === "intake" && !routingComplete && !showAllForms) return "welcome";
  return view;
}

const VIEW_PATHS = {
  login: "/login",
  welcome: "/start",
  intake: "/intake",
  submissions: "/submissions",
  templates: "/templates",
  staff: "/staff"
};

const PATH_VIEWS = Object.fromEntries(Object.entries(VIEW_PATHS).map(([view, path]) => [path, view]));

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const [authToken, setAuthToken] = useState(getStoredToken);
  const [authReady, setAuthReady] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [mode, setMode] = useState("patient");
  const [health, setHealth] = useState("Checking server");
  const [needsFirstAdmin, setNeedsFirstAdmin] = useState(false);
  const [forms, setForms] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [submissionDetailLoading, setSubmissionDetailLoading] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [staffUsers, setStaffUsers] = useState([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [recommendedFormIds, setRecommendedFormIds] = useState([]);
  const [routingComplete, setRoutingComplete] = useState(false);
  const [showAllForms, setShowAllForms] = useState(false);
  const [selectedFormId, setSelectedFormId] = useState(null);
  const [search, setSearch] = useState("");
  const [answers, setAnswers] = useState({});
  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState(false);
  const [formMessage, setFormMessage] = useState("");
  const [formError, setFormError] = useState(false);
  const [staffMessage, setStaffMessage] = useState("");
  const [staffError, setStaffError] = useState(false);

  const isStaff = mode === "staff";
  const view = PATH_VIEWS[location.pathname] || "login";
  const selectedForm = useMemo(() => forms.find((form) => form.id === selectedFormId), [forms, selectedFormId]);

  const navigateToView = useCallback((nextView, options = {}) => {
    navigate(VIEW_PATHS[nextView] || VIEW_PATHS.login, options);
  }, [navigate]);

  useEffect(() => {
    document.body.classList.toggle("access-mode", view === "login");
    document.body.classList.toggle("staff-mode", mode === "staff");
    document.body.classList.toggle("patient-mode", mode !== "staff");
    document.body.classList.toggle("admin-mode", currentUser?.role === "admin");
    document.body.dataset.view = view;
  }, [view, mode, currentUser]);

  useEffect(() => {
    setAnswers(initialAnswersForForm(selectedForm));
    setFormMessage("");
    setFormError(false);
  }, [selectedForm]);

  const setAuthSession = useCallback((payload) => {
    const token = payload.accessToken || "";
    setAuthToken(token);
    setCurrentUser(payload.user || null);
    storeToken(token);
  }, []);

  const loadBootstrapState = useCallback(async () => {
    const payload = await api("/api/auth/bootstrap", {}, authToken);
    setNeedsFirstAdmin(Boolean(payload.needsFirstAdmin));
  }, [authToken]);

  const checkHealth = useCallback(async () => {
    try {
      await api("/api/health", {}, authToken);
      setHealth("Server online");
    } catch {
      setHealth("Server offline");
    }
  }, [authToken]);

  const loadForms = useCallback(async () => {
    const payload = await api("/api/forms", {}, authToken);
    setForms(payload.forms);
    if (mode === "staff") {
      setShowAllForms(true);
      setRoutingComplete(true);
      setRecommendedFormIds(payload.forms.map((form) => form.id));
      setSelectedFormId((current) => current || payload.forms[0]?.id || null);
    }
  }, [authToken, mode]);

  const loadStaff = useCallback(async (user = currentUser, token = authToken) => {
    if (!token || user?.role !== "admin") {
      setStaffUsers([]);
      return;
    }
    setStaffLoading(true);
    try {
      const payload = await api("/api/staff", {}, token);
      setStaffUsers(payload.staff);
    } finally {
      setStaffLoading(false);
    }
  }, [authToken, currentUser]);

  const loadSubmissions = useCallback(async () => {
    if (!authToken) {
      setSubmissions([]);
      setSelectedSubmission(null);
      return;
    }
    setSubmissionsLoading(true);
    try {
      const payload = await api("/api/submissions", {}, authToken);
      const detailed = await Promise.all(
        payload.submissions.map(async (submission) => {
          try {
            const detail = await api(`/api/submissions/${encodeURIComponent(submission.id)}`, {}, authToken);
            return enrichSubmission({ ...submission, answers: detail.submission.answers || {} });
          } catch {
            return enrichSubmission(submission);
          }
        })
      );
      setSubmissions(detailed);
      setSelectedSubmission((current) => {
        if (!current) return null;
        return detailed.find((item) => item.id === current.id) || null;
      });
    } finally {
      setSubmissionsLoading(false);
    }
  }, [authToken]);

  const refreshAll = useCallback(async () => {
    await checkHealth();
    await loadBootstrapState();
    await loadForms();
    await loadSubmissions();
    await loadStaff();
  }, [checkHealth, loadBootstrapState, loadForms, loadSubmissions, loadStaff]);

  useEffect(() => {
    async function restore() {
      if (!authToken) {
        await refreshAll();
        if (location.pathname === "/") navigateToView("login", { replace: true });
        setAuthReady(true);
        return;
      }
      let restoredUser = null;
      try {
        const payload = await api("/api/auth/me", {}, authToken);
        restoredUser = payload.user;
        setCurrentUser(payload.user);
        setMode("staff");
        if (location.pathname === "/" || location.pathname === "/login") navigateToView("intake", { replace: true });
      } catch {
        setAuthSession({ accessToken: "", user: null });
        navigateToView("login", { replace: true });
      }
      await refreshAll();
      if (restoredUser?.role === "admin") await loadStaff(restoredUser, authToken);
      setAuthReady(true);
    }
    restore();
  }, []);

  useEffect(() => {
    if (!authToken) return;
    loadSubmissions();
    loadStaff();
  }, [authToken, currentUser?.role, loadSubmissions, loadStaff]);

  useEffect(() => {
    if (!authReady || !authToken || view !== "submissions") return;
    loadSubmissions();
  }, [authReady, authToken, view, loadSubmissions]);

  function changeView(nextView) {
    navigateToView(visibleViewFor(nextView, { mode, user: currentUser, routingComplete, showAllForms }));
  }

  async function authenticate(credentials, authMode = "login") {
    setAuthMessage("");
    setAuthError(false);
    try {
      const payload = await api(`/api/auth/${authMode === "register" ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({
          email: credentials.email.trim(),
          password: credentials.password,
          name: credentials.name?.trim() || undefined
        })
      });
      setAuthSession(payload);
      setMode("staff");
      setShowAllForms(true);
      setRoutingComplete(true);
      navigateToView("intake");
      await refreshAll();
      if (payload.user?.role === "admin") await loadStaff(payload.user, payload.accessToken);
    } catch (error) {
      setAuthError(true);
      setAuthMessage(error.message);
    }
  }

  function continuePatient() {
    setMode("patient");
    setRoutingComplete(false);
    setShowAllForms(false);
    setRecommendedFormIds([]);
    setSelectedFormId(null);
    navigateToView("welcome");
  }

  function enterStaffMode() {
    if (!authToken) {
      navigateToView("login");
      return;
    }
    setMode("staff");
    setShowAllForms(true);
    setRoutingComplete(true);
    setRecommendedFormIds(forms.map((form) => form.id));
    setSelectedFormId((current) => current || forms[0]?.id || null);
    navigateToView("intake");
  }

  function logout() {
    setAuthSession({ accessToken: "", user: null });
    setMode("patient");
    setRoutingComplete(false);
    setShowAllForms(false);
    setRecommendedFormIds([]);
    setSelectedFormId(null);
    navigateToView("login");
  }

  function handleRoute(formData) {
    const ids = recommendFormsFromRouting(formData);
    setRecommendedFormIds(ids);
    setRoutingComplete(true);
    setShowAllForms(false);
    setSelectedFormId(ids[0] || null);
    navigateToView("intake");
  }

  function showAllStaffForms() {
    if (!authToken) {
      navigateToView("login");
      return;
    }
    setMode("staff");
    setShowAllForms(true);
    setRoutingComplete(true);
    setRecommendedFormIds(forms.map((form) => form.id));
    setSelectedFormId((current) => current || forms[0]?.id || null);
    navigateToView("intake");
  }

  function handleAnswerChange(fieldId, value) {
    setAnswers((current) => {
      const next = { ...current, [fieldId]: value };
      for (const section of selectedForm?.sections || []) {
        for (const field of section.fields || []) {
          if (isRepeatedDemographicField(field, section.title)) {
            next[field.id] = demographicAutofillValue(field, next);
          }
        }
      }
      return addCalculatedScores(selectedForm?.id, next);
    });
  }

  async function submitIntake(event) {
    event.preventDefault();
    if (!selectedForm) return;
    setFormMessage("");
    setFormError(false);
    try {
      const payload = await api("/api/submissions", {
        method: "POST",
        body: JSON.stringify({ formId: selectedForm.id, answers: buildSubmissionAnswers(selectedForm, addCalculatedScores(selectedForm.id, answers), mode) })
      }, authToken);
      setFormMessage(`Saved ${payload.submission.formName} for ${payload.submission.patientName}.`);
      setAnswers(initialAnswersForForm(selectedForm));
      await loadSubmissions();
    } catch (error) {
      setFormError(true);
      setFormMessage([error.message, ...(error.details || [])].join(" "));
    }
  }

  async function selectSubmission(id) {
    setSubmissionDetailLoading(true);
    try {
      const summary = submissions.find((item) => item.id === id);
      const payload = await api(`/api/submissions/${encodeURIComponent(id)}`, {}, authToken);
      setSelectedSubmission(enrichSubmission({ ...summary, ...payload.submission }));
    } finally {
      setSubmissionDetailLoading(false);
    }
  }

  async function updateSubmissionStatus(id, status, nextAnswers) {
    const body = { status };
    if (nextAnswers) body.answers = addCalculatedScores(selectedSubmission?.formId, nextAnswers);

    await api(`/api/submissions/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(body)
    }, authToken);
    await loadSubmissions();
    await selectSubmission(id);
  }

  async function createStaff(payload, onSuccess) {
    setStaffMessage("");
    setStaffError(false);
    try {
      const result = await api("/api/staff", {
        method: "POST",
        body: JSON.stringify({
          name: payload.name,
          email: payload.email,
          password: payload.password,
          role: payload.role,
          title: payload.title || undefined,
          clinicLocation: payload.clinicLocation || undefined
        })
      }, authToken);
      setStaffMessage(`Created ${result.user.role} account for ${result.user.email}.`);
      onSuccess();
      await loadStaff();
    } catch (error) {
      setStaffError(true);
      setStaffMessage(error.message);
    }
  }

  const loginPage = (
      <LoginPage
        needsFirstAdmin={needsFirstAdmin}
        onLogin={(payload) => authenticate(payload, "login")}
        onRegister={(payload) => authenticate(payload, "register")}
        onContinuePatient={continuePatient}
        message={authMessage}
        error={authError}
      />
  );

  const welcomePage = <WelcomePage onRoute={handleRoute} onShowAllForms={showAllStaffForms} onStartOver={continuePatient} isStaff={isStaff} />;

  const intakePage = (
    <IntakePage
      forms={forms}
      selectedForm={selectedForm}
      selectedFormId={selectedFormId}
      setSelectedFormId={setSelectedFormId}
      search={search}
      setSearch={setSearch}
      showAllForms={showAllForms}
      routingComplete={routingComplete}
      recommendedFormIds={recommendedFormIds}
      answers={answers}
      mode={mode}
      onAnswerChange={handleAnswerChange}
      onSubmit={submitIntake}
      onClear={() => {
        setAnswers(initialAnswersForForm(selectedForm));
        setFormMessage("");
        setFormError(false);
      }}
      onStartOver={continuePatient}
      message={formMessage}
      error={formError}
    />
  );

  const submissionsPage = authToken ? (
    <SubmissionsPage
      submissions={submissions}
      isLoading={submissionsLoading}
      detailLoading={submissionDetailLoading}
      selectedSubmission={selectedSubmission}
      forms={forms}
      onSelect={selectSubmission}
      onStatusChange={updateSubmissionStatus}
    />
  ) : authReady ? <Navigate to="/login" replace /> : <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>;

  const templatesPage = authToken ? <TemplatesPage forms={forms} /> : authReady ? <Navigate to="/login" replace /> : <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>;
  const staffPage = !authReady
    ? <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>
    : currentUser?.role === "admin"
    ? <StaffPage staffUsers={staffUsers} isLoading={staffLoading} onCreateStaff={createStaff} message={staffMessage} error={staffError} />
    : <Navigate to={authToken ? "/intake" : "/login"} replace />;
  const guardedIntakePage = authToken && !authReady
    ? <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>
    : mode === "patient" && !routingComplete && !showAllForms
      ? <Navigate to="/start" replace />
      : intakePage;

  if (view === "login") return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={loginPage} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );

  return (
    <AppShell
      view={view}
      mode={mode}
      user={currentUser}
      health={health}
      onViewChange={changeView}
      onRefresh={refreshAll}
      onStaffMode={enterStaffMode}
      onPatientMode={continuePatient}
      onLogout={logout}
      onStartOver={continuePatient}
    >
      <Routes>
        <Route path="/" element={<Navigate to={authToken ? "/intake" : "/login"} replace />} />
        <Route path="/login" element={<Navigate to={authToken ? "/intake" : "/login"} replace />} />
        <Route path="/start" element={welcomePage} />
        <Route path="/intake" element={guardedIntakePage} />
        <Route path="/submissions" element={submissionsPage} />
        <Route path="/templates" element={templatesPage} />
        <Route path="/staff" element={staffPage} />
        <Route path="*" element={<Navigate to="/start" replace />} />
      </Routes>
    </AppShell>
  );
}
