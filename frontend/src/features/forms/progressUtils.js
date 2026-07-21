import { isRepeatedDemographicField, isStaffOnlyField } from "./fieldMeta";

export function isFilled(value, field) {
  if (field.type === "checkbox") return value === true;
  if (Array.isArray(value)) return value.length > 0;
  return value !== undefined && value !== null && String(value).trim() !== "";
}

export function getVisibleFields(form, mode) {
  if (!form) return [];
  return (form.sections || []).flatMap((section) =>
    (section.fields || [])
      .filter((field) => !isRepeatedDemographicField(field, section.title))
      .filter((field) => mode === "staff" || !isStaffOnlyField(field))
      .map((field) => ({ ...field, sectionTitle: section.title }))
  );
}

export function getFormProgress(form, answers, mode) {
  const sections = (form?.sections || []).map((section, sectionIndex) => {
    const fields = (section.fields || [])
      .filter((field) => !isRepeatedDemographicField(field, section.title))
      .filter((field) => mode === "staff" || !isStaffOnlyField(field));
    const requiredFields = fields.filter((field) => field.required);
    const completedRequired = requiredFields.filter((field) => isFilled(answers[field.id], field));
    const missingRequired = requiredFields.filter((field) => !isFilled(answers[field.id], field));
    return {
      id: `section_${sectionIndex}`,
      title: section.title || `Section ${sectionIndex + 1}`,
      totalFields: fields.length,
      requiredCount: requiredFields.length,
      completedRequiredCount: completedRequired.length,
      missingRequired,
      percent: requiredFields.length ? Math.round((completedRequired.length / requiredFields.length) * 100) : 100,
      isComplete: missingRequired.length === 0
    };
  });
  const fields = getVisibleFields(form, mode);
  const requiredFields = fields.filter((field) => field.required);
  const completedRequired = requiredFields.filter((field) => isFilled(answers[field.id], field));
  const missingRequired = requiredFields.filter((field) => !isFilled(answers[field.id], field));

  return {
    totalFields: fields.length,
    requiredCount: requiredFields.length,
    completedRequiredCount: completedRequired.length,
    missingRequired,
    percent: requiredFields.length ? Math.round((completedRequired.length / requiredFields.length) * 100) : 100,
    sections,
    completedSectionCount: sections.filter((section) => section.isComplete).length
  };
}
