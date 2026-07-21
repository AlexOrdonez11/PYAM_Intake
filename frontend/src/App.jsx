import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import { api, getStoredToken, storeToken } from "./api/client";
import { AppShell } from "./components/layout/AppShell";
import { buildSubmissionAnswers } from "./features/forms/FormRenderer";
import { getFormProgress } from "./features/forms/progressUtils";
import { demographicAutofillValue, isRepeatedDemographicField } from "./features/forms/fieldMeta";
import { addCalculatedScores } from "./features/scoring/calculatedScores";
import { enrichSubmission } from "./features/submissions/review";
import { IntakePage } from "./pages/IntakePage";
import { LoginPage } from "./pages/LoginPage";
import { StaffPage } from "./pages/StaffPage";
import { SubmissionsPage } from "./pages/SubmissionsPage";
import { TemplatesPage } from "./pages/TemplatesPage";
import { WelcomePage, recommendFormsFromRouting } from "./pages/WelcomePage";

const APP_MODE = window.PYAM_APP_MODE || "unified";
const IS_PATIENT_APP = APP_MODE === "patient";
const IS_STAFF_APP = APP_MODE === "staff";
const DRAFT_STORAGE_KEY = "pyam-intake-drafts-v1";

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

function readDraftStore() {
  try {
    return JSON.parse(window.localStorage.getItem(DRAFT_STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeDraftStore(store) {
  window.localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(store));
}

function draftForForm(formId) {
  return readDraftStore()[formId] || null;
}

function saveDraftForForm(form, answers) {
  if (!form) return null;
  const store = readDraftStore();
  const savedAt = new Date().toISOString();
  store[form.id] = {
    formId: form.id,
    formName: form.name,
    formTemplateVersion: form.version || 1,
    savedAt,
    answers
  };
  writeDraftStore(store);
  return store[form.id];
}

function removeDraftForForm(formId) {
  if (!formId) return;
  const store = readDraftStore();
  delete store[formId];
  writeDraftStore(store);
}

function clearAllDrafts() {
  window.localStorage.removeItem(DRAFT_STORAGE_KEY);
}

function hasMeaningfulAnswer(value) {
  if (Array.isArray(value)) return value.length > 0;
  if (value === true) return true;
  return value !== undefined && value !== null && String(value).trim() !== "";
}

function hasMeaningfulDraftAnswers(form, answers) {
  if (!form) return false;
  return Object.entries(answers || {}).some(([fieldId, value]) => {
    if (!hasMeaningfulAnswer(value)) return false;
    for (const section of form.sections || []) {
      const field = (section.fields || []).find((item) => item.id === fieldId);
      if (field && isRepeatedDemographicField(field, section.title)) return false;
    }
    return true;
  });
}

function visibleViewFor(view, { mode, user, routingComplete, showAllForms }) {
  if (IS_PATIENT_APP && ["login", "submissions", "templates", "staff"].includes(view)) return "welcome";
  if (IS_STAFF_APP && view === "welcome") return user ? "submissions" : "login";
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

function buildSubmissionQuery({ cursor = "", query = {} } = {}) {
  const params = new URLSearchParams();
  if (cursor) params.set("cursor", cursor);
  if (query.status) params.set("status", query.status);
  if (query.review) params.set("review", query.review);
  if (query.formId) params.set("formId", query.formId);
  if (query.search) params.set("search", query.search);
  if (query.sort) params.set("sort", query.sort);
  const queryText = params.toString();
  return queryText ? `?${queryText}` : "";
}

function SubmissionDetailRoute({
  authToken,
  submissions,
  submissionsLoading,
  submissionDetailLoading,
  selectedSubmission,
  forms,
  onSelect,
  onStatusChange,
  onRecordActivity,
  onBack
}) {
  const { submissionId } = useParams();

  useEffect(() => {
    if (!authToken || !submissionId) return;
    if (selectedSubmission?.id === submissionId && selectedSubmission?.answers) return;
    onSelect(submissionId);
  }, [authToken, submissionId, selectedSubmission?.id, selectedSubmission?.answers, onSelect]);

  return (
    <SubmissionsPage
      submissions={submissions}
      isLoading={submissionsLoading}
      detailLoading={submissionDetailLoading}
      selectedSubmission={selectedSubmission}
      forms={forms}
      onSelect={onSelect}
      onStatusChange={onStatusChange}
      onRecordActivity={onRecordActivity}
      detailOnly
      onBack={onBack}
    />
  );
}

function ResumeDraftRoute({ onLoadDraft }) {
  const { resumeCode } = useParams();

  useEffect(() => {
    if (resumeCode) onLoadDraft(resumeCode);
  }, [onLoadDraft, resumeCode]);

  return <div className="empty-state"><h2>Loading draft</h2><p>Opening the saved intake draft.</p></div>;
}

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const [authToken, setAuthToken] = useState(() => (IS_PATIENT_APP ? "" : getStoredToken()));
  const [authReady, setAuthReady] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [mode, setMode] = useState(IS_STAFF_APP ? "staff" : "patient");
  const [health, setHealth] = useState("Checking server");
  const [needsFirstAdmin, setNeedsFirstAdmin] = useState(false);
  const [forms, setForms] = useState([]);
  const [templateDrafts, setTemplateDrafts] = useState([]);
  const [templateVersions, setTemplateVersions] = useState({});
  const [submissions, setSubmissions] = useState([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [submissionsNextCursor, setSubmissionsNextCursor] = useState(null);
  const [submissionsHasMore, setSubmissionsHasMore] = useState(false);
  const [submissionQuery, setSubmissionQuery] = useState({ sort: "priority" });
  const [submissionDetailLoading, setSubmissionDetailLoading] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [staffUsers, setStaffUsers] = useState([]);
  const [staffLoading, setStaffLoading] = useState(false);
  const [recommendedFormIds, setRecommendedFormIds] = useState([]);
  const [completedFormIds, setCompletedFormIds] = useState([]);
  const [routingComplete, setRoutingComplete] = useState(false);
  const [showAllForms, setShowAllForms] = useState(false);
  const [selectedFormId, setSelectedFormId] = useState(null);
  const [search, setSearch] = useState("");
  const [answers, setAnswers] = useState({});
  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState(false);
  const [formMessage, setFormMessage] = useState("");
  const [formError, setFormError] = useState(false);
  const [completionNotice, setCompletionNotice] = useState(null);
  const [draftNotice, setDraftNotice] = useState(null);
  const [serverResumeDraft, setServerResumeDraft] = useState(null);
  const [resumeSaving, setResumeSaving] = useState(false);
  const [staffMessage, setStaffMessage] = useState("");
  const [staffError, setStaffError] = useState(false);

  const isStaff = mode === "staff";
  const view = location.pathname.startsWith("/submissions") ? "submissions" : location.pathname.startsWith("/resume/") ? "resume" : PATH_VIEWS[location.pathname] || "login";
  const selectedForm = useMemo(() => forms.find((form) => form.id === selectedFormId), [forms, selectedFormId]);

  const navigateToView = useCallback((nextView, options = {}) => {
    navigate(VIEW_PATHS[nextView] || VIEW_PATHS.login, options);
  }, [navigate]);

  useEffect(() => {
    document.body.classList.toggle("access-mode", view === "login");
    document.body.classList.toggle("staff-mode", mode === "staff" || IS_STAFF_APP);
    document.body.classList.toggle("patient-mode", mode !== "staff" || IS_PATIENT_APP);
    document.body.classList.toggle("split-patient-app", IS_PATIENT_APP);
    document.body.classList.toggle("split-staff-app", IS_STAFF_APP);
    document.body.classList.toggle("admin-mode", currentUser?.role === "admin");
    document.body.dataset.view = view;
  }, [view, mode, currentUser]);

  useEffect(() => {
    if (!selectedForm) {
      setAnswers({});
      setDraftNotice(null);
      return;
    }
    const initialAnswers = initialAnswersForForm(selectedForm);
    if (serverResumeDraft?.formId === selectedForm.id) {
      setAnswers(addCalculatedScores(selectedForm.id, { ...initialAnswers, ...(serverResumeDraft.answers || {}) }));
      setDraftNotice({
        formId: serverResumeDraft.formId,
        formName: serverResumeDraft.formName,
        savedAt: serverResumeDraft.updatedAt || serverResumeDraft.createdAt,
        restored: true,
        serverDraft: true,
        resumeCode: serverResumeDraft.resumeCode,
        resumeUrl: `${window.location.origin}/resume/${serverResumeDraft.resumeCode}`
      });
      setFormMessage("");
      setFormError(false);
      return;
    }
    const storedDraft = mode === "patient" ? draftForForm(selectedForm.id) : null;
    if (storedDraft?.answers) {
      setAnswers(addCalculatedScores(selectedForm.id, { ...initialAnswers, ...storedDraft.answers }));
      setDraftNotice({ ...storedDraft, restored: true });
    } else {
      setAnswers(initialAnswers);
      setDraftNotice(null);
    }
    setFormMessage("");
    setFormError(false);
  }, [selectedForm, mode, serverResumeDraft]);

  useEffect(() => {
    if (!selectedForm || mode !== "patient") return;
    const timer = window.setTimeout(() => {
      if (!hasMeaningfulDraftAnswers(selectedForm, answers)) {
        removeDraftForForm(selectedForm.id);
        setDraftNotice((current) => current?.serverDraft && current.formId === selectedForm.id ? current : null);
        return;
      }
      const saved = saveDraftForForm(selectedForm, answers);
      setDraftNotice((current) => current?.serverDraft && current.formId === selectedForm.id ? current : { ...saved, restored: false });
    }, 700);
    return () => window.clearTimeout(timer);
  }, [answers, mode, selectedForm]);

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

  const loadTemplateDrafts = useCallback(async () => {
    if (!authToken || currentUser?.role !== "admin") {
      setTemplateDrafts([]);
      return [];
    }
    const payload = await api("/api/forms/drafts", {}, authToken);
    setTemplateDrafts(payload.drafts || []);
    return payload.drafts || [];
  }, [authToken, currentUser?.role]);

  const loadTemplateVersions = useCallback(async (formId) => {
    if (!authToken || currentUser?.role !== "admin" || !formId) return [];
    const payload = await api(`/api/forms/${encodeURIComponent(formId)}/versions`, {}, authToken);
    setTemplateVersions((current) => ({ ...current, [formId]: payload.versions || [] }));
    return payload.versions || [];
  }, [authToken, currentUser?.role]);

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

  const loadSubmissions = useCallback(async ({ append = false, cursor = "" } = {}) => {
    if (!authToken) {
      setSubmissions([]);
      setSelectedSubmission(null);
      setSubmissionsNextCursor(null);
      setSubmissionsHasMore(false);
      return;
    }
    setSubmissionsLoading(true);
    try {
      const query = buildSubmissionQuery({ cursor, query: submissionQuery });
      const payload = await api(`/api/submissions${query}`, {}, authToken);
      const summaries = payload.submissions.map((submission) => enrichSubmission(submission));
      setSubmissions((current) => append ? [...current, ...summaries] : summaries);
      setSubmissionsNextCursor(payload.nextCursor || null);
      setSubmissionsHasMore(Boolean(payload.hasMore));
      setSelectedSubmission((current) => {
        if (!current) return null;
        const refreshedSummary = summaries.find((item) => item.id === current.id);
        return refreshedSummary ? { ...current, ...refreshedSummary } : current;
      });
    } finally {
      setSubmissionsLoading(false);
    }
  }, [authToken, submissionQuery]);

  const loadMoreSubmissions = useCallback(async () => {
    if (!submissionsNextCursor) return;
    await loadSubmissions({ append: true, cursor: submissionsNextCursor });
  }, [loadSubmissions, submissionsNextCursor]);

  const refreshAll = useCallback(async () => {
    await checkHealth();
    await loadBootstrapState();
    await loadForms();
    await loadSubmissions();
    await loadStaff();
  }, [checkHealth, loadBootstrapState, loadForms, loadSubmissions, loadStaff]);

  useEffect(() => {
    async function restore() {
      if (IS_PATIENT_APP) {
        setAuthSession({ accessToken: "", user: null });
        await checkHealth();
        await loadBootstrapState();
        await loadForms();
        if (location.pathname === "/" || location.pathname === "/login") navigateToView("welcome", { replace: true });
        setAuthReady(true);
        return;
      }
      if (!authToken) {
        await refreshAll();
        if (location.pathname === "/" || (IS_STAFF_APP && location.pathname === "/start")) navigateToView("login", { replace: true });
        setAuthReady(true);
        return;
      }
      let restoredUser = null;
      try {
        const payload = await api("/api/auth/me", {}, authToken);
        restoredUser = payload.user;
        setCurrentUser(payload.user);
        setMode("staff");
        if (location.pathname === "/" || location.pathname === "/login") navigateToView(IS_STAFF_APP ? "submissions" : "intake", { replace: true });
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
      navigateToView(IS_STAFF_APP ? "submissions" : "intake");
      await refreshAll();
      if (payload.user?.role === "admin") await loadStaff(payload.user, payload.accessToken);
    } catch (error) {
      setAuthError(true);
      setAuthMessage(error.message);
    }
  }

  function continuePatient() {
    if (IS_STAFF_APP) {
      navigateToView(authToken ? "submissions" : "login");
      return;
    }
    setMode("patient");
    setRoutingComplete(false);
    setShowAllForms(false);
    setRecommendedFormIds([]);
    setCompletedFormIds([]);
    clearAllDrafts();
    setDraftNotice(null);
    setServerResumeDraft(null);
    setSelectedFormId(null);
    navigateToView("welcome");
  }

  function enterStaffMode() {
    if (IS_PATIENT_APP) return;
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
    setMode(IS_STAFF_APP ? "staff" : "patient");
    setRoutingComplete(false);
    setShowAllForms(false);
    setRecommendedFormIds([]);
    setCompletedFormIds([]);
    clearAllDrafts();
    setDraftNotice(null);
    setServerResumeDraft(null);
    setSelectedFormId(null);
    navigateToView(IS_STAFF_APP ? "login" : "login");
  }

  function handleRoute(formData) {
    const ids = recommendFormsFromRouting(formData);
    setRecommendedFormIds(ids);
    setCompletedFormIds([]);
    setDraftNotice(null);
    setServerResumeDraft(null);
    setRoutingComplete(true);
    setShowAllForms(false);
    setSelectedFormId(ids[0] || null);
    navigateToView("intake");
  }

  function handleResumeLookup(resumeCode) {
    const normalizedCode = String(resumeCode || "").trim().toUpperCase();
    if (!normalizedCode) return;
    navigate(`/resume/${encodeURIComponent(normalizedCode)}`);
  }

  function showAllStaffForms() {
    if (IS_PATIENT_APP) return;
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

  function focusField(fieldId) {
    window.requestAnimationFrame(() => {
      const fieldElement = document.getElementById(`field_${fieldId}`);
      fieldElement?.focus();
      fieldElement?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  function handleAnswerChange(fieldId, value) {
    setCompletionNotice(null);
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
    setCompletionNotice(null);
    const progress = getFormProgress(selectedForm, answers, mode);
    if (progress.missingRequired.length) {
      const preview = progress.missingRequired.slice(0, 4).map((field) => field.label).join(", ");
      setFormError(true);
      setFormMessage(`Please complete ${progress.missingRequired.length} required field${progress.missingRequired.length === 1 ? "" : "s"} before submitting: ${preview}${progress.missingRequired.length > 4 ? ", and more" : ""}.`);
      focusField(progress.missingRequired[0].id);
      return;
    }
    try {
      const submittedFormId = selectedForm.id;
      const submissionAnswers = buildSubmissionAnswers(selectedForm, addCalculatedScores(submittedFormId, answers), mode);
      const resumeCode = draftNotice?.serverDraft && draftNotice.formId === submittedFormId ? draftNotice.resumeCode : "";
      const payload = resumeCode
        ? await api(`/api/patient-drafts/${encodeURIComponent(resumeCode)}/submit`, {
          method: "POST",
          body: JSON.stringify({ answers: submissionAnswers })
        }, "")
        : await api("/api/submissions", {
          method: "POST",
          body: JSON.stringify({ formId: submittedFormId, answers: submissionAnswers })
        }, authToken);
      removeDraftForForm(submittedFormId);
      const nextCompletedFormIds = [...new Set([...completedFormIds, submittedFormId])];
      const pendingRecommendedIds = recommendedFormIds.filter((id) => !nextCompletedFormIds.includes(id));
      const nextFormId = showAllForms ? submittedFormId : pendingRecommendedIds[0] || null;
      setCompletedFormIds(nextCompletedFormIds);
      setCompletionNotice({
        formName: payload.submission.formName,
        patientName: payload.submission.patientName,
        remainingCount: pendingRecommendedIds.length,
        nextFormName: forms.find((form) => form.id === pendingRecommendedIds[0])?.name || ""
      });
      setDraftNotice(null);
      setServerResumeDraft(null);
      setSelectedFormId(nextFormId || submittedFormId);
      setAnswers(initialAnswersForForm(forms.find((form) => form.id === (nextFormId || submittedFormId))));
      await loadSubmissions();
    } catch (error) {
      setFormError(true);
      setFormMessage([error.message, ...(error.details || [])].join(" "));
    }
  }

  const loadPatientResumeDraft = useCallback(async (resumeCode) => {
    setFormMessage("");
    setFormError(false);
    try {
      const payload = await api(`/api/patient-drafts/${encodeURIComponent(resumeCode)}`, {}, "");
      const form = payload.form;
      const draft = payload.draft;
      setForms((current) => current.some((item) => item.id === form.id) ? current : [...current, form]);
      setServerResumeDraft(draft);
      setMode("patient");
      setShowAllForms(false);
      setRoutingComplete(true);
      setRecommendedFormIds([draft.formId]);
      setCompletedFormIds([]);
      setSelectedFormId(draft.formId);
      setAnswers(addCalculatedScores(draft.formId, { ...initialAnswersForForm(form), ...(draft.answers || {}) }));
      setDraftNotice({
        formId: draft.formId,
        formName: draft.formName,
        savedAt: draft.updatedAt || draft.createdAt,
        restored: true,
        serverDraft: true,
        resumeCode: draft.resumeCode || resumeCode.toUpperCase(),
        resumeUrl: `${window.location.origin}/resume/${draft.resumeCode || resumeCode.toUpperCase()}`
      });
      navigateToView("intake", { replace: true });
    } catch (error) {
      setFormError(true);
      setFormMessage(error.message || "Unable to load that resume draft.");
      navigateToView("welcome", { replace: true });
    }
  }, [navigateToView]);

  async function savePatientResumeDraft() {
    if (!selectedForm) return;
    setResumeSaving(true);
    setFormMessage("");
    setFormError(false);
    try {
      const body = JSON.stringify({
        formId: selectedForm.id,
        answers: buildSubmissionAnswers(selectedForm, addCalculatedScores(selectedForm.id, answers), mode),
        status: "draft"
      });
      const resumeCode = draftNotice?.resumeCode;
      const payload = resumeCode
        ? await api(`/api/patient-drafts/${encodeURIComponent(resumeCode)}`, { method: "PATCH", body }, "")
        : await api("/api/patient-drafts", { method: "POST", body }, "");
      const serverDraft = payload.draft;
      setServerResumeDraft(serverDraft);
      setDraftNotice({
        formId: serverDraft.formId,
        formName: serverDraft.formName,
        savedAt: serverDraft.updatedAt || serverDraft.createdAt,
        restored: false,
        serverDraft: true,
        resumeCode: serverDraft.resumeCode,
        resumeUrl: `${window.location.origin}/resume/${serverDraft.resumeCode}`
      });
      setFormMessage(`Resume code saved: ${serverDraft.resumeCode}`);
    } catch (error) {
      setFormError(true);
      setFormMessage(error.message || "Unable to save resume draft.");
    } finally {
      setResumeSaving(false);
    }
  }

  const selectSubmission = useCallback(async (id) => {
    setSubmissionDetailLoading(true);
    try {
      const summary = submissions.find((item) => item.id === id);
      const payload = await api(`/api/submissions/${encodeURIComponent(id)}`, {}, authToken);
      setSelectedSubmission(enrichSubmission({ ...summary, ...payload.submission }));
      if (location.pathname !== `/submissions/${id}`) navigate(`/submissions/${id}`);
    } finally {
      setSubmissionDetailLoading(false);
    }
  }, [authToken, location.pathname, navigate, submissions]);

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

  async function recordSubmissionActivity(id, action, metadata = {}) {
    const payload = await api(`/api/submissions/${encodeURIComponent(id)}/audit-events`, {
      method: "POST",
      body: JSON.stringify({ action, metadata })
    }, authToken);
    const enriched = enrichSubmission(payload.submission);
    setSelectedSubmission(enriched);
    setSubmissions((current) => current.map((submission) => (submission.id === id ? { ...submission, ...enriched } : submission)));
    return enriched;
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

  async function saveTemplate(template, options = {}) {
    const payload = await api(`/api/forms/${encodeURIComponent(template.id)}`, {
      method: "PATCH",
      body: JSON.stringify({ template, publish: options.publish !== false })
    }, authToken);
    if (payload.form.status === "active") {
      setForms((current) => current.map((form) => (form.id === payload.form.id ? payload.form : form)));
      setTemplateDrafts((current) => current.filter((draft) => draft.id !== payload.form.id));
      setTemplateVersions((current) => ({ ...current, [payload.form.id]: [] }));
    } else if (payload.form.status === "draft") {
      setTemplateDrafts((current) => {
        const withoutCurrent = current.filter((draft) => draft.id !== payload.form.id);
        return [payload.form, ...withoutCurrent];
      });
      setTemplateVersions((current) => ({ ...current, [payload.form.id]: [] }));
    }
    return payload;
  }

  async function deleteTemplateDraft(formId) {
    await api(`/api/forms/${encodeURIComponent(formId)}/draft`, { method: "DELETE" }, authToken);
    setTemplateDrafts((current) => current.filter((draft) => draft.id !== formId));
    setTemplateVersions((current) => ({ ...current, [formId]: [] }));
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

  const welcomePage = (
    <WelcomePage
      onRoute={handleRoute}
      onShowAllForms={showAllStaffForms}
      onStartOver={continuePatient}
      onResumeDraft={handleResumeLookup}
      isStaff={isStaff && !IS_PATIENT_APP}
    />
  );

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
      completedFormIds={completedFormIds}
      answers={answers}
      mode={mode}
      onAnswerChange={handleAnswerChange}
      onSubmit={submitIntake}
      onClear={() => {
        setAnswers(initialAnswersForForm(selectedForm));
        setFormMessage("");
        setCompletionNotice(null);
        removeDraftForForm(selectedForm?.id);
        setDraftNotice(null);
        setServerResumeDraft(null);
        setFormError(false);
      }}
      onStartOver={continuePatient}
      message={formMessage}
      error={formError}
      completionNotice={completionNotice}
      draftNotice={draftNotice}
      resumeSaving={resumeSaving}
      onSaveResumeDraft={savePatientResumeDraft}
      onDiscardDraft={() => {
        removeDraftForForm(selectedForm?.id);
        setAnswers(initialAnswersForForm(selectedForm));
        setDraftNotice(null);
        setServerResumeDraft(null);
        setFormMessage("");
        setFormError(false);
      }}
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
      onRecordActivity={recordSubmissionActivity}
      onLoadMore={loadMoreSubmissions}
      hasMore={submissionsHasMore}
      onQueryChange={setSubmissionQuery}
    />
  ) : authReady ? <Navigate to="/login" replace /> : <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>;

  const templatesPage = authToken ? (
    <TemplatesPage
      forms={forms}
      templateDrafts={templateDrafts}
      templateVersions={templateVersions}
      user={currentUser}
      onSaveTemplate={saveTemplate}
      onLoadDrafts={loadTemplateDrafts}
      onLoadVersions={loadTemplateVersions}
      onDeleteDraft={deleteTemplateDraft}
    />
  ) : authReady ? <Navigate to="/login" replace /> : <div className="empty-state"><h2>Loading</h2><p>Checking your session.</p></div>;
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

  if (IS_PATIENT_APP && view === "login") return (
    <Routes>
      <Route path="/" element={<Navigate to="/start" replace />} />
      <Route path="/login" element={<Navigate to="/start" replace />} />
      <Route path="/start" element={welcomePage} />
      <Route path="*" element={<Navigate to="/start" replace />} />
    </Routes>
  );

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
      appMode={APP_MODE}
    >
      <Routes>
        <Route path="/" element={<Navigate to={IS_STAFF_APP ? (authToken ? "/submissions" : "/login") : authToken ? "/intake" : "/start"} replace />} />
        <Route path="/login" element={<Navigate to={authToken ? (IS_STAFF_APP ? "/submissions" : "/intake") : "/login"} replace />} />
        <Route path="/start" element={IS_STAFF_APP ? <Navigate to={authToken ? "/submissions" : "/login"} replace /> : welcomePage} />
        <Route path="/resume/:resumeCode" element={IS_STAFF_APP ? <Navigate to={authToken ? "/submissions" : "/login"} replace /> : <ResumeDraftRoute onLoadDraft={loadPatientResumeDraft} />} />
        <Route path="/intake" element={guardedIntakePage} />
        <Route path="/submissions" element={IS_PATIENT_APP ? <Navigate to="/start" replace /> : submissionsPage} />
        <Route path="/submissions/:submissionId" element={IS_PATIENT_APP ? <Navigate to="/start" replace /> : authToken ? (
          <SubmissionDetailRoute
            authToken={authToken}
            submissions={submissions}
            submissionsLoading={submissionsLoading}
            submissionDetailLoading={submissionDetailLoading}
            selectedSubmission={selectedSubmission}
            forms={forms}
            onSelect={selectSubmission}
            onStatusChange={updateSubmissionStatus}
            onRecordActivity={recordSubmissionActivity}
            onBack={() => navigateToView("submissions")}
          />
        ) : <Navigate to="/login" replace />} />
        <Route path="/templates" element={IS_PATIENT_APP ? <Navigate to="/start" replace /> : templatesPage} />
        <Route path="/staff" element={IS_PATIENT_APP ? <Navigate to="/start" replace /> : staffPage} />
        <Route path="*" element={<Navigate to={IS_STAFF_APP ? (authToken ? "/submissions" : "/login") : "/start"} replace />} />
      </Routes>
    </AppShell>
  );
}
