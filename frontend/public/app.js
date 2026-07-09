


function setAuthSession(payload) {
  state.authToken = payload.accessToken || "";
  state.currentUser = payload.user || null;
  if (state.authToken) {
    localStorage.setItem("pyam.authToken", state.authToken);
  } else {
    localStorage.removeItem("pyam.authToken");
  }
  renderAuthState();
}

function renderAuthState() {
  const isLoggedIn = Boolean(state.authToken && state.currentUser);
  const isAdmin = state.currentUser?.role === "admin";
  document.body.classList.toggle("admin-mode", isAdmin);
  els.authUser.textContent = isLoggedIn ? `${state.currentUser.email} - ${state.currentUser.role}` : "";
  els.authUser.classList.toggle("hidden", !isLoggedIn);
  els.logoutButton.classList.toggle("hidden", !isLoggedIn);
  document.querySelectorAll("[data-admin-only]").forEach((item) => {
    item.classList.toggle("hidden", !isAdmin);
  });
}

function showAuthDialog() {
  els.authMessage.textContent = "";
  els.authMessage.classList.remove("error");
  renderBootstrapState();
  document.body.classList.add("access-mode");
  setView("login");
  els.authEmail.focus();
}

function hideAuthDialog() {
  els.authForm.reset();
}

async function authenticate(mode = "login") {
  els.authMessage.textContent = "";
  els.authMessage.classList.remove("error");

  try {
    const payload = await api(`/api/auth/${mode === "register" ? "register" : "login"}`, {
      method: "POST",
      body: JSON.stringify({
        email: els.authEmail.value.trim(),
        password: els.authPassword.value,
        name: els.authName.value.trim() || undefined
      })
    });
    setAuthSession(payload);
    hideAuthDialog();
    state.mode = "staff";
    document.body.classList.remove("access-mode");
    applyMode();
    await loadSubmissions();
    if (state.currentUser?.role === "admin") await loadStaff();
    setView("intake");
  } catch (error) {
    els.authMessage.classList.add("error");
    els.authMessage.textContent = error.message;
  }
}

async function loadBootstrapState() {
  const payload = await api("/api/auth/bootstrap");
  state.needsFirstAdmin = Boolean(payload.needsFirstAdmin);
  renderBootstrapState();
}

function renderBootstrapState() {
  els.registerButton.classList.toggle("hidden", !state.needsFirstAdmin);
  els.authName.closest(".field").classList.toggle("hidden", !state.needsFirstAdmin);
  if (state.needsFirstAdmin) {
    els.registerButton.textContent = "Create First Admin";
  }
}

async function restoreAuthSession() {
  if (!state.authToken) {
    renderAuthState();
    return;
  }
  try {
    const payload = await api("/api/auth/me");
    state.currentUser = payload.user;
    state.mode = "staff";
  } catch {
    state.authToken = "";
    state.currentUser = null;
    localStorage.removeItem("pyam.authToken");
  }
  renderAuthState();
}

function setView(viewName) {
  if (viewName === "login") {
    document.body.classList.add("access-mode");
  }
  if (viewName === "staff" && state.currentUser?.role !== "admin") {
    viewName = state.mode === "staff" ? "intake" : "welcome";
  }
  if (state.mode === "patient" && ["submissions", "templates", "staff"].includes(viewName)) {
    viewName = "welcome";
  }
  if (viewName === "intake" && !state.routingComplete && !state.showAllForms) {
    viewName = "welcome";
  }
  els.navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  els.views.forEach((view) => {
    view.classList.toggle("active", view.id === `view-${viewName}`);
  });
  els.pageTitle.textContent =
    viewName === "login"
      ? "Welcome"
      : viewName === "submissions"
      ? "Submission Review"
      : viewName === "staff"
        ? "Staff Access"
      : viewName === "templates"
        ? "Template Library"
        : viewName === "welcome"
          ? "Start Intake"
          : "Patient Intake";
}

