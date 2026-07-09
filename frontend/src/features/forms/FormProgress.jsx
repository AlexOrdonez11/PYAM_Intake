import { getFormProgress } from "./progressUtils";

export function FormProgress({ form, answers, mode }) {
  const progress = getFormProgress(form, answers, mode);
  const missingPreview = progress.missingRequired.slice(0, 4);

  return (
    <section className="form-progress" aria-label="Form completion">
      <div className="form-progress-header">
        <div>
          <strong>{progress.percent}% complete</strong>
          <span>
            {progress.completedRequiredCount} of {progress.requiredCount} required fields complete
          </span>
        </div>
        <span className={`progress-status ${progress.missingRequired.length ? "needs-work" : "ready"}`}>
          {progress.missingRequired.length ? "Needs info" : "Ready"}
        </span>
      </div>
      <div className="progress-track" aria-hidden="true">
        <span style={{ width: `${progress.percent}%` }} />
      </div>
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
