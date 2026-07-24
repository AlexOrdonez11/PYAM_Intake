import { useEffect, useState } from "react";
import { FormField } from "../components/fields/FormField";
import { fieldOwner, isCalculatedStaffField, isRepeatedDemographicField, isStaffOnlyField } from "../features/forms/fieldMeta";
import { AsqScoreTable } from "../features/scoring/AsqScoreTable";
import { calculateAsqScores } from "../features/scoring/asqScoring";
import { addCalculatedScores } from "../features/scoring/calculatedScores";
import { scoreInsightsForSubmission } from "../features/scoring/scoreInsights";
import { calculateAge } from "./WelcomePage";

function displayAnswer(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value === true) return "Yes";
  if (value === false) return "No";
  return value || "Not provided";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

const SUBMISSION_STATUSES = [
  ["draft", "Draft"],
  ["new", "New"],
  ["in-review", "In review"],
  ["needs-patient-follow-up", "Needs patient follow-up"],
  ["ready-for-chart", "Ready for chart"],
  ["complete", "Completed"]
];

function statusLabelText(status) {
  if (status === "needs-follow-up") return "Needs patient follow-up";
  return SUBMISSION_STATUSES.find(([value]) => value === status)?.[1] || String(status || "Unknown").replaceAll("-", " ");
}

function statusMatches(submissionStatus, filterStatus) {
  if (!filterStatus) return true;
  if (filterStatus === "needs-patient-follow-up") return ["needs-patient-follow-up", "needs-follow-up"].includes(submissionStatus);
  return submissionStatus === filterStatus;
}

function reviewCounts(submissions) {
  return submissions.reduce((counts, submission) => {
    const flags = submission.review?.flags || [];
    counts.total += 1;
    counts.needsReview += submission.review?.status === "needs-review" ? 1 : 0;
    counts.high += flags.filter((flag) => flag.severity === "high").length;
    counts.medium += flags.filter((flag) => flag.severity === "medium").length;
    counts.draft += submission.status === "draft" ? 1 : 0;
    counts.new += submission.status === "new" ? 1 : 0;
    counts.followUp += ["needs-follow-up", "needs-patient-follow-up"].includes(submission.status) ? 1 : 0;
    counts.readyForChart += submission.status === "ready-for-chart" ? 1 : 0;
    counts.complete += submission.status === "complete" ? 1 : 0;
    return counts;
  }, { total: 0, needsReview: 0, high: 0, medium: 0, draft: 0, new: 0, followUp: 0, readyForChart: 0, complete: 0 });
}

function severityScore(submission) {
  const flags = submission.review?.flags || [];
  const flagScore = flags.reduce((score, flag) => score + (flag.severity === "high" ? 100 : flag.severity === "medium" ? 30 : 5), 0);
  const statusScore = ["needs-follow-up", "needs-patient-follow-up"].includes(submission.status) ? 80 : submission.review?.status === "needs-review" ? 60 : submission.status === "new" ? 20 : submission.status === "draft" ? 5 : 0;
  return flagScore + statusScore;
}

function submissionSearchText(submission) {
  return [
    submission.patientName,
    submission.formName,
    submission.category,
    submission.status,
    statusLabelText(submission.status),
    submission.review?.label,
    ...(submission.review?.flags || []).map((flag) => flag.label)
  ].join(" ").toLowerCase();
}