function applyMode() {
  const isStaff = state.mode === "staff";
  if (isStaff) document.body.classList.remove("access-mode");
  document.body.classList.toggle("staff-mode", isStaff);
  document.body.classList.toggle("patient-mode", !isStaff);
  els.viewModePill.textContent = isStaff ? "Staff view" : "Patient view";

  if (isStaff) {
    state.showAllForms = true;
    state.routingComplete = true;
    state.recommendedFormIds = state.forms.map((form) => form.id);
    state.selectedFormId = state.selectedFormId || state.forms[0]?.id || null;
  } else {
    state.showAllForms = false;
    const restrictedViewActive = ["submissions", "templates", "staff"].some((view) =>
      document.querySelector(`#view-${view}`)?.classList.contains("active")
    );
    if (restrictedViewActive) setView("welcome");
  }

  renderFormList();
  renderSelectedForm();
  renderAuthState();
}

function resetPatientFlow() {
  state.mode = "patient";
  document.body.classList.remove("access-mode");
  state.routingComplete = false;
  state.showAllForms = false;
  state.recommendedFormIds = [];
  state.selectedFormId = null;
  els.routingForm.reset();
  renderFormList();
  renderSelectedForm();
  setView("welcome");
}

function getSelectedForm() {
  return state.forms.find((form) => form.id === state.selectedFormId);
}

function calculateAge(dateOfBirth) {
  if (!dateOfBirth) return null;
  const birth = new Date(`${dateOfBirth}T00:00:00`);
  if (Number.isNaN(birth.getTime())) return null;
  const today = new Date();
  let years = today.getFullYear() - birth.getFullYear();
  let months = today.getMonth() - birth.getMonth();
  if (today.getDate() < birth.getDate()) months -= 1;
  if (months < 0) {
    years -= 1;
    months += 12;
  }
  const totalMonths = years * 12 + months;
  return { years, months, totalMonths };
}

function wellVisitFormId(age, location) {
  if (!age) return "well-child-visit";
  const months = age.totalMonths;
  if (months < 1) return "newborn-2-5-days";
  if (months < 2) return "1-month-visit";
  if (months < 4) return "2-months-visit";
  if (months < 6) return "4-months-visit";
  if (months < 7) return "6-months-visit";
  if (months < 9) return "7-8-months-visit";
  if (months < 10) return "9-months-visit";
  if (months < 12) return "10-months-visit";
  if (months < 14) return location === "maplewood" ? "12-months-visit-maplewood" : "12-months-visit-eagan";
  if (months < 15) return "14-months-visit";
  if (months < 18) return "15-months-visit";
  if (months < 20) return "18-months-visit";
  if (months < 22) return "20-months-visit";
  if (months < 24) return "22-months-visit";
  if (months < 27) return location === "maplewood" ? "2-year-visit-maplewood" : "2-year-visit-eagan";
  if (months < 30) return "27-months-visit";
  if (months < 33) return "30-months-visit";
  if (months < 36) return "33-months-visit";
  if (months < 42) return "3-year-visit";
  if (months < 48) return "42-months-visit";
  if (months < 54) return "4-year-visit";
  if (months < 60) return "54-months-visit";
  if (months < 72) return "5-year-visit";
  const year = age.years;
  if (year <= 6) return "6-year-visit";
  if (year <= 7) return "7-year-visit";
  if (year <= 8) return "8-year-visit";
  if (year <= 9) return "9-year-visit";
  if (year <= 10) return "10-year-visit";
  if (year <= 11) return "11-year-visit";
  if (year <= 12) return "12-year-visit";
  if (year <= 14) return "13-14-year-visit";
  if (year <= 17) return "15-17-year-visit";
  if (year <= 21) return "18-21-year-visit";
  return "well-child-visit";
}

