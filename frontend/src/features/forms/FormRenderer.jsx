import { Fragment } from "react";
import { FormField } from "../../components/fields/FormField";
import { AsqScoreTable } from "../scoring/AsqScoreTable";
import { calculateAsqScores } from "../scoring/asqScoring";
import { FormProgress } from "./FormProgress.jsx";
import { getFormProgress, getVisibleFields, isFilled } from "./progressUtils";
import { demographicAutofillValue, isRepeatedDemographicField, isStaffOnlyField } from "./fieldMeta";

function ContentItem({ item }) {
  if (!item) return null;
  if (item.type === "heading") {
    return <h4 className="content-heading">{item.text || item.title || ""}</h4>;
  }

  return (
    <div className={`content-block${item.variant ? ` ${item.variant}` : ""}`}>
      {item.title ? <strong>{item.title}</strong> : null}
      {item.text ? <p>{item.text}</p> : null}
      {Array.isArray(item.items) ? (
        <ul>{item.items.map((entry) => <li key={entry}>{entry}</li>)}</ul>
      ) : null}
      {item.url ? (
        <a className="content-link" href={item.url} target="_blank" rel="noopener noreferrer">
          {item.linkLabel || "Open source packet"}
        </a>
      ) : null}
    </div>
  );
}

function groupedFields(fields) {
  return fields.map((field, index) => {
    const previous = fields[index - 1];
    const startsGroup = field.groupTitle && field.groupTitle !== previous?.groupTitle;
    return { field, startsGroup };
  });
}

export function buildSubmissionAnswers(form, answers, mode) {
  const output = {};

  for (const section of form.sections || []) {
    for (const field of section.fields || []) {
      if (isRepeatedDemographicField(field, section.title)) continue;
      if (mode !== "staff" && isStaffOnlyField(field)) continue;
      output[field.id] = answers[field.id] ?? (field.type === "multicheck" ? [] : field.type === "checkbox" ? false : "");
    }
  }

  for (const section of form.sections || []) {
    for (const field of section.fields || []) {
      if (isRepeatedDemographicField(field, section.title)) {
        output[field.id] = demographicAutofillValue(field, output);
      }
    }
  }

  return output;
}

function focusField(fieldId) {
  const fieldElement = document.getElementById(`field_${fieldId}`);
  fieldElement?.focus();
  fieldElement?.scrollIntoView({ behavior: "smooth", block: "center" });
}

function CompletionNotice({ notice }) {
  if (!notice) return null;
  return (
    <section className="completion-notice" role="status">
      <div>
        <p className="eyebrow">Submission saved</p>
        <h3>{notice.formName}</h3>
        <p>
          {notice.remainingCount
            ? `${notice.remainingCount} pending form${notice.remainingCount === 1 ? "" : "s"} left${notice.nextFormName ? ` - ${notice.nextFormName} is ready.` : "."}`
            : "All pending forms for this intake are complete."}
        </p>
      </div>
    </section>
  );
}

function DraftNotice({ notice, resumeSaving, onSaveResumeDraft, onDiscardDraft }) {
  if (!notice) return null;
  const savedAt = notice.savedAt ? new Date(notice.savedAt).toLocaleString() : "just now";
  return (
    <section className={`draft-notice ${notice.restored ? "restored" : ""}`} role="status">
      <div>
        <p className="eyebrow">{notice.restored ? "Draft restored" : "Draft saved"}</p>
        <h3>{notice.formName || "Current form"}</h3>
        <p>{notice.serverDraft ? "Saved on the server" : "Autosaved locally on this device"} at {savedAt}.</p>
        {notice.resumeCode ? (
          <div className="resume-code-box">
            <span>Resume code</span>
            <strong>{notice.resumeCode}</strong>
            <small>{notice.resumeUrl}</small>
          </div>
        ) : null}
      </div>
      <div className="draft-actions">
        {onSaveResumeDraft ? <button className="secondary-button" type="button" onClick={onSaveResumeDraft} disabled={resumeSaving}>{resumeSaving ? "Saving" : notice.resumeCode ? "Update resume code" : "Save resume code"}</button> : null}
        {onDiscardDraft ? <button className="ghost-button" type="button" onClick={onDiscardDraft}>Discard draft</button> : null}
      </div>
    </section>
  );
}