function sortSubmissions(submissions, sortMode) {
  const sorted = [...submissions];
  if (sortMode === "priority") {
    return sorted.sort((a, b) => severityScore(b) - severityScore(a) || new Date(b.createdAt) - new Date(a.createdAt));
  }
  if (sortMode === "oldest") {
    return sorted.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
  }
  if (sortMode === "patient") {
    return sorted.sort((a, b) => String(a.patientName || "").localeCompare(String(b.patientName || "")));
  }
  if (sortMode === "form") {
    return sorted.sort((a, b) => String(a.formName || "").localeCompare(String(b.formName || "")));
  }
  return sorted.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

function ScoreInsights({ insights }) {
  if (!insights.length) return null;
  const concerningCount = insights.filter((insight) => ["below", "monitor"].includes(insight.status)).length;
  return (
    <section className="score-insights-panel">
      <div className="score-panel-header">
        <div>
          <p className="eyebrow">Score explanations</p>
          <h3>Calculated interpretation</h3>
        </div>
        <span className="score-help">{concerningCount ? `${concerningCount} highlighted` : "No highlighted thresholds"}</span>
      </div>
      <div className="score-insight-grid">
        {insights.map((insight) => (
          <article className={`score-insight ${insight.status}`} key={insight.key}>
            <div>
              <strong>{insight.label}</strong>
              <span>{statusLabel(insight.status)} - {insight.value}</span>
            </div>
            <p>{insight.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

const SCORE_SYSTEM_META = {
  "ASQ-3": { purpose: "Developmental screening", normalLabel: "On schedule", concernLabel: "Delayed or monitor range" },
  EPDS: { purpose: "Postpartum depression screening", normalLabel: "Below review threshold", concernLabel: "Mood review threshold met" },
  "PHQ-2": { purpose: "Depression prescreen", normalLabel: "Negative prescreen", concernLabel: "Positive prescreen" },
  "PHQ-A": { purpose: "Adolescent depression screening", normalLabel: "Below moderate range", concernLabel: "Moderate or higher range" },
  "PHQ-9": { purpose: "Depression screening", normalLabel: "Below moderate range", concernLabel: "Moderate or higher range" },
  "GAD-7": { purpose: "Anxiety screening", normalLabel: "Below moderate range", concernLabel: "Moderate or higher range" },
  PPSC: { purpose: "Preschool behavioral screening", normalLabel: "Below cutoff", concernLabel: "Cutoff met" },
  "PSC-17": { purpose: "Pediatric psychosocial screening", normalLabel: "Below cutoff", concernLabel: "Cutoff met" },
  "M-CHAT": { purpose: "Autism risk screening", normalLabel: "Low risk", concernLabel: "Medium/high risk" },
  CRAFFT: { purpose: "Substance-use risk screening", normalLabel: "No positive threshold", concernLabel: "Positive threshold met" },
  ASRS: { purpose: "Adult ADHD screening", normalLabel: "Negative screen", concernLabel: "Positive screen" },
  "ACE Concussion": { purpose: "Concussion symptom review", normalLabel: "No automatic symptom flag", concernLabel: "Symptom/red flag present" },
  ACT: { purpose: "Asthma control test", normalLabel: "Likely controlled", concernLabel: "May not be controlled" },
  "C-ACT": { purpose: "Child asthma control test", normalLabel: "Likely controlled", concernLabel: "May not be controlled" },
  "Child SCARED": { purpose: "Child anxiety screening", normalLabel: "Below cutoff", concernLabel: "Cutoff met" },
  "Parent SCARED": { purpose: "Parent anxiety screening", normalLabel: "Below cutoff", concernLabel: "Cutoff met" },
  "Vanderbilt Parent": { purpose: "ADHD and behavior rating", normalLabel: "Below symptom threshold", concernLabel: "Threshold or impairment present" },
  "Vanderbilt Teacher": { purpose: "ADHD and behavior rating", normalLabel: "Below symptom threshold", concernLabel: "Threshold or impairment present" },
  "Vanderbilt Parent Follow-up": { purpose: "ADHD treatment follow-up", normalLabel: "Below symptom threshold", concernLabel: "Threshold or impairment present" },
  "Vanderbilt Teacher Follow-up": { purpose: "ADHD treatment follow-up", normalLabel: "Below symptom threshold", concernLabel: "Threshold or impairment present" }
};

function scoreStatus(value, threshold, lowerIsConcerning = false) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "incomplete";
  return lowerIsConcerning ? parsed < threshold ? "below" : "above" : parsed >= threshold ? "below" : "above";
}

function statusLabel(status) {
  return {
    below: "Review",
    monitor: "Monitor",
    above: "OK",
    incomplete: "Incomplete"
  }[status] || "Review";
}

function thresholdLabel(threshold, lowerIsConcerning = false) {
  if (threshold === null || threshold === undefined) return "";
  return lowerIsConcerning ? `Concern if < ${threshold}` : `Concern if >= ${threshold}`;
}

function addScoreCard(cards, { key, system, label, value, status = "above", detail, threshold, lowerIsConcerning = false, outcome }) {
  if (value === null || value === undefined || value === "") return;
  const meta = SCORE_SYSTEM_META[system] || {};
  const resolvedOutcome = outcome || (status === "above" ? meta.normalLabel : status === "incomplete" ? "Incomplete" : meta.concernLabel);
  cards.push({
    key,
    system,
    label,
    value: String(value),
    status,
    detail,
    threshold,
    thresholdText: thresholdLabel(threshold, lowerIsConcerning),
    outcome: resolvedOutcome || statusLabel(status),
    purpose: meta.purpose || "Calculated screening score"
  });
}

function scoringCardsForSubmission(submission, answers) {
  if (!submission) return [];
  const cards = [];

  calculateAsqScores(submission.formId, answers).forEach((score) => {
    addScoreCard(cards, {
      key: `asq-${score.key}`,
      system: "ASQ-3",
      label: score.label,
      value: score.total === null ? "Incomplete" : `${score.total}/60`,
      status: score.zone.key,
      detail: score.zone.label,
      threshold: score.cutoff.toFixed(2),
      outcome: score.zone.label
    });
  });

  [
    ["epds_total_score", "EPDS", "Postpartum depression total", 10],
    ["phq2_total_score", "PHQ-2", "Depression prescreen total", 3],
    ["phqa_total_score", "PHQ-A", "Adolescent depression total", 10],
    ["phq9_total_score", "PHQ-9", "Depression total", 10],
    ["gad7_total_score", "GAD-7", "Anxiety total", 10],
    ["ppsc_total_score", "PPSC", "Preschool behavioral total", 9],
    ["psc17_internalizing_score", "PSC-17", "Internalizing", 5],
    ["psc17_attention_score", "PSC-17", "Attention", 7],
    ["psc17_externalizing_score", "PSC-17", "Externalizing", 7],
    ["psc17_total_score", "PSC-17", "Total", 15],
    ["mchat_risk_score", "M-CHAT", "Autism risk score", 3],
    ["crafft_part_a_yes_count", "CRAFFT", "Part A yes count", 1],
    ["crafft_part_b_yes_count", "CRAFFT", "Part B yes count", 2],
    ["asrs_part_a_positive_count", "ASRS", "Part A positive items", 4],
    ["asrs_part_b_positive_count", "ASRS", "Part B positive items", 1],
    ["ace_physical_total", "ACE Concussion", "Physical symptoms", 1],
    ["ace_cognitive_total", "ACE Concussion", "Cognitive symptoms", 1],
    ["ace_emotional_total", "ACE Concussion", "Emotional symptoms", 1],
    ["ace_sleep_total", "ACE Concussion", "Sleep symptoms", 1],
    ["ace_total_symptom_score", "ACE Concussion", "Total symptoms", 1],
    ["ace_red_flag_count", "ACE Concussion", "Red flags", 1]
  ].forEach(([key, system, label, threshold]) => {
    addScoreCard(cards, {
      key,
      system,
      label,
      value: answers[key],
      status: scoreStatus(answers[key], threshold),
      threshold,
      detail: Number(answers[key]) >= threshold ? "Review threshold met" : "No automatic threshold flag"
    });
  });

  [
    ["act_total_score", "ACT", "Asthma control total", 20],
    ["cact_total_score", "C-ACT", "Child asthma control total", 20]
  ].forEach(([key, system, label, threshold]) => {
    addScoreCard(cards, {
      key,
      system,
      label,
      value: answers[key],
      status: scoreStatus(answers[key], threshold, true),
      threshold,
      lowerIsConcerning: true,
      detail: answers[key.replace("_total_score", "_control_status")] || "Higher scores indicate better control"
    });
  });

  ["child_scared", "parent_scared"].forEach((prefix) => {
    const system = prefix === "child_scared" ? "Child SCARED" : "Parent SCARED";
    [
      ["total_score", "Total", 25],
      ["panic_somatic_score", "Panic / somatic", 7],
      ["generalized_anxiety_score", "Generalized anxiety", 9],
      ["separation_anxiety_score", "Separation anxiety", 5],
      ["social_anxiety_score", "Social anxiety", 8],
      ["school_avoidance_score", "School avoidance", 3]
    ].forEach(([suffix, label, threshold]) => {
      const key = `${prefix}_${suffix}`;
      addScoreCard(cards, {
        key,
        system,
        label,
        value: answers[key],
        status: scoreStatus(answers[key], threshold),
        threshold,
        detail: Number(answers[key]) >= threshold ? "Cutoff met" : "Cutoff not met"
      });
    });
  });

  [
    ["vanderbilt_parent", "Vanderbilt Parent", ["inattention", "hyperactive_impulsive", "oppositional", "conduct", "anxiety_depression"]],
    ["vanderbilt_teacher", "Vanderbilt Teacher", ["inattention", "hyperactive_impulsive", "oppositional_conduct", "anxiety_depression"]],
    ["vanderbilt_parent_followup", "Vanderbilt Parent Follow-up", ["inattention", "hyperactive_impulsive", "oppositional"]],
    ["vanderbilt_teacher_followup", "Vanderbilt Teacher Follow-up", ["inattention", "hyperactive_impulsive", "oppositional_conduct"]]
  ].forEach(([prefix, system, domains]) => {
    domains.forEach((domain) => {
      const key = `${prefix}_${domain}`;
      addScoreCard(cards, {
        key,
        system,
        label: domain.replaceAll("_", " "),
        value: answers[key],
        status: scoreStatus(answers[key], 6),
        threshold: 6,
        detail: "Count of symptom items scored often/very often"
      });
    });
    addScoreCard(cards, {
      key: `${prefix}_impairment_present`,
      system,
      label: "Performance impairment",
      value: answers[`${prefix}_impairment_present`],
      status: answers[`${prefix}_impairment_present`] === "Yes" ? "monitor" : "above",
      detail: "Based on performance items",
      outcome: answers[`${prefix}_impairment_present`] === "Yes" ? "Impairment present" : "No impairment identified"
    });
  });

  return cards;
}

function ScoringOverview({ cards }) {
  if (!cards.length) {
    return (
      <section className="scoring-overview empty-scoring-overview">
        <p className="eyebrow">Calculated scoring</p>
        <h3>No calculated scores for this form</h3>
      </section>
    );
  }

  const groupedCards = cards.reduce((groups, card) => {
    groups[card.system] = groups[card.system] || [];
    groups[card.system].push(card);
    return groups;
  }, {});
  const scoreCounts = cards.reduce((counts, card) => {
    counts[card.status] = (counts[card.status] || 0) + 1;
    return counts;
  }, {});
  const concernCount = (scoreCounts.below || 0) + (scoreCounts.monitor || 0);

  return (
    <section className="scoring-overview">
      <div className="score-panel-header">
        <div>
          <p className="eyebrow">Calculated scoring</p>
          <h3>Clinical scoring summary</h3>
        </div>
        <span className="score-help">{cards.length} calculated value{cards.length === 1 ? "" : "s"}</span>
      </div>
      <div className="scoring-alert-strip">
        <div className={concernCount ? "needs-review" : "ready"}>
          <strong>{concernCount ? `${concernCount} score${concernCount === 1 ? "" : "s"} need attention` : "No score thresholds flagged"}</strong>
          <span>{scoreCounts.below || 0} review / {scoreCounts.monitor || 0} monitor / {scoreCounts.above || 0} ok / {scoreCounts.incomplete || 0} incomplete</span>
        </div>
        <div className="score-status-legend" aria-label="Score status legend">
          <span><i className="below" /> Review</span>
          <span><i className="monitor" /> Monitor</span>
          <span><i className="above" /> OK</span>
          <span><i className="incomplete" /> Incomplete</span>
        </div>
      </div>
      <div className="scoring-system-list">
        {Object.entries(groupedCards).map(([system, systemCards]) => (
          <div className="scoring-system-group" key={system}>
            <div className="scoring-system-header">
              <div>
                <strong>{system}</strong>
                <small>{systemCards[0]?.purpose}</small>
              </div>
              <span>{systemCards.length} value{systemCards.length === 1 ? "" : "s"}</span>
            </div>
            <div className="scoring-card-grid">
              {systemCards.map((card) => (
                <article className={`scoring-card ${card.status}`} key={card.key}>
                  <div className="score-card-topline">
                    <p>{statusLabel(card.status)}</p>
                    {card.thresholdText ? <em>{card.thresholdText}</em> : null}
                  </div>
                  <strong>{card.value}</strong>
                  <span>{card.label}</span>
                  <b>{card.outcome}</b>
                  <small>{card.detail}</small>
                </article>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function firstAnswer(answers, keys) {
  for (const key of keys) {
    if (answers[key]) return answers[key];
  }
  return "";
}

function countAnsweredEntries(answers, fieldMap) {
  return Object.entries(answers).filter(([key, value]) => {
    const field = fieldMap.get(key);
    if (field && isCalculatedStaffField(field)) return false;
    if (Array.isArray(value)) return value.length > 0;
    return value !== "" && value !== null && value !== undefined && value !== false;
  }).length;
}

function hasMeaningfulAnswer(value) {
  if (Array.isArray(value)) return value.length > 0;
  return value !== "" && value !== null && value !== undefined && value !== false;
}

const FORM_AGE_RULES = [
  ["newborn-2-5-days", 0, 1, "newborn"],
  ["1-month-visit", 0, 2, "0-1 months"],
  ["2-months-visit", 1, 4, "2-3 months"],
  ["4-months-visit", 3, 6, "4-5 months"],
  ["6-months-visit", 5, 7, "6 months"],
  ["7-8-months-visit", 6, 9, "7-8 months"],
  ["9-months-visit", 8, 10, "9 months"],
  ["10-months-visit", 9, 12, "10-11 months"],
  ["12-months-visit-eagan", 11, 14, "12-13 months"],
  ["12-months-visit-maplewood", 11, 14, "12-13 months"],
  ["14-months-visit", 13, 15, "14 months"],
  ["15-months-visit", 14, 18, "15-17 months"],
  ["18-months-visit", 17, 20, "18-19 months"],
  ["20-months-visit", 19, 22, "20-21 months"],
  ["22-months-visit", 21, 24, "22-23 months"],
  ["2-year-visit-eagan", 23, 27, "24-26 months"],
  ["2-year-visit-maplewood", 23, 27, "24-26 months"],
  ["27-months-visit", 26, 30, "27-29 months"],
  ["30-months-visit", 29, 33, "30-32 months"],
  ["33-months-visit", 32, 36, "33-35 months"],
  ["3-year-visit", 35, 42, "3 years"],
  ["42-months-visit", 41, 48, "42-47 months"],
  ["4-year-visit", 47, 54, "4 years"],
  ["54-months-visit", 53, 60, "54-59 months"],
  ["5-year-visit", 59, 72, "5 years"],
  ["6-year-visit", 72, 84, "6 years"],
  ["7-year-visit", 84, 96, "7 years"],
  ["8-year-visit", 96, 108, "8 years"],
  ["9-year-visit", 108, 120, "9 years"],
  ["10-year-visit", 120, 132, "10 years"],
  ["11-year-visit", 132, 144, "11 years"],
  ["12-year-visit", 144, 156, "12 years"],
  ["13-14-year-visit", 156, 180, "13-14 years"],
  ["15-17-year-visit", 180, 216, "15-17 years"],
  ["18-21-year-visit", 216, 264, "18-21 years"],
  ["patient-portal-under-11", 0, 144, "under 12 years"],
  ["patient-portal-12-17", 144, 216, "12-17 years"],
  ["patient-portal-18-plus", 216, Infinity, "18 years and older"],
  ["child-act-4-11", 48, 144, "4-11 years"],
  ["asthma-act-12-plus", 144, Infinity, "12 years and older"],
  ["initial-anxiety-6-12", 72, 156, "6-12 years"],
  ["adult-adhd-asrs", 216, Infinity, "18 years and older"]
];

function ageRuleForForm(formId) {
  const rule = FORM_AGE_RULES.find(([id]) => id === formId);
  return rule ? { minMonths: rule[1], maxMonths: rule[2], label: rule[3] } : null;
}

function dateValueIsFuture(value) {
  if (!value) return false;
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return parsed > today;
}

function qualityItem(severity, label, detail) {
  return { severity, label, detail };
}

function getDataQualityWarnings({ submission, answers, scoringCards, staffFields }) {
  const warnings = [];
  const dob = firstAnswer(answers, ["date_of_birth", "baby_date_of_birth", "baby_dob", "birth_date", "dob", "epds_baby_date_of_birth"]);
  const patientName = submission.patientName && submission.patientName !== "Unnamed patient" ? submission.patientName : firstAnswer(answers, ["patient_name", "child_name", "baby_name", "patient_first_name"]);
  const phone = firstAnswer(answers, ["phone", "phone_number", "parent_phone", "caregiver_phone", "proxy_phone", "epds_phone"]);
  const caregiver = firstAnswer(answers, ["completed_by", "caregiver_name", "parent_guardian_name", "guardian_name", "psc17_caregiver_name", "bpsc_caregiver_name"]);
  const visitDate = firstAnswer(answers, ["visit_date", "date", "today_date"]);
  const age = calculateAge(dob);
  const ageRule = ageRuleForForm(submission.formId);
  const requiredStaffFields = staffFields.filter((field) => field.required && !isCalculatedStaffField(field));
  const missingStaffFields = requiredStaffFields.filter((field) => !hasMeaningfulAnswer(answers[field.id]));
  const incompleteScores = scoringCards.filter((card) => card.status === "incomplete");

  if (!patientName) warnings.push(qualityItem("high", "Patient name missing", "The submission could not identify a patient name."));
  if (!dob) warnings.push(qualityItem("high", "Date of birth missing", "Age-based routing and form fit cannot be verified."));
  if (dob && dateValueIsFuture(dob)) warnings.push(qualityItem("high", "Date of birth is in the future", "Confirm the DOB before charting this intake."));
  if (visitDate && dateValueIsFuture(visitDate)) warnings.push(qualityItem("medium", "Visit date is in the future", "Confirm whether this intake is for a future appointment."));
  if (age && ageRule && (age.totalMonths < ageRule.minMonths || age.totalMonths >= ageRule.maxMonths)) {
    warnings.push(qualityItem("high", "Age does not match selected form", `Patient age is about ${age.years}y ${age.months}m, but this form expects ${ageRule.label}.`));
  }
  if (!phone) warnings.push(qualityItem("medium", "Contact phone missing", "Staff may not be able to reach the family for follow-up."));
  if (!caregiver && age && age.years < 18) warnings.push(qualityItem("medium", "Caregiver name missing", "Pediatric submissions should identify the person completing the form."));
  if (incompleteScores.length) warnings.push(qualityItem("medium", "Calculated scoring incomplete", `${incompleteScores.length} calculated score${incompleteScores.length === 1 ? "" : "s"} could not be completed.`));
  if (missingStaffFields.length) warnings.push(qualityItem("low", "Required staff fields missing", `${missingStaffFields.length} required staff field${missingStaffFields.length === 1 ? "" : "s"} still need completion.`));

  return warnings;
}

function DataQualityPanel({ warnings }) {
  const highCount = warnings.filter((warning) => warning.severity === "high").length;
  const mediumCount = warnings.filter((warning) => warning.severity === "medium").length;
  if (!warnings.length) {
    return (
      <section className="data-quality-panel ready">
        <div className="data-quality-header">
          <div>
            <p className="eyebrow">Data quality</p>
            <h3>No quality warnings</h3>
          </div>
          <span className="progress-status ready">Clear</span>
        </div>
        <p>Basic demographics, routing, contact, and scoring checks look consistent.</p>
      </section>
    );
  }

  return (
    <section className={`data-quality-panel ${highCount ? "high" : "medium"}`}>
      <div className="data-quality-header">
        <div>
          <p className="eyebrow">Data quality</p>
          <h3>{warnings.length} warning{warnings.length === 1 ? "" : "s"}</h3>
        </div>
        <span className={`progress-status ${highCount ? "needs-work" : "ready"}`}>
          {highCount ? `${highCount} high` : `${mediumCount} medium`}
        </span>
      </div>
      <div className="data-quality-list">
        {warnings.map((warning) => (
          <article className={`data-quality-item ${warning.severity}`} key={`${warning.label}-${warning.detail}`}>
            <strong>{warning.label}</strong>
            <p>{warning.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function PatientReviewSummary({ submission, answers, fieldMap, scoringCards }) {
  const highFlags = submission.review?.flags?.filter((flag) => flag.severity === "high").length || 0;
  const mediumFlags = submission.review?.flags?.filter((flag) => flag.severity === "medium").length || 0;
  const concerningScores = scoringCards.filter((card) => card.status === "below" || card.status === "monitor").length;
  const answeredCount = countAnsweredEntries(answers, fieldMap);
  const dob = firstAnswer(answers, ["date_of_birth", "baby_date_of_birth", "baby_dob", "birth_date", "dob"]);
  const completedBy = firstAnswer(answers, ["completed_by", "caregiver_name", "parent_guardian_name", "guardian_name"]);
  const phone = firstAnswer(answers, ["phone", "phone_number", "parent_phone", "caregiver_phone"]);
  const templateVersion = submission.formTemplateVersion || submission.formTemplateSnapshot?.version;

  return (
    <section className="patient-review-summary">
      <div className="summary-stat">
        <span>Review</span>
        <strong>{submission.review?.label || "Routine"}</strong>
        <small>{highFlags} high / {mediumFlags} medium flags</small>
      </div>
      <div className="summary-stat">
        <span>Scores</span>
        <strong>{concerningScores}</strong>
        <small>values needing attention</small>
      </div>
      <div className="summary-stat">
        <span>Responses</span>
        <strong>{answeredCount}</strong>
        <small>answered fields</small>
      </div>
      <div className="summary-stat wide">
        <span>Patient context</span>
        <strong>{dob || "DOB not provided"}</strong>
        <small>{completedBy ? `Completed by ${completedBy}` : "Caregiver not provided"}{phone ? ` - ${phone}` : ""}</small>
      </div>
      <div className="summary-stat">
        <span>Template</span>
        <strong>{templateVersion ? `v${templateVersion}` : "Version unknown"}</strong>
        <small>{submission.formTemplateSnapshot?.sections?.length || "Current"} section reference</small>
      </div>
    </section>
  );
}

function getStaffReviewChecklist({ submission, staffFields, answers, scoringCards, auditEvents }) {
  const status = submission.status || "new";
  const hasReviewActivity = Boolean(submission.reviewedBy) || auditEvents.some((event) => event.action === "staff_review_updated");
  const hasPdfExport = auditEvents.some((event) => event.action === "pdf_exported");
  const requiredStaffFields = staffFields.filter((field) => field.required && !isCalculatedStaffField(field));
  const missingStaffFields = requiredStaffFields.filter((field) => !hasMeaningfulAnswer(answers[field.id]));
  const incompleteScores = scoringCards.filter((card) => card.status === "incomplete");
  const concernScores = scoringCards.filter((card) => card.status === "below" || card.status === "monitor");

  return [
    {
      key: "patient-answers",
      label: "Patient answers reviewed",
      state: hasReviewActivity || !["new", "draft"].includes(status) ? "ready" : "needs-work",
      detail: hasReviewActivity ? "Staff review activity recorded." : "Move into review or save a staff review after checking answers."
    },
    {
      key: "scoring",
      label: "Calculated scoring reviewed",
      state: incompleteScores.length ? "needs-work" : "ready",
      detail: scoringCards.length
        ? `${concernScores.length} attention score${concernScores.length === 1 ? "" : "s"} / ${incompleteScores.length} incomplete.`
        : "No calculated scoring for this form."
    },
    {
      key: "staff-fields",
      label: "Staff fields completed",
      state: missingStaffFields.length ? "needs-work" : "ready",
      detail: requiredStaffFields.length
        ? missingStaffFields.length
          ? `${missingStaffFields.length} required staff field${missingStaffFields.length === 1 ? "" : "s"} missing.`
          : "Required staff fields are complete."
        : "No required staff-only fields."
    },
    {
      key: "status",
      label: "Review status selected",
      state: ["in-review", "needs-follow-up", "needs-patient-follow-up", "ready-for-chart", "complete"].includes(status) ? "ready" : "needs-work",
      detail: `Current status: ${statusLabelText(status)}.`
    },
    {
      key: "review-saved",
      label: "Review saved",
      state: hasReviewActivity ? "ready" : "needs-work",
      detail: hasReviewActivity ? "Last review metadata is recorded." : "Save review once staff fields and scoring are checked."
    },
    {
      key: "pdf-export",
      label: "PDF exported",
      state: hasPdfExport ? "ready" : "optional",
      detail: hasPdfExport ? "PDF export is recorded in activity history." : "Recommended when the summary needs to be attached or shared."
    }
  ];
}

function statusTransitionGuardrails({ targetStatus, reviewChecklist, dataQualityWarnings, submission, scoringCards }) {
  if (!["ready-for-chart", "complete"].includes(targetStatus)) {
    return { blocked: [], warnings: [] };
  }

  const blocked = [];
  const warnings = [];
  const requiredChecklistIssues = reviewChecklist.filter((item) => item.key !== "status" && item.state === "needs-work");
  const highQualityWarnings = dataQualityWarnings.filter((item) => item.severity === "high");
  const mediumQualityWarnings = dataQualityWarnings.filter((item) => item.severity === "medium");
  const reviewFlags = submission?.review?.flags || [];
  const highReviewFlags = reviewFlags.filter((flag) => flag.severity === "high");
  const mediumReviewFlags = reviewFlags.filter((flag) => flag.severity === "medium");
  const concerningScores = scoringCards.filter((card) => card.status === "below" || card.status === "monitor");

  blocked.push(...requiredChecklistIssues.map((item) => item.label));
  blocked.push(...highQualityWarnings.map((item) => item.label));
  warnings.push(...mediumQualityWarnings.map((item) => item.label));
  warnings.push(...highReviewFlags.map((flag) => flag.label));
  warnings.push(...mediumReviewFlags.map((flag) => flag.label));
  warnings.push(...concerningScores.map((card) => `${card.label}: ${card.outcome}`));

  return {
    blocked: [...new Set(blocked)],
    warnings: [...new Set(warnings)].filter((item) => !blocked.includes(item))
  };
}

function StaffReviewChecklist({ items }) {
  const requiredItems = items.filter((item) => item.state !== "optional");
  const completedRequired = requiredItems.filter((item) => item.state === "ready").length;
  const allRequiredReady = completedRequired === requiredItems.length;

  return (
    <section className={`staff-review-checklist ${allRequiredReady ? "ready" : "needs-work"}`}>
      <div className="checklist-header">
        <div>
          <p className="eyebrow">Review checklist</p>
          <h3>{completedRequired}/{requiredItems.length} required ready</h3>
        </div>
        <span className={`progress-status ${allRequiredReady ? "ready" : "needs-work"}`}>
          {allRequiredReady ? "Ready" : "Needs work"}
        </span>
      </div>
      <div className="checklist-items">
        {items.map((item) => (
          <article className={`checklist-item ${item.state}`} key={item.key}>
            <span className="checklist-icon" aria-hidden="true">{item.state === "ready" ? "OK" : item.state === "optional" ? "i" : "!"}</span>
            <div>
              <strong>{item.label}</strong>
              <p>{item.detail}</p>
            </div>
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
    patient_draft_submitted: "Draft submitted",
    updated: "Submission updated",
    submission_updated: "Submission updated",
    status_changed: "Status changed",
    staff_review_updated: "Staff review updated",
    pdf_exported: "PDF exported",
    submission_viewed: "Submission viewed",
    staff_note_added: "Staff note added"
  };
  return labels[action] || String(action || "Activity").replaceAll("_", " ");
}

function actorLabel(event) {
  if (event.actorRole === "patient" || event.by === "patient") return "Patient";
  return event.actorName || event.actorEmail || event.by || event.actorId || "Staff user";
}

function auditTone(action) {
  if (action === "submission_created" || action === "patient_draft_submitted" || action === "created") return "created";
  if (action === "status_changed") return "status";
  if (action === "staff_review_updated") return "review";
  if (action === "pdf_exported") return "export";
  return "default";
}

function auditDescription(event) {
  const metadata = event.metadata || {};
  if (event.action === "submission_created" || event.action === "created") {
    return `${metadata.formName || "Intake form"} submitted${metadata.requiredMissingCount ? ` with ${metadata.requiredMissingCount} missing required item${metadata.requiredMissingCount === 1 ? "" : "s"}` : ""}.`;
  }
  if (event.action === "patient_draft_submitted") {
    return `${metadata.formName || "Intake form"} submitted from saved draft${metadata.resumeCode ? ` ${metadata.resumeCode}` : ""}.`;
  }
  if (event.action === "status_changed") {
    return `Status moved from ${statusLabelText(metadata.previousStatus || "new")} to ${statusLabelText(metadata.newStatus || "new")}.`;
  }
  if (event.action === "staff_review_updated") {
    const changedCount = metadata.changedAnswerCount || 0;
    return changedCount ? `${changedCount} staff response field${changedCount === 1 ? "" : "s"} updated.` : "Staff review was saved.";
  }
  if (event.action === "pdf_exported") {
    return `PDF summary exported${metadata.destination ? ` for ${metadata.destination}` : ""}.`;
  }
  return "Activity recorded on this submission.";
}

function auditBadges(event) {
  const metadata = event.metadata || {};
  const badges = [];
  if (metadata.formTemplateVersion) badges.push(`Template v${metadata.formTemplateVersion}`);
  if (metadata.newStatus) badges.push(`Status: ${statusLabelText(metadata.newStatus)}`);
  if (metadata.changedAnswerCount) badges.push(`${metadata.changedAnswerCount} changed fields`);
  if (metadata.reviewLockUpdated) badges.push("Review lock updated");
  if (metadata.exportFormat) badges.push(String(metadata.exportFormat).toUpperCase());
  return badges;
}

function AuditHistory({ events = [] }) {
  const orderedEvents = [...events].sort((a, b) => String(b.at || "").localeCompare(String(a.at || "")));
  if (!orderedEvents.length) return null;
  const latest = orderedEvents[0];

  return (
    <section className="audit-panel">
      <div className="detail-header compact-detail-header">
        <div>
          <p className="eyebrow">Activity timeline</p>
          <h3>Submission history</h3>
          <span className="audit-latest">Latest: {formatAuditAction(latest.action)}{latest.at ? ` on ${new Date(latest.at).toLocaleString()}` : ""}</span>
        </div>
        <span className="audit-count">{orderedEvents.length} events</span>
      </div>
      <div className="audit-timeline">
        {orderedEvents.map((event, index) => {
          const badges = auditBadges(event);
          return (
            <article className={`audit-event ${auditTone(event.action)}`} key={event.id || `${event.at}-${index}`}>
              <div className="audit-marker" />
              <div>
                <div className="audit-event-header">
                  <strong>{formatAuditAction(event.action)}</strong>
                  <span>{event.at ? new Date(event.at).toLocaleString() : "No timestamp"}</span>
                </div>
                <p>{auditDescription(event)}</p>
                <small>{actorLabel(event)}{event.actorRole ? ` - ${event.actorRole}` : ""}</small>
                {badges.length ? (
                  <div className="audit-badges">
                    {badges.map((badge) => <span key={badge}>{badge}</span>)}
                  </div>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function staffActorName(actor) {
  if (!actor) return "";
  return actor.name || actor.actorName || actor.email || actor.actorEmail || actor.id || actor.actorId || "";
}

function ReviewOwnership({ submission }) {
  const reviewedBy = submission.reviewedBy;
  const reviewLock = submission.reviewLock;
  const completedBy = submission.completedBy;
  if (!reviewedBy && !reviewLock && !completedBy) {
    return (
      <section className="review-ownership-panel">
        <p className="eyebrow">Review ownership</p>
        <h3>Not assigned</h3>
        <span>No staff review activity has been recorded yet.</span>
      </section>
    );
  }
  return (
    <section className="review-ownership-panel">
      <p className="eyebrow">Review ownership</p>
      <h3>{staffActorName(reviewLock?.lockedBy || reviewedBy) || "Staff reviewer"}</h3>
      {reviewedBy ? <span>Last reviewed by {staffActorName(reviewedBy)}{submission.reviewedAt ? ` on ${new Date(submission.reviewedAt).toLocaleString()}` : ""}</span> : null}
      {reviewLock ? <small>Soft lock active from {new Date(reviewLock.lockedAt).toLocaleString()} until {new Date(reviewLock.expiresAt).toLocaleString()}</small> : null}
      {completedBy ? <small>Completed by {staffActorName(completedBy)}{submission.completedAt ? ` on ${new Date(submission.completedAt).toLocaleString()}` : ""}</small> : null}
    </section>
  );
}

function exportSubmissionPdf({ submission, form, answers, staffFields, fieldMap, insights, scoringCards }) {
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
  const scoringRows = scoringCards.map((card) => `<tr><th>${escapeHtml(card.system)}<br><small>${escapeHtml(card.label)}</small></th><td><strong>${escapeHtml(card.value)} - ${escapeHtml(card.outcome)}</strong><br>${escapeHtml(card.thresholdText || "No fixed threshold")}<br>${escapeHtml(card.detail)}</td></tr>`).join("");
  const staffRows = staffFields.map((field) => `<tr><th>${escapeHtml(field.label)}</th><td>${escapeHtml(displayAnswer(answers[field.id]))}</td></tr>`).join("");
  const flagRows = (submission.review?.flags || []).map((flag) => `<span class="flag ${escapeHtml(flag.severity)}">${escapeHtml(flag.label)}</span>`).join("") || "<span class=\"flag low\">No automatic flags</span>";
  const report = `<!doctype html>
    <html><head><title>${escapeHtml(submission.patientName)} - Intake Summary</title>
    <style>
      body{font-family:Arial,sans-serif;color:#17213a;margin:32px;line-height:1.45}
      h1,h2{margin:0 0 8px} h2{margin-top:28px;font-size:18px;border-bottom:1px solid #d6dfed;padding-bottom:8px}
      .meta{color:#53657f;margin-bottom:18px}.flag{display:inline-block;margin:4px 6px 4px 0;padding:4px 9px;border-radius:999px;background:#e7edf7;font-size:12px}
      .flag.high{background:#f7d4d7;color:#8f1d2a}.flag.medium{background:#ffe8a8;color:#76510a}.flag.low{background:#dff3e7;color:#2c6b42}
      small{color:#53657f;font-weight:400}
      table{width:100%;border-collapse:collapse;margin-top:10px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #e5ebf4;padding:8px 10px}th{width:36%;color:#344765}
      @media print{button{display:none}body{margin:18px}}
    </style></head>
    <body>
      <button onclick="window.print()">Print / save PDF</button>
      <h1>${escapeHtml(submission.patientName)}</h1>
      <div class="meta">${escapeHtml(submission.formName)} | Template v${escapeHtml(submission.formTemplateVersion || submission.formTemplateSnapshot?.version || "unknown")} | ${escapeHtml(new Date(submission.createdAt).toLocaleString())} | Status: ${escapeHtml(statusLabelText(submission.status))}</div>
      <div class="meta">Reviewed by: ${escapeHtml(staffActorName(submission.reviewedBy) || "Not reviewed yet")}${submission.reviewedAt ? ` | ${escapeHtml(new Date(submission.reviewedAt).toLocaleString())}` : ""}</div>
      <h2>Review Flags</h2><div>${flagRows}</div>
      <h2>Calculated Scores</h2><table>${scoringRows || "<tr><td>No calculated scores for this form.</td></tr>"}</table>
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

function templateFromSubmissionSnapshot(submission) {
  const snapshot = submission?.formTemplateSnapshot;
  if (!snapshot?.id) return null;
  return {
    id: snapshot.id,
    name: snapshot.name || submission.formName,
    category: snapshot.category || submission.category,
    description: snapshot.description || "",
    estimatedMinutes: snapshot.estimatedMinutes,
    version: snapshot.version || submission.formTemplateVersion,
    status: "snapshot",
    sections: (snapshot.sections || []).map((section) => ({
      title: section.title || "Submitted section",
      content: section.content || [],
      fields: (section.fields || []).map((field) => ({
        ...field,
        options: Array.isArray(field.options) ? field.options : undefined,
        staffOnly: Boolean(field.staffOnly || field.owner === "staff")
      }))
    }))
  };
}

export function SubmissionsPage({ submissions, isLoading, detailLoading, selectedSubmission, forms, onSelect, onStatusChange, onRecordActivity, detailOnly = false, onBack, onLoadMore, hasMore = false, onQueryChange }) {
  const [statusFilter, setStatusFilter] = useState("");
  const [reviewFilter, setReviewFilter] = useState("");
  const [formFilter, setFormFilter] = useState("");
  const [queueSearch, setQueueSearch] = useState("");
  const [sortMode, setSortMode] = useState("priority");
  const [staffDraft, setStaffDraft] = useState({});
  const [staffSaving, setStaffSaving] = useState(false);
  const [staffMessage, setStaffMessage] = useState("");
  const formOptions = forms
    .map((form) => [form.id, form.name])
    .filter(([id, name]) => id && name)
    .sort((a, b) => String(a[1]).localeCompare(String(b[1])));

  useEffect(() => {
    if (!onQueryChange || detailOnly) return undefined;
    const timer = window.setTimeout(() => {
      onQueryChange({
        status: statusFilter,
        review: reviewFilter,
        formId: formFilter,
        search: queueSearch.trim(),
        sort: sortMode
      });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [detailOnly, formFilter, onQueryChange, queueSearch, reviewFilter, sortMode, statusFilter]);

  const visibleSubmissions = sortSubmissions(submissions.filter((submission) => {
    const statusMatch = statusMatches(submission.status, statusFilter);
    const review = submission.review || { flags: [] };
    const reviewMatch =
      !reviewFilter ||
      review.status === reviewFilter ||
      review.flags.some((flag) => flag.type === reviewFilter || flag.key === reviewFilter);
    const formMatch = formFilter ? submission.formId === formFilter : true;
    const searchMatch = queueSearch.trim() ? submissionSearchText(submission).includes(queueSearch.trim().toLowerCase()) : true;
    return statusMatch && reviewMatch && formMatch && searchMatch;
  }), sortMode);

  const activeSelectedForm = selectedSubmission ? forms.find((form) => form.id === selectedSubmission.formId) : null;
  const snapshotSelectedForm = selectedSubmission ? templateFromSubmissionSnapshot(selectedSubmission) : null;
  const selectedForm = snapshotSelectedForm || activeSelectedForm;
  const isUsingSnapshotTemplate = Boolean(snapshotSelectedForm);
  const selectedAnswers = selectedSubmission ? addCalculatedScores(selectedSubmission.formId, selectedSubmission.answers || {}) : {};
  const selectedInsights = selectedSubmission ? scoreInsightsForSubmission(selectedSubmission, selectedForm, selectedAnswers) : [];
  const selectedAuditEvents = selectedSubmission?.auditHistory || selectedSubmission?.audit || [];
  const scoringCards = selectedSubmission ? scoringCardsForSubmission(selectedSubmission, selectedAnswers) : [];
  const dashboardCounts = reviewCounts(submissions);
  const filteredCounts = reviewCounts(visibleSubmissions);
  const isInitialQueueLoading = isLoading && submissions.length === 0;
  const priorityQueue = sortSubmissions(submissions
    .filter((submission) => submission.review?.status === "needs-review" || ["needs-follow-up", "needs-patient-follow-up"].includes(submission.status))
    , "priority").slice(0, 5);
  const activeFilterCount = [statusFilter, reviewFilter, formFilter, queueSearch.trim()].filter(Boolean).length;
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
  const reviewChecklist = selectedSubmission
    ? getStaffReviewChecklist({ submission: selectedSubmission, staffFields, answers: staffDraft, scoringCards, auditEvents: selectedAuditEvents })
    : [];
  const dataQualityWarnings = selectedSubmission
    ? getDataQualityWarnings({ submission: selectedSubmission, answers: staffDraft, scoringCards, staffFields })
    : [];

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

  async function handleStatusChange(nextStatus) {
    if (!selectedSubmission) return;
    setStaffMessage("");

    const guardrails = statusTransitionGuardrails({
      targetStatus: nextStatus,
      reviewChecklist,
      dataQualityWarnings,
      submission: selectedSubmission,
      scoringCards
    });

    if (guardrails.blocked.length) {
      setStaffMessage(`Cannot mark ${statusLabelText(nextStatus)} yet. Resolve: ${guardrails.blocked.slice(0, 4).join(", ")}${guardrails.blocked.length > 4 ? ", and more" : ""}.`);
      return;
    }

    if (guardrails.warnings.length) {
      const confirmed = window.confirm(
        `This record still has review items before ${statusLabelText(nextStatus)}:\n\n` +
        guardrails.warnings.slice(0, 8).map((item) => `- ${item}`).join("\n") +
        `${guardrails.warnings.length > 8 ? "\n- More items not shown" : ""}\n\nContinue anyway?`
      );
      if (!confirmed) return;
    }

    try {
      await onStatusChange(selectedSubmission.id, nextStatus, staffDraft);
      setStaffMessage(`Status updated to ${statusLabelText(nextStatus)}.`);
    } catch (error) {
      setStaffMessage(error.message || "Unable to update status.");
    }
  }

  async function handleExportPdf() {
    if (!selectedSubmission) return;
    exportSubmissionPdf({ submission: selectedSubmission, form: selectedForm, answers: selectedAnswers, staffFields, fieldMap, insights: selectedInsights, scoringCards });
    if (onRecordActivity) {
      await onRecordActivity(selectedSubmission.id, "pdf_exported", {
        exportFormat: "pdf",
        destination: "staff review",
        scoringCardCount: scoringCards.length,
        reviewFlagCount: selectedSubmission.review?.flags?.length || 0
      });
    }
  }

  const detailContent = (
    <article className={`submission-detail ${detailOnly ? "submission-detail-page" : ""}`}>
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
            <div className="detail-actions">
              {detailOnly ? <button className="secondary-button" type="button" onClick={onBack}>Back to queue</button> : null}
              <select className="select-input" aria-label="Submission status" value={selectedSubmission.status} onChange={(event) => handleStatusChange(event.target.value)}>
                {SUBMISSION_STATUSES.map(([status, label]) => (
                  <option value={status} key={status}>{label}</option>
                ))}
              </select>
              <button className="secondary-button" type="button" onClick={handleExportPdf}>Export PDF</button>
            </div>
          </div>
          <section className={`template-source-banner ${isUsingSnapshotTemplate ? "snapshot" : "current"}`}>
            <strong>{isUsingSnapshotTemplate ? "Reviewing submitted template snapshot" : "Reviewing current active template"}</strong>
            <span>
              {isUsingSnapshotTemplate
                ? `This record uses the form structure saved at submission time${selectedForm?.version ? `, version ${selectedForm.version}` : ""}.`
                : "This older record has no saved snapshot, so labels and staff fields come from the current active template."}
            </span>
          </section>
          <PatientReviewSummary submission={selectedSubmission} answers={selectedAnswers} fieldMap={fieldMap} scoringCards={scoringCards} />
          <div className="submission-review-workspace">
            <div className="review-main-column">
              <ScoringOverview cards={scoringCards} />
              <AsqScoreTable formId={selectedSubmission.formId} answers={selectedAnswers} submitted />
              <section className="answer-panel">
                <div className="detail-header compact-detail-header">
                  <div>
                    <p className="eyebrow">Submitted answers</p>
                    <h3>Patient and form responses</h3>
                  </div>
                </div>
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
              </section>
            </div>
            <aside className="review-side-column">
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
              <DataQualityPanel warnings={dataQualityWarnings} />
              <StaffReviewChecklist items={reviewChecklist} />
              <ReviewOwnership submission={selectedSubmission} />
              {staffMessage ? <div className="message staff-status-message" role="status">{staffMessage}</div> : null}
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
                </section>
              ) : null}
              <AuditHistory events={selectedAuditEvents} />
            </aside>
          </div>
        </>
      )}
    </article>
  );

  if (detailOnly) {
    return (
      <section className="view active" aria-label="Submission detail">
        <div className="panel submission-detail-shell">
          {detailContent}
        </div>
      </section>
    );
  }

  return (
    <section className="view active" aria-label="Submissions">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Submissions</h2>
            <p>
              {isInitialQueueLoading
                ? "Loading intake records."
                : `${visibleSubmissions.length} of ${submissions.length} records shown${activeFilterCount ? ` with ${activeFilterCount} active filter${activeFilterCount === 1 ? "" : "s"}` : ""}.`}
            </p>
          </div>
          <div className="submission-controls">
            <div className="queue-search-control" role="search">
              <label htmlFor="submission-search">Search queue</label>
              <input
                id="submission-search"
                className="search-input"
                type="search"
                placeholder="Patient, form, flag, status"
                value={queueSearch}
                onChange={(event) => setQueueSearch(event.target.value)}
              />
              {queueSearch ? <button className="filter-clear" type="button" onClick={() => setQueueSearch("")}>Clear</button> : null}
            </div>
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
            <div className="queue-filter-row">
              <select className="select-input" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} aria-label="Filter by status">
                <option value="">All statuses</option>
                <option value="draft">Draft</option>
                <option value="new">New</option>
                <option value="in-review">In review</option>
                <option value="needs-patient-follow-up">Needs patient follow-up</option>
                <option value="ready-for-chart">Ready for chart</option>
                <option value="complete">Completed</option>
              </select>
              <select className="select-input" value={formFilter} onChange={(event) => setFormFilter(event.target.value)} aria-label="Filter by form">
                <option value="">All forms</option>
                {formOptions.map(([formId, formName]) => <option value={formId} key={formId}>{formName}</option>)}
              </select>
              <select className="select-input" value={sortMode} onChange={(event) => setSortMode(event.target.value)} aria-label="Sort queue">
                <option value="priority">Priority first</option>
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
                <option value="patient">Patient A-Z</option>
                <option value="form">Form A-Z</option>
              </select>
              {activeFilterCount ? (
                <button className="ghost-button" type="button" onClick={() => {
                  setStatusFilter("");
                  setReviewFilter("");
                  setFormFilter("");
                  setQueueSearch("");
                }}>Reset filters</button>
              ) : null}
            </div>
          </div>
        </div>

        {isInitialQueueLoading ? (
          <section className="staff-dashboard loading-dashboard" aria-busy="true" aria-label="Loading submission summary">
            {["Needs review", "New", "Patient follow-up", "Ready for chart", "Showing"].map((label) => (
              <div className="dashboard-stat loading-stat" key={label}>
                <span className="loading-value">...</span>
                <strong>{label}</strong>
                <p>Loading latest records</p>
              </div>
            ))}
            <div className="priority-queue loading-priority">
              <div>
                <p className="eyebrow">Priority queue</p>
                <strong>Review next</strong>
              </div>
              <p>Loading priority records.</p>
            </div>
          </section>
        ) : (
          <section className="staff-dashboard">
            <div className="dashboard-stat urgent">
              <span>{dashboardCounts.needsReview}</span>
              <strong>Needs review</strong>
              <p>{dashboardCounts.high} high priority flags</p>
            </div>
            <div className="dashboard-stat">
              <span>{dashboardCounts.new}</span>
              <strong>New</strong>
              <p>{dashboardCounts.draft} draft records</p>
            </div>
            <div className="dashboard-stat">
              <span>{dashboardCounts.followUp}</span>
              <strong>Patient follow-up</strong>
              <p>Needs patient outreach</p>
            </div>
            <div className="dashboard-stat complete">
              <span>{dashboardCounts.readyForChart}</span>
              <strong>Ready for chart</strong>
              <p>{dashboardCounts.complete} completed</p>
            </div>
            <div className="dashboard-stat filtered">
              <span>{visibleSubmissions.length}</span>
              <strong>Showing</strong>
              <p>{filteredCounts.needsReview} need review in this view</p>
            </div>
            <div className="priority-queue">
              <div>
                <p className="eyebrow">Priority queue</p>
                <strong>Review next</strong>
              </div>
              {priorityQueue.length ? priorityQueue.map((submission) => (
                <button key={submission.id} type="button" onClick={() => onSelect(submission.id)}>
                  <span>{submission.patientName}</span>
                  <small>{submission.review?.flags?.[0]?.label || statusLabelText(submission.status)}</small>
                </button>
              )) : <p>No priority submissions right now.</p>}
            </div>
          </section>
        )}

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
                  <span className="status-badge">{statusLabelText(submission.status)}</span>
                </div>
                {submission.review?.flags?.length ? (
                  <div className="review-flag-list">
                    {submission.review.flags.slice(0, 3).map((flag) => <span className={`review-flag ${flag.severity}`} key={flag.key}>{flag.label}</span>)}
                  </div>
                ) : null}
              </button>
            )) : (
              <div className="empty-state">
                <h2>{submissions.length ? "No matching submissions" : "No submissions"}</h2>
                <p>{submissions.length ? "Adjust search, filters, or sorting to widen the queue." : "Submitted intakes will appear here."}</p>
              </div>
            )}
            {hasMore ? (
              <button className="secondary-button load-more-button" type="button" onClick={onLoadMore} disabled={isLoading}>
                {isLoading ? "Loading" : "Load more"}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  );
}
