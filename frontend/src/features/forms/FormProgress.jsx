import { getFormProgress } from "./progressUtils";

function focusSection(sectionId) {
  const sectionElement = document.getElementById(sectionId);
  sectionElement?.scrollIntoView({ behavior: "smooth", block: "start" });
  const firstInput = sectionElement?.querySelector("input, select, textarea, button");
  firstInput?.focus?.({ preventScroll: true });
}

export function FormProgress({ form, answers, mode }) {
  const progress = getFormProgress(form, answers, mode);
  const missingPreview = progress.missingRequired.slice(0, 4);
  const sectionsWithFields = progress.sections.filter((section) => section.totalFields > 0);

  return (
    <section className="form-progress" aria-label="Form completion">
      <div className="form-progress-header">
        <div>
          <strong>{progress.percent}% complete</strong>
          <span>
            {progress.completedFieldCount} of {progress.totalFields} fields complete - {progress.completedSectionCount} of {sectionsWithFields.length} sections complete
          </span>
        </div>
        <span className={`progress-status ${progress.missingRequired.length ? "needs-work" : "ready"}`}>
          {progress.missingRequired.length ? "Needs info" : "Ready"}
        </span>
      </div>
      <div className="progress-track" aria-hidden="true">
        <span style={{ width: `${progress.percent}%` }} />
      </div>
      {sectionsWithFields.length ? (
        <div className="section-progress-grid" aria-label="Section completion">
          {sectionsWithFields.map((section) => (
            <button
              className={`section-progress-chip ${section.isComplete ? "complete" : "incomplete"}`}
              key={section.id}
              type="button"
              onClick={() => focusSection(section.id)}
            >
              <span>{section.title}</span>
              <strong>{section.percent}%</strong>
              {section.isComplete ? <small>Complete</small> : <small>{section.completedFieldCount}/{section.totalFields} fields</small>}
            </button>
          ))}
        </div>
      ) : null}
      {progress.missingRequired.length ? (
        <div className="missing-fields">
          <span>Missing:</span>
          {missingPreview.map((field) => (
            <button
              key={field.id}
              type="button"
              onClick={() => document.getElementById(`field_${field.id}`)?.focus()}
            >
              {field.label}
            </button>
          ))}
          {progress.missingRequired.length > missingPreview.length ? (
            <em>+{progress.missingRequired.length - missingPreview.length} more</em>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
