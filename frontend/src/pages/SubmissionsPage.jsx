import { useEffect, useState } from "react";
import { FormField } from "../components/fields/FormField";
import { fieldOwner, isCalculatedStaffField, isRepeatedDemographicField, isStaffOnlyField } from "../features/forms/fieldMeta";
import { AsqScoreTable } from "../features/scoring/AsqScoreTable";
import { addCalculatedScores } from "../features/scoring/calculatedScores";
import { scoreInsightsForSubmission } from "../features/scoring/scoreInsights";

function displayAnswer(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value === true) return "Yes";
  if (value === false) return "No";
  return value || "Not provided";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function reviewCounts(submissions) {
  return submissions.reduce((counts, submission) => {
    const flags = submission.review?.flags || [];
    counts.total += 1;
    counts.needsReview += submission.review?.status === "needs-review" ? 1 : 0;
    counts.high += flags.filter((flag) => flag.severity === "high").length;
    counts.medium += flags.filter((flag) => flag.severity === "medium").length;
    counts.new += submission.status === "new" ? 1 : 0;
    counts.followUp += submission.status === "needs-follow-up" ? 1 : 0;
    counts.complete += submission.status === "complete" ? 1 : 0;
    return counts;
  }, { total: 0, needsReview: 0, high: 0, medium: 0, new: 0, followUp: 0, complete: 0 });
}