function ValidationSummary({ progress, show }) {
  if (!show || !progress.missingRequired.length) return null;
  return (
    <section className="validation-summary" role="alert" aria-live="assertive">
      <div>
        <p className="eyebrow">Required information</p>
        <h3>{progress.missingRequired.length} required field{progress.missingRequired.length === 1 ? "" : "s"} still need attention</h3>
      </div>
      <div className="validation-link-list">
        {progress.missingRequired.slice(0, 8).map((field) => (
          <button type="button" key={field.id} onClick={() => focusField(field.id)}>
            {field.label}
          </button>
        ))}
        {progress.missingRequired.length > 8 ? <span>+{progress.missingRequired.length - 8} more</span> : null}
      </div>
    </section>
  );
}

function getSubmitReview(form, answers, mode, progress) {
  const visibleFields = getVisibleFields(form, mode);
  const missingSignatures = visibleFields.filter((field) => field.type === "signature" && field.required && !isFilled(answers[field.id], field));
  const incompleteAsqScores = calculateAsqScores(form.id, answers).filter((score) => score.total === null);
  const sectionsNeedingWork = progress.sections.filter((section) => section.totalFields > 0 && !section.isComplete);

  return [
    {
      key: "required",
      label: "Required fields",
      status: progress.missingRequired.length ? "needs-work" : "ready",
      value: progress.missingRequired.length ? `${progress.missingRequired.length} missing` : "Ready",
      detail: progress.missingRequired.length ? "Complete these before submitting." : "All required fields are complete.",
      actionField: progress.missingRequired[0]?.id
    },
    {
      key: "sections",
      label: "Sections",
      status: sectionsNeedingWork.length ? "needs-work" : "ready",
      value: `${progress.completedSectionCount}/${progress.sections.length} ready`,
      detail: sectionsNeedingWork.length ? `${sectionsNeedingWork.length} section${sectionsNeedingWork.length === 1 ? "" : "s"} still need required information.` : "Every section is ready.",
      actionSection: sectionsNeedingWork[0]?.id
    },
    {
      key: "signatures",
      label: "Signatures",
      status: missingSignatures.length ? "needs-work" : "ready",
      value: missingSignatures.length ? `${missingSignatures.length} missing` : "Ready",
      detail: missingSignatures.length ? "Required signature fields need a typed legal name." : "Required signatures are complete.",
      actionField: missingSignatures[0]?.id
    },
    {
      key: "scoring",
      label: "Scoring groups",
      status: incompleteAsqScores.length ? "needs-work" : "ready",
      value: incompleteAsqScores.length ? `${incompleteAsqScores.length} incomplete` : "Ready",
      detail: incompleteAsqScores.length ? "Some ASQ groups are missing answers, so staff scoring will be incomplete." : "Calculated scoring groups have enough answers.",
      actionField: incompleteAsqScores[0]
        ? `${incompleteAsqScores[0].fieldPrefix}${Math.max(0, incompleteAsqScores[0].itemScores.findIndex((score) => score === null)) + 1}`
        : null
    }
  ];
}

