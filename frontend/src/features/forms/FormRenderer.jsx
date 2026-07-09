import { FormField } from "../../components/fields/FormField";
import { AsqScoreTable } from "../scoring/AsqScoreTable";
import { FormProgress } from "./FormProgress.jsx";
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

export function FormRenderer({ form, answers, mode, onAnswerChange, onSubmit, onClear, onStartOver, message, error }) {
  if (!form) {
    return (
      <div className="empty-state">
        <h2>Select a form</h2>
        <p>The selected packet will open here with sections, required fields, and electronic signature capture.</p>
      </div>
    );
  }

  return (
    <form className="intake-form" onSubmit={onSubmit}>
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

      <FormProgress form={form} answers={answers} mode={mode} />

      <AsqScoreTable formId={form.id} answers={answers} />

      {(form.sections || []).map((section) => {
        const visibleFields = (section.fields || []).filter((field) => !isRepeatedDemographicField(field, section.title));
        return (
          <section className="form-section" data-staff-only={section.staffOnly || undefined} key={section.title}>
            <h3>{section.title}</h3>
            {section.content?.length ? (
              <div className="section-content">
                {section.content.map((item, index) => <ContentItem item={item} key={`${section.title}-${index}`} />)}
              </div>
            ) : null}
            {visibleFields.length ? (
              <div className="field-grid">
                {visibleFields.map((field) => (
                  <FormField
                    field={field}
                    key={field.id}
                    value={answers[field.id]}
                    onChange={onAnswerChange}
                  />
                ))}
              </div>
            ) : null}
          </section>
        );
      })}

      <div className="form-footer">
        <button className="secondary-button" type="button" onClick={onClear}>Clear</button>
        <button className="primary-button" type="submit">Submit Intake</button>
      </div>
      <div className={`message${error ? " error" : ""}`} role="status">{message}</div>
    </form>
  );
}
