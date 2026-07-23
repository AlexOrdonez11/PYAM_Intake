export function fieldName(field) {
  return `field_${field.id}`;
}

export function isPatientInfoSection(sectionTitle = "") {
  return sectionTitle === "Patient" || sectionTitle.startsWith("Patient and Visit");
}

export function isRepeatedDemographicField(field, sectionTitle = "") {
  if (!field || isPatientInfoSection(sectionTitle)) return false;

  const id = String(field.id || "").toLowerCase();
  const label = String(field.label || "").toLowerCase().trim();

  if (id.startsWith("lead_")) return false;
  if (id.includes("asq") && id.includes("completed_date")) return false;
  if (id.includes("test_date") || id.includes("date_drawn") || id.includes("date_analyzed")) return false;
  if (id.includes("parent_dob") || id.includes("caregiver_date_of_birth")) return false;

  return (
    id === "epds_name" ||
    id === "phqa_name" ||
    id === "phqa_date" ||
    id === "mnvfc_patient_name" ||
    id === "mnvfc_birth_date" ||
    id === "mnvfc_parent_guardian" ||
    id === "bpsc_caregiver_name" ||
    id === "bpsc_child_name" ||
    id === "bpsc_date" ||
    id === "psc17_caregiver_name" ||
    id === "psc17_child_name" ||
    id === "psc17_date" ||
    id === "ppsc_child_name" ||
    id === "ppsc_today_date" ||
    id.includes("baby_dob") ||
    id.includes("baby_date_of_birth") ||
    label === "child name" ||
    label === "name of child" ||
    label === "patient name" ||
    label === "caregiver completing this form" ||
    label === "date" ||
    label === "today's date" ||
    label === "birth date"
  );
}

export function getTodayDateValue() {
  return new Date().toISOString().slice(0, 10);
}

export function demographicAutofillValue(field, answers) {
  const id = String(field.id || "").toLowerCase();
  const label = String(field.label || "").toLowerCase().trim();

  if (id.includes("dob") || id.includes("birth") || label.includes("birth")) {
    return answers.date_of_birth || "";
  }
  if (id.includes("caregiver") || id.includes("parent_guardian")) {
    return answers.completed_by || "";
  }
  if (id.endsWith("_date") || label === "date" || label === "today's date") {
    return answers.visit_date || getTodayDateValue();
  }
  return answers.patient_name || "";
}

export function isStaffOnlyField(field) {
  if (!field) return false;
  if (field.staffOnly === false || field.owner === "patient") return false;
  if (field.staffOnly) return true;
  if (field.owner === "staff") return true;

  const id = String(field.id || "").toLowerCase();
  const label = String(field.label || "").toLowerCase();

  if (["baby_id", "child_id", "patient_id"].includes(id)) return true;
  if (label.includes("baby id") || label.includes("child id") || label.includes("patient id")) return true;
  if (id.startsWith("lead_")) return true;
  if (id.startsWith("mnvfc_") && (
    id.includes("staff") ||
    id.includes("notes") ||
    id.includes("review") ||
    id.includes("verified") ||
    id.includes("processed") ||
    id.includes("completed_by")
  )) return true;
  if (id.includes("staff_notes")) return true;
  if (id.includes("total_score") || id.endsWith("_score")) return true;
  if (id.includes("_zone") || label.includes("score zone")) return true;
  if (id.includes("cutoff_met")) return true;
  if (id.includes("follow_up_actions") || id.includes("referral_reason") || id.includes("rescreen_months")) return true;
  if (id.includes("optional_item_responses")) return true;
  if (id === "crafft_part_a_yes_count" || id === "crafft_part_b_yes_count") return true;
  if (label.includes("staff notes") || label.includes("office coding")) return true;

  return false;
}

export function isCalculatedStaffField(field) {
  if (!field) return false;

  const id = String(field.id || "").toLowerCase();
  const label = String(field.label || "").toLowerCase();

  return (
    id.includes("total_score") ||
    id.endsWith("_score") ||
    id.endsWith("_total") ||
    id.includes("_total_") ||
    id.includes("_zone") ||
    id.endsWith("_control_status") ||
    id.endsWith("_impairment_present") ||
    id.endsWith("_screen_result") ||
    id.endsWith("_count") ||
    id.includes("cutoff_met") ||
    id === "crafft_part_a_yes_count" ||
    id === "crafft_part_b_yes_count" ||
    label.includes("total score") ||
    label.includes("score zone")
  );
}

export function fieldOwner(field, sectionTitle) {
  if (isRepeatedDemographicField(field, sectionTitle)) return "autofilled";
  if (isStaffOnlyField(field)) return "staff";
  return "patient";
}
