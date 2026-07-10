import { fieldName, isStaffOnlyField } from "../../features/forms/fieldMeta";

function Required({ field }) {
  return field.required ? <span className="required" aria-hidden="true">*</span> : null;
}

export function FormField({ field, value, onChange, readOnly = false }) {
  const id = fieldName(field);
  const staffOnly = isStaffOnlyField(field);
  const required = Boolean(field.required);
  const fieldAttrs = {
    "data-staff-only": staffOnly || undefined,
    "data-readonly": readOnly || undefined
  };
  const setValue = (nextValue) => {
    if (!readOnly) onChange(field.id, nextValue);
  };
  const commonProps = {
    id,
    name: field.id,
    required: required && !readOnly,
    value: value || "",
    onChange: (event) => setValue(event.target.value)
  };
  const readOnlyProps = {
    readOnly,
    "aria-readonly": readOnly || undefined
  };

  if (["text", "email", "tel", "date", "number", "datetime-local"].includes(field.type)) {
    return (
      <div className="field" {...fieldAttrs}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <input className="field-control" type={field.type} {...commonProps} {...readOnlyProps} />
        {readOnly ? <span className="field-readonly-note">Calculated automatically</span> : null}
      </div>
    );
  }

  if (field.type === "signature") {
    return (
      <div className="field" {...fieldAttrs}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <input className="field-control" type="text" placeholder="Type full legal name" {...commonProps} {...readOnlyProps} />
        {readOnly ? <span className="field-readonly-note">Calculated automatically</span> : null}
      </div>
    );
  }

  if (field.type === "textarea") {
    return (
      <div className="field full" {...fieldAttrs}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <textarea className="field-control" {...commonProps} {...readOnlyProps} />
        {readOnly ? <span className="field-readonly-note">Calculated automatically</span> : null}
      </div>
    );
  }

  if (field.type === "select") {
    return (
      <div className="field" {...fieldAttrs}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <select className="field-control" {...commonProps} aria-readonly={readOnly || undefined} disabled={readOnly}>
          <option value="">Select</option>
          {(field.options || []).map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
        {readOnly ? <span className="field-readonly-note">Calculated automatically</span> : null}
      </div>
    );
  }

  if (field.type === "checkbox") {
    return (
      <div className="field full" {...fieldAttrs}>
        <label className="choice-option">
          <input
            type="checkbox"
            name={field.id}
            required={required && !readOnly}
            checked={Boolean(value)}
            disabled={readOnly}
            onChange={(event) => setValue(event.target.checked)}
          />
          <span>{field.label} <Required field={field} /></span>
        </label>
      </div>
    );
  }

  if (field.type === "radio" || field.type === "multicheck") {
    const inputType = field.type === "radio" ? "radio" : "checkbox";
    const selectedValues = Array.isArray(value) ? value : [];

    return (
      <div className="field full" {...fieldAttrs}>
        <span className="choice-label">{field.label} <Required field={field} /></span>
        <div className="choice-group">
          {(field.options || []).map((option) => (
            <label className="choice-option" key={option}>
              <input
                type={inputType}
                name={field.id}
                value={option}
                required={required && field.type === "radio" && !readOnly}
                checked={field.type === "radio" ? value === option : selectedValues.includes(option)}
                disabled={readOnly}
                onChange={(event) => {
                  if (field.type === "radio") {
                    setValue(option);
                    return;
                  }
                  const next = event.target.checked
                    ? [...selectedValues, option]
                    : selectedValues.filter((item) => item !== option);
                  setValue(next);
                }}
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }

  if (field.type === "scale") {
    return (
      <div className="field full" {...fieldAttrs}>
        <span className="choice-label">{field.label} <Required field={field} /></span>
        <div className="scale-group">
          {(field.options || []).map((option, index) => (
            <label className="scale-option" key={option}>
              <input
                type="radio"
                name={field.id}
                value={option}
                data-score={index + 1}
                required={required && !readOnly}
                checked={value === option}
                disabled={readOnly}
                onChange={() => setValue(option)}
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }

  return null;
}