function ScoreInsights({ insights }) {
  if (!insights.length) return null;
  return (
    <section className="score-insights-panel">
      <div className="score-panel-header">
        <div>
          <p className="eyebrow">Score explanations</p>
          <h3>Calculated interpretation</h3>
        </div>
      </div>
      <div className="score-insight-grid">
        {insights.map((insight) => (
          <article className={`score-insight ${insight.status}`} key={insight.key}>
            <div>
              <strong>{insight.label}</strong>
              <span>{insight.value}</span>
            </div>
            <p>{insight.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatAuditAction(action) {
  const labels = {
    created: "Submission created",
    submission_created: "Submission created",
    updated: "Submission updated",
    submission_updated: "Submission updated",
    status_changed: "Status changed",
    staff_review_updated: "Staff review updated"
  };
  return labels[action] || String(action || "Activity").replaceAll("_", " ");
}

function actorLabel(event) {
  if (event.actorRole === "patient" || event.by === "patient") return "Patient";
  return event.actorName || event.actorEmail || event.by || event.actorId || "Staff user";
}

function AuditHistory({ events = [] }) {
  const orderedEvents = [...events].sort((a, b) => String(b.at || "").localeCompare(String(a.at || "")));
  if (!orderedEvents.length) return null;

  return (
    <section className="audit-panel">
      <div className="detail-header compact-detail-header">
        <div>
          <p className="eyebrow">Audit history</p>
          <h3>Record activity</h3>
        </div>
        <span className="audit-count">{orderedEvents.length} events</span>
      </div>
      <div className="audit-timeline">
        {orderedEvents.map((event, index) => {
          const metadata = event.metadata || {};
          const changedCount = metadata.changedAnswerCount ?? (event.answersUpdated ? 1 : 0);
          return (
            <article className="audit-event" key={event.id || `${event.at}-${index}`}>
              <div className="audit-marker" />
              <div>
                <div className="audit-event-header">
                  <strong>{formatAuditAction(event.action)}</strong>
                  <span>{event.at ? new Date(event.at).toLocaleString() : "No timestamp"}</span>
                </div>
                <p>{actorLabel(event)}{event.actorRole ? ` - ${event.actorRole}` : ""}</p>
                {metadata.previousStatus || metadata.newStatus ? (
                  <small>Status: {String(metadata.previousStatus || "new").replaceAll("-", " ")} to {String(metadata.newStatus || metadata.previousStatus || "new").replaceAll("-", " ")}</small>
                ) : null}
                {changedCount ? <small>{changedCount} response field{changedCount === 1 ? "" : "s"} changed</small> : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function exportSubmissionPdf({ submission, form, answers, staffFields, fieldMap, insights }) {
  const rows = Object.entries(answers)
    .filter(([key]) => {
      const field = fieldMap.get(key);
      return !field || !isRepeatedDemographicField(field, field.section);
    })
    .map(([key, value]) => {
      const field = fieldMap.get(key);
      return `<tr><th>${escapeHtml(field?.label || key)}</th><td>${escapeHtml(displayAnswer(value))}</td></tr>`;
    })
    .join("");
  const insightRows = insights.map((insight) => `<tr><th>${escapeHtml(insight.label)}</th><td><strong>${escapeHtml(insight.value)}</strong><br>${escapeHtml(insight.detail)}</td></tr>`).join("");
  const staffRows = staffFields.map((field) => `<tr><th>${escapeHtml(field.label)}</th><td>${escapeHtml(displayAnswer(answers[field.id]))}</td></tr>`).join("");
  const flagRows = (submission.review?.flags || []).map((flag) => `<span class="flag ${escapeHtml(flag.severity)}">${escapeHtml(flag.label)}</span>`).join("") || "<span class=\"flag low\">No automatic flags</span>";
  const report = `<!doctype html>
    <html><head><title>${escapeHtml(submission.patientName)} - Intake Summary</title>
    <style>
      body{font-family:Arial,sans-serif;color:#17213a;margin:32px;line-height:1.45}
      h1,h2{margin:0 0 8px} h2{margin-top:28px;font-size:18px;border-bottom:1px solid #d6dfed;padding-bottom:8px}
      .meta{color:#53657f;margin-bottom:18px}.flag{display:inline-block;margin:4px 6px 4px 0;padding:4px 9px;border-radius:999px;background:#e7edf7;font-size:12px}
      .flag.high{background:#f7d4d7;color:#8f1d2a}.flag.medium{background:#ffe8a8;color:#76510a}.flag.low{background:#dff3e7;color:#2c6b42}
      table{width:100%;border-collapse:collapse;margin-top:10px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #e5ebf4;padding:8px 10px}th{width:36%;color:#344765}
      @media print{button{display:none}body{margin:18px}}
    </style></head>
    <body>
      <button onclick="window.print()">Print / save PDF</button>
      <h1>${escapeHtml(submission.patientName)}</h1>
      <div class="meta">${escapeHtml(submission.formName)} | ${escapeHtml(new Date(submission.createdAt).toLocaleString())} | Status: ${escapeHtml(submission.status.replaceAll("-", " "))}</div>
      <h2>Review Flags</h2><div>${flagRows}</div>
      <h2>Score Explanations</h2><table>${insightRows || "<tr><td>No calculated scoring insights.</td></tr>"}</table>
      <h2>Staff Review Fields</h2><table>${staffRows || "<tr><td>No staff-only fields.</td></tr>"}</table>
      <h2>Submitted Answers</h2><table>${rows}</table>
    </body></html>`;
  const win = window.open("", "_blank", "width=960,height=720");
  if (!win) return;
  win.document.write(report);
  win.document.close();
  win.focus();
}

export function SubmissionsPage({ submissions, isLoading, detailLoading, selectedSubmission, forms, onSelect, onStatusChange }) {
  const [statusFilter, setStatusFilter] = useState("");
  const [reviewFilter, setReviewFilter] = useState("");
  const [staffDraft, setStaffDraft] = useState({});
  const [staffSaving, setStaffSaving] = useState(false);
  const [staffMessage, setStaffMessage] = useState("");
  const visibleSubmissions = submissions.filter((submission) => {
    const statusMatch = statusFilter ? submission.status === statusFilter : true;
    const review = submission.review || { flags: [] };
    const reviewMatch =
      !reviewFilter ||
      review.status === reviewFilter ||
      review.flags.some((flag) => flag.type === reviewFilter || flag.key === reviewFilter);
    return statusMatch && reviewMatch;
  });

  const selectedForm = selectedSubmission ? forms.find((form) => form.id === selectedSubmission.formId) : null;
  const selectedAnswers = selectedSubmission ? addCalculatedScores(selectedSubmission.formId, selectedSubmission.answers || {}) : {};
  const selectedInsights = selectedSubmission ? scoreInsightsForSubmission(selectedSubmission, selectedForm, selectedAnswers) : [];
  const selectedAuditEvents = selectedSubmission?.auditHistory || selectedSubmission?.audit || [];
  const dashboardCounts = reviewCounts(submissions);
  const priorityQueue = submissions
    .filter((submission) => submission.review?.status === "needs-review" || submission.status === "needs-follow-up")
    .slice(0, 5);
  const staffFields = (selectedForm?.sections || []).flatMap((section) =>
    (section.fields || [])
      .filter((field) => !isRepeatedDemographicField(field, section.title) && isStaffOnlyField(field))
      .map((field) => ({ ...field, section: section.title }))
  );
  const fieldMap = new Map(
    (selectedForm?.sections || []).flatMap((section) =>
      (section.fields || []).map((field) => [field.id, { ...field, section: section.title }])
    )
  );

  useEffect(() => {
    setStaffDraft(selectedAnswers);
    setStaffMessage("");
  }, [selectedSubmission]);

  async function saveStaffReview() {
    if (!selectedSubmission) return;
    setStaffSaving(true);
    setStaffMessage("");
    try {
      await onStatusChange(selectedSubmission.id, selectedSubmission.status, staffDraft);
      setStaffMessage("Staff review responses saved.");
    } catch (error) {
      setStaffMessage(error.message || "Unable to save staff review responses.");
    } finally {
      setStaffSaving(false);
    }
  }

  function handleExportPdf() {
    if (!selectedSubmission) return;
    exportSubmissionPdf({ submission: selectedSubmission, form: selectedForm, answers: selectedAnswers, staffFields, fieldMap, insights: selectedInsights });
  }

  return (
    <section className="view active" aria-label="Submissions">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Submissions</h2>
            <p>Review locally stored intake records.</p>
          </div>
          <div className="submission-controls">
            <div className="review-tabs" aria-label="Review filters">
              {[
                ["", "All"],
                ["needs-review", "Needs review"],
                ["asq", "ASQ flags"],
                ["behavioral", "Behavioral"]
              ].map(([value, label]) => (
                <button className={`review-tab ${reviewFilter === value ? "active" : ""}`} key={value} onClick={() => setReviewFilter(value)} type="button">{label}</button>
              ))}
            </div>
            <select className="select-input" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="">All statuses</option>
              <option value="new">New</option>
              <option value="in-review">In review</option>
              <option value="needs-follow-up">Needs follow-up</option>
              <option value="complete">Complete</option>
            </select>
          </div>
        </div>

        <section className="staff-dashboard">
          <div className="dashboard-stat urgent">
            <span>{dashboardCounts.needsReview}</span>
            <strong>Needs review</strong>
            <p>{dashboardCounts.high} high priority flags</p>
          </div>
          <div className="dashboard-stat">
            <span>{dashboardCounts.new}</span>
            <strong>New</strong>
            <p>Awaiting staff review</p>
          </div>
          <div className="dashboard-stat">
            <span>{dashboardCounts.followUp}</span>
            <strong>Follow-up</strong>
            <p>Marked for next action</p>
          </div>
          <div className="dashboard-stat complete">
            <span>{dashboardCounts.complete}</span>
            <strong>Complete</strong>
            <p>{dashboardCounts.total} total submissions</p>
          </div>
          <div className="priority-queue">
            <div>
              <p className="eyebrow">Priority queue</p>
              <strong>Review next</strong>
            </div>
            {priorityQueue.length ? priorityQueue.map((submission) => (
              <button key={submission.id} type="button" onClick={() => onSelect(submission.id)}>
                <span>{submission.patientName}</span>
                <small>{submission.review?.flags?.[0]?.label || submission.status.replaceAll("-", " ")}</small>
              </button>
            )) : <p>No priority submissions right now.</p>}
          </div>
        </section>

        <div className="submission-layout">
          <div className="submission-list">
            {isLoading ? (
              <div className="empty-state"><h2>Loading submissions</h2><p>Pulling the latest intake records.</p></div>
            ) : visibleSubmissions.length ? visibleSubmissions.map((submission) => (
              <button className={`submission-card ${submission.id === selectedSubmission?.id ? "active" : ""}`} key={submission.id} onClick={() => onSelect(submission.id)} type="button">
                <div className="submission-title-row">
                  <strong>{submission.patientName}</strong>
                  <span className={`review-badge ${submission.review?.status || "routine"}`}>{submission.review?.label || "Routine"}</span>
                </div>
                <span>{submission.formName}</span>
                <div className="template-meta">
                  <span>{new Date(submission.createdAt).toLocaleString()}</span>
                  <span className="status-badge">{submission.status.replaceAll("-", " ")}</span>
                </div>
                {submission.review?.flags?.length ? (
                  <div className="review-flag-list">
                    {submission.review.flags.slice(0, 3).map((flag) => <span className={`review-flag ${flag.severity}`} key={flag.key}>{flag.label}</span>)}
                  </div>
                ) : null}
              </button>
            )) : (
              <div className="empty-state"><h2>No submissions</h2><p>Submitted intakes will appear here.</p></div>
            )}
          </div>

          <article className="submission-detail">
            {detailLoading ? (
              <div className="empty-state">
                <h2>Loading details</h2>
                <p>Opening the selected intake record.</p>
              </div>
            ) : !selectedSubmission ? (
              <div className="empty-state">
                <h2>No submission selected</h2>
                <p>Choose a record to see the full patient response payload.</p>
              </div>
            ) : (
              <>
                <div className="detail-header">
                  <div>
                    <p className="eyebrow">{selectedSubmission.category}</p>
                    <h2>{selectedSubmission.patientName}</h2>
                    <p>{selectedSubmission.formName} - {new Date(selectedSubmission.createdAt).toLocaleString()}</p>
                  </div>
                  <select className="select-input" aria-label="Submission status" value={selectedSubmission.status} onChange={(event) => onStatusChange(selectedSubmission.id, event.target.value)}>
                    {["new", "in-review", "needs-follow-up", "complete"].map((status) => (
                      <option value={status} key={status}>{status.replaceAll("-", " ")}</option>
                    ))}
                  </select>
                  <button className="secondary-button" type="button" onClick={handleExportPdf}>Export PDF</button>
                </div>
                <section className={`review-panel ${selectedSubmission.review?.status || "routine"}`}>
                  <div>
                    <p className="eyebrow">Review status</p>
                    <h3>{selectedSubmission.review?.label || "Routine"}</h3>
                  </div>
                  {selectedSubmission.review?.flags?.length ? (
                    <div className="review-flag-list">
                      {selectedSubmission.review.flags.map((flag) => <span className={`review-flag ${flag.severity}`} key={flag.key}>{flag.label}</span>)}
                    </div>
                  ) : <span className="review-flag low">No automatic flags</span>}
                </section>
                <AuditHistory events={selectedAuditEvents} />
                <AsqScoreTable formId={selectedSubmission.formId} answers={selectedAnswers} submitted />
                <ScoreInsights insights={selectedInsights} />
                {staffFields.length ? (
                  <section className="review-edit-panel">
                    <div className="detail-header compact-detail-header">
                      <div>
                        <p className="eyebrow">Staff review</p>
                        <h3>Staff responses</h3>
                      </div>
                      <button className="primary-button" type="button" onClick={saveStaffReview} disabled={staffSaving}>
                        {staffSaving ? "Saving" : "Save review"}
                      </button>
                    </div>
                    <div className="field-grid">
                      {staffFields.map((field) => (
                        <FormField
                          field={field}
                          key={field.id}
                          value={staffDraft[field.id]}
                          readOnly={isCalculatedStaffField(field)}
                          onChange={(fieldId, value) => setStaffDraft((current) => ({ ...current, [fieldId]: value }))}
                        />
                      ))}
                    </div>
                    {staffMessage ? <div className="message" role="status">{staffMessage}</div> : null}
                  </section>
                ) : null}
                <div className="answer-list">
                  {Object.entries(selectedAnswers).filter(([key]) => {
                    const field = fieldMap.get(key);
                    return !field || !isRepeatedDemographicField(field, field.section);
                  }).map(([key, value]) => {
                    const field = fieldMap.get(key);
                    const owner = field ? fieldOwner(field, field.section) : "patient";
                    return (
                      <div className="answer-row" key={key}>
                        <strong>{field?.label || key} <span className={`field-owner ${owner}`}>{owner}</span></strong>
                        <span>{displayAnswer(value)}</span>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </article>
        </div>
      </div>
    </section>
  );
}
