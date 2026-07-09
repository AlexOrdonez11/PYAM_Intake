import { useEffect, useState } from "react";
import { FormField } from "../components/fields/FormField";
import { fieldOwner, isRepeatedDemographicField, isStaffOnlyField } from "../features/forms/fieldMeta";
import { AsqScoreTable } from "../features/scoring/AsqScoreTable";

function displayAnswer(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value === true) return "Yes";
  if (value === false) return "No";
  return value || "Not provided";
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
    setStaffDraft(selectedSubmission?.answers || {});
    setStaffMessage("");
  }, [selectedSubmission?.id]);

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
                <AsqScoreTable formId={selectedSubmission.formId} answers={selectedSubmission.answers || {}} submitted />
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
                          onChange={(fieldId, value) => setStaffDraft((current) => ({ ...current, [fieldId]: value }))}
                        />
                      ))}
                    </div>
                    {staffMessage ? <div className="message" role="status">{staffMessage}</div> : null}
                  </section>
                ) : null}
                <div className="answer-list">
                  {Object.entries(selectedSubmission.answers || {}).filter(([key]) => {
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