function portalFormId(age) {
  if (!age) return "patient-portal-18-plus";
  if (age.years < 12) return "patient-portal-under-11";
  if (age.years < 18) return "patient-portal-12-17";
  return "patient-portal-18-plus";
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function recommendFormsFromRouting(formData) {
  const age = calculateAge(formData.get("dateOfBirth"));
  const visitType = formData.get("visitType");
  const location = formData.get("location");
  const extras = formData.getAll("extras");
  const ids = [];

  if (visitType === "well") ids.push(wellVisitFormId(age, location));
  if (visitType === "portal") ids.push(portalFormId(age));
  if (visitType === "records") ids.push("roi-2026");
  if (visitType === "asthma") ids.push(age && age.years < 12 ? "child-act-4-11" : "asthma-act-12-plus");
  if (visitType === "injury") ids.push("acute-concussion-evaluation");
  if (visitType === "procedure") ids.push("wart-consent");

  if (visitType === "behavioral" || extras.includes("adhd")) {
    ids.push(age && age.years >= 18 ? "adult-adhd-asrs" : "vanderbilt-parent");
  }
  if (extras.includes("teacher")) {
    ids.push("vanderbilt-teacher");
  }
  if (extras.includes("anxiety")) {
    ids.push("initial-anxiety-6-12");
  }
  if (extras.includes("asthma") && visitType !== "asthma") {
    ids.push(age && age.years < 12 ? "child-act-4-11" : "asthma-act-12-plus");
  }

  return unique(ids);
}

function renderFormList() {
  const query = els.formSearch.value.trim().toLowerCase();
  const baseForms = state.showAllForms
    ? state.forms
    : state.forms.filter((form) => state.recommendedFormIds.includes(form.id));
  const forms = baseForms.filter((form) => [form.name, form.category, form.description].join(" ").toLowerCase().includes(query));

  els.formListTitle.textContent = state.showAllForms ? "All Forms" : "Recommended Forms";
  els.formListDescription.textContent = state.showAllForms
    ? "Staff view is active. All available forms are visible."
    : state.routingComplete
      ? `${forms.length} form${forms.length === 1 ? "" : "s"} matched this intake.`
      : "Complete the start questions above to see the right forms.";

  if (!forms.length) {
    els.formList.innerHTML = `
      <div class="empty-state compact-empty">
        <h2>${state.routingComplete ? "No matching forms" : "Start above"}</h2>
        <p>${state.routingComplete ? "Adjust the start questions or use staff override." : "Patients will only see forms after routing."}</p>
      </div>
    `;
    return;
  }

  els.formList.innerHTML = forms
    .map(
      (form) => `
        <button class="form-card ${form.id === state.selectedFormId ? "active" : ""}" data-form-id="${form.id}" type="button">
          <strong>${escapeHtml(form.name)}</strong>
          <span>${escapeHtml(form.category)} - ${form.estimatedMinutes} min</span>
        </button>
      `
    )
    .join("");
}


function renderField(field) {
  const required = field.required ? '<span class="required" aria-hidden="true">*</span>' : "";
  const common = `id="${fieldName(field)}" name="${field.id}" ${field.required ? "required" : ""}`;
  const staffOnly = isStaffOnlyField(field) ? " data-staff-only" : "";

  if (["text", "email", "tel", "date", "number", "datetime-local"].includes(field.type)) {
    return `
      <div class="field"${staffOnly}>
        <label for="${fieldName(field)}">${escapeHtml(field.label)} ${required}</label>
        <input class="field-control" ${common} type="${field.type}">
      </div>
    `;
  }

  if (field.type === "signature") {
    return `
      <div class="field"${staffOnly}>
        <label for="${fieldName(field)}">${escapeHtml(field.label)} ${required}</label>
        <input class="field-control" ${common} type="text" placeholder="Type full legal name">
      </div>
    `;
  }

  if (field.type === "textarea") {
    return `
      <div class="field full"${staffOnly}>
        <label for="${fieldName(field)}">${escapeHtml(field.label)} ${required}</label>
        <textarea class="field-control" ${common}></textarea>
      </div>
    `;
  }

  if (field.type === "select") {
    return `
      <div class="field"${staffOnly}>
        <label for="${fieldName(field)}">${escapeHtml(field.label)} ${required}</label>
        <select class="field-control" ${common}>
          <option value="">Select</option>
          ${(field.options || []).map((option) => `<option value="${escapeHtml(option)}">${escapeHtml(option)}</option>`).join("")}
        </select>
      </div>
    `;
  }

  if (field.type === "checkbox") {
    return `
      <div class="field full"${staffOnly}>
        <label class="choice-option">
          <input type="checkbox" name="${field.id}" ${field.required ? "required" : ""}>
          <span>${escapeHtml(field.label)} ${required}</span>
        </label>
      </div>
    `;
  }

  if (field.type === "radio" || field.type === "multicheck") {
    const inputType = field.type === "radio" ? "radio" : "checkbox";
    return `
      <div class="field full"${staffOnly}>
        <span class="choice-label">${escapeHtml(field.label)} ${required}</span>
        <div class="choice-group">
          ${(field.options || [])
            .map(
              (option) => `
                <label class="choice-option">
                  <input type="${inputType}" name="${field.id}" value="${escapeHtml(option)}" ${field.required ? "required" : ""}>
                  <span>${escapeHtml(option)}</span>
                </label>
              `
            )
            .join("")}
        </div>
      </div>
    `;
  }

  if (field.type === "scale") {
    return `
      <div class="field full"${staffOnly}>
        <span class="choice-label">${escapeHtml(field.label)} ${required}</span>
        <div class="scale-group">
          ${(field.options || [])
            .map(
              (option, index) => `
                <label class="scale-option">
                  <input type="radio" name="${field.id}" value="${escapeHtml(option)}" data-score="${index + 1}" ${field.required ? "required" : ""}>
                  <span>${escapeHtml(option)}</span>
                </label>
              `
            )
            .join("")}
        </div>
      </div>
    `;
  }

  return "";
}

function renderContentItem(item) {
  if (!item) return "";
  const variant = item.variant ? ` ${item.variant}` : "";
  const title = item.title ? `<strong>${escapeHtml(item.title)}</strong>` : "";
  const text = item.text ? `<p>${escapeHtml(item.text)}</p>` : "";
  const link = item.url
    ? `<a class="content-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.linkLabel || "Open source packet")}</a>`
    : "";
  const list = Array.isArray(item.items)
    ? `<ul>${item.items.map((entry) => `<li>${escapeHtml(entry)}</li>`).join("")}</ul>`
    : "";

  if (item.type === "heading") {
    return `<h4 class="content-heading">${escapeHtml(item.text || item.title || "")}</h4>`;
  }

  return `<div class="content-block${variant}">${title}${text}${list}${link}</div>`;
}


function renderSection(section) {
  const content = (section.content || []).map(renderContentItem).join("");
  const fields = (section.fields || [])
    .filter((field) => !isRepeatedDemographicField(field, section.title))
    .map(renderField)
    .join("");
  const staffOnly = section.staffOnly ? " data-staff-only" : "";

  return `
    <section class="form-section"${staffOnly}>
      <h3>${escapeHtml(section.title)}</h3>
      ${content ? `<div class="section-content">${content}</div>` : ""}
      ${fields ? `<div class="field-grid">${fields}</div>` : ""}
    </section>
  `;
}

function renderSelectedForm() {
  const form = getSelectedForm();
  if (!form) {
    els.selectedEmpty.classList.remove("hidden");
    els.intakeForm.classList.add("hidden");
    return;
  }

  els.selectedEmpty.classList.add("hidden");
  els.intakeForm.classList.remove("hidden");
  els.intakeForm.reset();
  els.selectedCategory.textContent = form.category;
  els.selectedName.textContent = form.name;
  els.selectedDescription.textContent = form.description;
  els.selectedTime.textContent = `${form.estimatedMinutes} min`;
  els.formMessage.textContent = "";
  els.formMessage.classList.remove("error");

  els.formSections.innerHTML = `${renderAsqScoreTable(form.id)}${form.sections.map(renderSection).join("")}`;
  syncAsqScores();
}

function collectAnswers(form) {
  const answers = {};

  for (const section of form.sections) {
    for (const field of section.fields || []) {
      if (isRepeatedDemographicField(field, section.title)) continue;
      if (!document.body.classList.contains("staff-mode") && isStaffOnlyField(field)) continue;
      const controls = [...els.intakeForm.querySelectorAll(`[name="${CSS.escape(field.id)}"]`)];
      if (!controls.length) continue;

      if (field.type === "checkbox") {
        answers[field.id] = controls[0].checked;
      } else if (field.type === "multicheck") {
        answers[field.id] = controls.filter((control) => control.checked).map((control) => control.value);
      } else if (["radio", "scale"].includes(field.type)) {
        const selected = controls.find((control) => control.checked);
        answers[field.id] = selected ? selected.value : "";
      } else {
        answers[field.id] = controls[0].value.trim();
      }
    }
  }

  for (const section of form.sections) {
    for (const field of section.fields || []) {
      if (!isRepeatedDemographicField(field, section.title)) continue;
      answers[field.id] = demographicAutofillValue(field, answers);
    }
  }

  return answers;
}


async function submitIntake(event) {
  event.preventDefault();
  const form = getSelectedForm();
  if (!form) return;

  els.formMessage.textContent = "";
  els.formMessage.classList.remove("error");

  try {
    const payload = await api("/api/submissions", {
      method: "POST",
      body: JSON.stringify({ formId: form.id, answers: collectAnswers(form) })
    });
    els.formMessage.textContent = `Saved ${payload.submission.formName} for ${payload.submission.patientName}.`;
    els.intakeForm.reset();
    await loadSubmissions();
  } catch (error) {
    els.formMessage.classList.add("error");
    els.formMessage.textContent = [error.message, ...(error.details || [])].join(" ");
  }
}

function renderSubmissions() {
  const submissions = state.submissions.filter((submission) => {
    const statusMatch = state.statusFilter ? submission.status === state.statusFilter : true;
    const review = submission.review || { flags: [] };
    const reviewMatch =
      !state.reviewFilter ||
      review.status === state.reviewFilter ||
      review.flags.some((flag) => flag.type === state.reviewFilter || flag.key === state.reviewFilter);
    return statusMatch && reviewMatch;
  });

  if (els.reviewTabs) {
    els.reviewTabs.querySelectorAll("[data-review-filter]").forEach((button) => {
      button.classList.toggle("active", button.dataset.reviewFilter === state.reviewFilter);
    });
  }

  if (!submissions.length) {
    els.submissionList.innerHTML = '<div class="empty-state"><h2>No submissions</h2><p>Submitted intakes will appear here.</p></div>';
    return;
  }

  els.submissionList.innerHTML = submissions
    .map(
      (submission) => `
        <button class="submission-card ${submission.id === state.selectedSubmissionId ? "active" : ""}" data-submission-id="${submission.id}" type="button">
          <div class="submission-title-row">
            <strong>${escapeHtml(submission.patientName)}</strong>
            <span class="review-badge ${escapeHtml(submission.review?.status || "routine")}">${escapeHtml(submission.review?.label || "Routine")}</span>
          </div>
          <span>${escapeHtml(submission.formName)}</span>
          <div class="template-meta">
            <span>${new Date(submission.createdAt).toLocaleString()}</span>
            <span class="status-badge">${escapeHtml(submission.status.replaceAll("-", " "))}</span>
          </div>
          ${
            submission.review?.flags?.length
              ? `<div class="review-flag-list">${submission.review.flags
                  .slice(0, 3)
                  .map((flag) => `<span class="review-flag ${escapeHtml(flag.severity)}">${escapeHtml(flag.label)}</span>`)
                  .join("")}</div>`
              : ""
          }
        </button>
      `
    )
    .join("");
}

async function renderSubmissionDetail(id) {
  if (!id) return;
  state.selectedSubmissionId = id;
  renderSubmissions();

  const { submission } = await api(`/api/submissions/${encodeURIComponent(id)}`);
  const enrichedSubmission = enrichSubmission(submission);
  const form = state.forms.find((item) => item.id === submission.formId);
  const fields = form ? form.sections.flatMap((section) => (section.fields || []).map((field) => ({ ...field, section: section.title }))) : [];
  const fieldMap = new Map(fields.map((field) => [field.id, field]));

  const rows = Object.entries(submission.answers)
    .filter(([key]) => {
      const field = fieldMap.get(key);
      return !field || !isRepeatedDemographicField(field, field.section);
    })
    .map(([key, value]) => {
      const field = fieldMap.get(key);
      const label = field ? field.label : key;
      const displayValue = Array.isArray(value) ? value.join(", ") : value === true ? "Yes" : value === false ? "No" : value || "Not provided";
      const owner = field ? fieldOwner(field, field.section) : "patient";
      return `
        <div class="answer-row">
          <strong>${escapeHtml(label)} <span class="field-owner ${escapeHtml(owner)}">${escapeHtml(owner)}</span></strong>
          <span>${escapeHtml(displayValue)}</span>
        </div>
      `;
    })
    .join("");

  els.submissionDetail.innerHTML = `
    <div class="detail-header">
      <div>
        <p class="eyebrow">${escapeHtml(submission.category)}</p>
        <h2>${escapeHtml(submission.patientName)}</h2>
        <p>${escapeHtml(submission.formName)} - ${new Date(submission.createdAt).toLocaleString()}</p>
      </div>
      <select class="select-input" id="detail-status" aria-label="Submission status">
        ${["new", "in-review", "needs-follow-up", "complete"]
          .map((status) => `<option value="${status}" ${status === submission.status ? "selected" : ""}>${status.replaceAll("-", " ")}</option>`)
          .join("")}
      </select>
    </div>
    <section class="review-panel ${escapeHtml(enrichedSubmission.review.status)}">
      <div>
        <p class="eyebrow">Review status</p>
        <h3>${escapeHtml(enrichedSubmission.review.label)}</h3>
      </div>
      ${
        enrichedSubmission.review.flags.length
          ? `<div class="review-flag-list">${enrichedSubmission.review.flags
              .map((flag) => `<span class="review-flag ${escapeHtml(flag.severity)}">${escapeHtml(flag.label)}</span>`)
              .join("")}</div>`
          : `<span class="review-flag low">No automatic flags</span>`
      }
    </section>
    ${renderAsqSubmissionScoreTable(submission.formId, submission.answers)}
    <div class="answer-list">${rows}</div>
  `;

  document.querySelector("#detail-status").addEventListener("change", async (event) => {
    await api(`/api/submissions/${encodeURIComponent(submission.id)}`, {
      method: "PATCH",
      body: JSON.stringify({ status: event.target.value })
    });
    await loadSubmissions();
    await renderSubmissionDetail(submission.id);
  });
}

function renderTemplates() {
  els.templateGrid.innerHTML = state.forms
    .map((form) => {
      const fieldCount = form.sections.reduce((count, section) => count + (section.fields || []).length, 0);
      const contentCount = form.sections.reduce((count, section) => count + (section.content || []).length, 0);
      return `
        <article class="template-card">
          <strong>${escapeHtml(form.name)}</strong>
          <span>${escapeHtml(form.description)}</span>
          <div class="template-meta">
            <span>${escapeHtml(form.category)}</span>
            <span>${fieldCount} fields - ${contentCount} notes</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderStaff() {
  if (!state.staffUsers.length) {
    els.staffList.innerHTML = '<div class="empty-state compact-empty"><h2>No users yet</h2><p>Create the first staff account from the form.</p></div>';
    return;
  }

  els.staffList.innerHTML = state.staffUsers
    .map(
      (user) => `
        <article class="staff-card">
          <div>
            <strong>${escapeHtml(user.name || user.email)}</strong>
            <span>${escapeHtml(user.email)}</span>
          </div>
          <div class="staff-card-meta">
            <span class="status-badge">${escapeHtml(user.role)}</span>
            <span>${escapeHtml(user.title || "No title")}</span>
            <span>${escapeHtml(user.clinicLocation || "All locations")}</span>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadStaff() {
  if (state.currentUser?.role !== "admin") {
    state.staffUsers = [];
    renderStaff();
    return;
  }
  const payload = await api("/api/staff");
  state.staffUsers = payload.staff;
  renderStaff();
}

async function submitStaff(event) {
  event.preventDefault();
  els.staffMessage.textContent = "";
  els.staffMessage.classList.remove("error");
  const formData = new FormData(els.staffForm);

  try {
    const payload = await api("/api/staff", {
      method: "POST",
      body: JSON.stringify({
        name: formData.get("name"),
        email: formData.get("email"),
        password: formData.get("password"),
        role: formData.get("role"),
        title: formData.get("title") || undefined,
        clinicLocation: formData.get("clinicLocation") || undefined
      })
    });
    els.staffMessage.textContent = `Created ${payload.user.role} account for ${payload.user.email}.`;
    els.staffForm.reset();
    await loadStaff();
  } catch (error) {
    els.staffMessage.classList.add("error");
    els.staffMessage.textContent = error.message;
  }
}

async function loadForms() {
  const payload = await api("/api/forms");
  state.forms = payload.forms;
  if (state.mode === "staff") {
    state.showAllForms = true;
    state.routingComplete = true;
    state.recommendedFormIds = state.forms.map((form) => form.id);
  }
  if (state.showAllForms && !state.selectedFormId && state.forms.length) state.selectedFormId = state.forms[0].id;
  renderFormList();
  renderSelectedForm();
  renderTemplates();
}

async function loadSubmissions() {
  if (!state.authToken) {
    state.submissions = [];
    renderSubmissions();
    return;
  }
  const payload = await api("/api/submissions");
  const detailed = await Promise.all(
    payload.submissions.map(async (submission) => {
      try {
        const detail = await api(`/api/submissions/${encodeURIComponent(submission.id)}`);
        return enrichSubmission({ ...submission, answers: detail.submission.answers || {} });
      } catch {
        return enrichSubmission(submission);
      }
    })
  );
  state.submissions = detailed;
  renderSubmissions();
}

async function checkHealth() {
  try {
    await api("/api/health");
    els.healthPill.textContent = "Server online";
  } catch {
    els.healthPill.textContent = "Server offline";
  }
}

async function refreshAll() {
  await checkHealth();
  await loadBootstrapState();
  await loadForms();
  await loadSubmissions();
  await loadStaff();
}

els.navButtons.forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
els.refreshButton.addEventListener("click", refreshAll);
els.staffModeButton.addEventListener("click", () => {
  if (!state.authToken) {
    showAuthDialog();
    return;
  }
  state.mode = "staff";
  applyMode();
  setView("intake");
});
els.patientModeButton.addEventListener("click", () => {
  resetPatientFlow();
  applyMode();
});
els.logoutButton.addEventListener("click", () => {
  setAuthSession({ accessToken: "", user: null });
  state.mode = "patient";
  state.routingComplete = false;
  state.showAllForms = false;
  state.recommendedFormIds = [];
  state.selectedFormId = null;
  applyMode();
  showAuthDialog();
});
els.authForm.addEventListener("submit", (event) => {
  event.preventDefault();
  authenticate("login");
});
els.registerButton.addEventListener("click", () => authenticate("register"));
els.continuePatientButton.addEventListener("click", () => {
  resetPatientFlow();
  applyMode();
  setView("welcome");
});
els.startOverButton.addEventListener("click", () => {
  resetPatientFlow();
  applyMode();
});
els.routingForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(els.routingForm);
  state.recommendedFormIds = recommendFormsFromRouting(formData);
  state.routingComplete = true;
  state.showAllForms = false;
  state.selectedFormId = state.recommendedFormIds[0] || null;
  renderFormList();
  renderSelectedForm();
  setView("intake");
});
els.showAllForms.addEventListener("click", () => {
  if (!state.authToken) {
    showAuthDialog();
    return;
  }
  state.mode = "staff";
  state.showAllForms = true;
  state.routingComplete = true;
  state.recommendedFormIds = state.forms.map((form) => form.id);
  state.selectedFormId = state.selectedFormId || state.forms[0]?.id || null;
  renderFormList();
  renderSelectedForm();
  setView("intake");
});
els.formSearch.addEventListener("input", renderFormList);
els.formList.addEventListener("click", (event) => {
  const card = event.target.closest("[data-form-id]");
  if (!card) return;
  state.selectedFormId = card.dataset.formId;
  renderFormList();
  renderSelectedForm();
});
els.intakeForm.addEventListener("change", syncAsqScores);
els.intakeForm.addEventListener("input", syncAsqScores);
els.intakeForm.addEventListener("submit", submitIntake);
els.clearForm.addEventListener("click", () => {
  els.intakeForm.reset();
  syncAsqScores();
  els.formMessage.textContent = "";
  els.formMessage.classList.remove("error");
});
els.statusFilter.addEventListener("change", () => {
  state.statusFilter = els.statusFilter.value;
  renderSubmissions();
});
els.reviewTabs?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-review-filter]");
  if (!button) return;
  state.reviewFilter = button.dataset.reviewFilter;
  renderSubmissions();
});
els.submissionList.addEventListener("click", (event) => {
  const card = event.target.closest("[data-submission-id]");
  if (card) renderSubmissionDetail(card.dataset.submissionId);
});
els.staffForm.addEventListener("submit", submitStaff);

restoreAuthSession()
  .then(() => refreshAll())
  .then(() => {
    applyMode();
    if (state.currentUser) {
      setView("intake");
    } else {
      setView("login");
    }
  });