function SubmitReview({ form, answers, mode, progress }) {
  const checks = getSubmitReview(form, answers, mode, progress);
  const needsWork = checks.filter((check) => check.status === "needs-work");

  return (
    <section className={`submit-review ${needsWork.length ? "needs-work" : "ready"}`} aria-label="Review before submit">
      <div className="submit-review-header">
        <div>
          <p className="eyebrow">Review before submit</p>
          <h3>{needsWork.length ? `${needsWork.length} item${needsWork.length === 1 ? "" : "s"} need attention` : "Ready to submit"}</h3>
          <p>{needsWork.length ? "Use these checks to finish the form before submitting." : "Everything required for this form is complete."}</p>
        </div>
        <span className={`progress-status ${needsWork.length ? "needs-work" : "ready"}`}>{needsWork.length ? "Needs info" : "Ready"}</span>
      </div>
      <div className="submit-review-grid">
        {checks.map((check) => (
          <article className={`submit-review-card ${check.status}`} key={check.key}>
            <div>
              <strong>{check.label}</strong>
              <span>{check.value}</span>
            </div>
            <p>{check.detail}</p>
            {check.actionField ? (
              <button type="button" onClick={() => focusField(check.actionField)}>Go to field</button>
            ) : check.actionSection ? (
              <button type="button" onClick={() => document.getElementById(check.actionSection)?.scrollIntoView({ behavior: "smooth", block: "start" })}>Go to section</button>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}

export function FormRenderer({ form, answers, mode, onAnswerChange, onSubmit, onClear, onStartOver, message, error, completionNotice, draftNotice, resumeSaving, onSaveResumeDraft, onDiscardDraft }) {
  if (!form) {
    return (
      <div className="empty-state">
        <h2>Select a form</h2>
        <p>The selected packet will open here with sections, required fields, and electronic signature capture.</p>
      </div>
    );
  }

  const progress = getFormProgress(form, answers, mode);

  return (
    <form className="intake-form" onSubmit={onSubmit} noValidate>
      <div className="form-heading">
        <div>
          <p className="eyebrow">{form.category}</p>
          <h2>{form.name}</h2>
          <p>{form.description}</p>
        </div>
        <div className="form-heading-actions">
          {onStartOver ? <button className="ghost-button form-start-over" type="button" onClick={onStartOver}>Start over</button> : null}
          <span className="time-badge">
            <span>Estimated time</span>
            <strong>{form.estimatedMinutes} min</strong>
          </span>
        </div>
      </div>

      <CompletionNotice notice={completionNotice} />

      <DraftNotice notice={draftNotice} resumeSaving={resumeSaving} onSaveResumeDraft={onSaveResumeDraft} onDiscardDraft={onDiscardDraft} />

      <FormProgress form={form} answers={answers} mode={mode} />

      <ValidationSummary progress={progress} show={error} />

      <AsqScoreTable formId={form.id} answers={answers} />

      {(form.sections || [])
        .map((section, sectionIndex) => ({ section, sectionIndex }))
        .filter(({ section }) => mode === "staff" || !(section.staffOnly || section.owner === "staff"))
        .map(({ section, sectionIndex }) => {
        const visibleFields = (section.fields || [])
          .filter((field) => !isRepeatedDemographicField(field, section.title))
          .filter((field) => mode === "staff" || !isStaffOnlyField(field));
        const sectionProgress = progress.sections[sectionIndex];
        return (
          <section className="form-section" data-staff-only={section.staffOnly || undefined} id={`section_${sectionIndex}`} key={section.title}>
            <div className="form-section-heading">
              <h3>{section.title}</h3>
              {sectionProgress ? (
                <span className={`section-status ${sectionProgress.isComplete ? "complete" : "incomplete"}`}>
                  {sectionProgress.isComplete ? "Ready" : `${sectionProgress.missingRequired.length} missing`}
                </span>
              ) : null}
            </div>
            {section.content?.length ? (
              <div className="section-content">
                {section.content.map((item, index) => <ContentItem item={item} key={`${section.title}-${index}`} />)}
              </div>
            ) : null}
            {visibleFields.length ? (
              <div className="field-grid">
                {groupedFields(visibleFields).map(({ field, startsGroup }) => (
                  <Fragment key={field.id}>
                    {startsGroup ? (
                      <div className={`field-group-heading ${field.groupVariant || ""}`}>
                        <h4>{field.groupTitle}</h4>
                        {field.groupDescription ? <p>{field.groupDescription}</p> : null}
                      </div>
                    ) : null}
                    <FormField
                      field={field}
                      value={answers[field.id]}
                      onChange={onAnswerChange}
                    />
                  </Fragment>
                ))}
              </div>
            ) : null}
          </section>
        );
      })}

      <SubmitReview form={form} answers={answers} mode={mode} progress={progress} />

      <div className="form-footer">
        <button className="secondary-button" type="button" onClick={onClear}>Clear</button>
        <button className="primary-button" type="submit">Submit Intake</button>
      </div>
      <div className={`message${error ? " error" : ""}`} role="status">{message}</div>
    </form>
  );
}
