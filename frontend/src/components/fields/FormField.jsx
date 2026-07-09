import { fieldName, isStaffOnlyField } from "../../features/forms/fieldMeta";

function Required({ field }) {
  return field.required ? <span className="required" aria-hidden="true">*</span> : null;
}

export function FormField({ field, value, onChange }) {
  const id = fieldName(field);
  const staffOnly = isStaffOnlyField(field);
  const required = Boolean(field.required);
  const setValue = (nextValue) => onChange(field.id, nextValue);
  const commonProps = {
    id,
    name: field.id,
    required,
    value: value || "",
    onChange: (event) => setValue(event.target.value)
  };

  if (["text", "email", "tel", "date", "number", "datetime-local"].includes(field.type)) {
    return (
      <div className="field" data-staff-only={staffOnly || undefined}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <input className="field-control" type={field.type} {...commonProps} />
      </div>
    );
  }

  if (field.type === "signature") {
    return (
      <div className="field" data-staff-only={staffOnly || undefined}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <input className="field-control" type="text" placeholder="Type full legal name" {...commonProps} />
      </div>
    );
  }

  if (field.type === "textarea") {
    return (
      <div className="field full" data-staff-only={staffOnly || undefined}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <textarea className="field-control" {...commonProps} />
      </div>
    );
  }

  if (field.type === "select") {
    return (
      <div className="field" data-staff-only={staffOnly || undefined}>
        <label htmlFor={id}>{field.label} <Required field={field} /></label>
        <select className="field-control" {...commonProps}>
          <option value="">Select</option>
          {(field.options || []).map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>
    );
  }

  if (field.type === "checkbox") {
    return (
      <div className="field full" data-staff-only={staffOnly || undefined}>
        <label className="choice-option">
          <input
            type="checkbox"
            name={field.id}
            required={required}
            checked={Boolean(value)}
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
      <div className="field full" data-staff-only={staffOnly || undefined}>
        <span className="choice-label">{field.label} <Required field={field} /></span>
        <div className="choice-group">
          {(field.options || []).map((option) => (
            <label className="choice-option" key={option}>
              <input
                type={inputType}
                name={field.id}
                value={option}
                required={required && field.type === "radio"}
                checked={field.type === "radio" ? value === option : selectedValues.includes(option)}
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
      <div className="field full" data-staff-only={staffOnly || undefined}>
        <span className="choice-label">{field.label} <Required field={field} /></span>
        <div className="scale-group">
          {(field.options || []).map((option, index) => (
            <label className="scale-option" key={option}>
              <input
                type="radio"
                name={field.id}
                value={option}
                data-score={index + 1}
                required={required}
                checked={value === option}
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
