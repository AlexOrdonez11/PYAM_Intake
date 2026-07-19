import { calculateAsqScores } from "./asqScoring";
import { addCalculatedScores } from "./calculatedScores";

function numberValue(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function addInsight(insights, key, label, value, status, detail) {
  if (value === null || value === undefined || value === "") return;
  insights.push({ key, label, value: String(value), status, detail });
}

export function scoreInsightsForSubmission(submission, form, answers = null) {
  if (!submission) return [];

  const scoredAnswers = answers || addCalculatedScores(submission.formId, submission.answers || {});
  const insights = [];
  const asqScores = calculateAsqScores(submission.formId, scoredAnswers);

  asqScores.forEach((score) => {
    const detailByZone = {
      below: "Delayed range. Staff should review development concerns and consider referral or follow-up.",
      monitor: "Close to cutoff. Staff may provide activities, monitor, and consider rescreening.",
      above: "On schedule for this area based on submitted ASQ answers.",
      incomplete: "Not enough answered ASQ items to calculate this area."
    };
    addInsight(insights, `asq-${score.key}`, `ASQ ${score.label}`, score.total === null ? "Incomplete" : `${score.total}/60`, score.zone.key, detailByZone[score.zone.key]);
  });

  const scoreRules = [
    ["epds_total_score", "EPDS", 10, "Elevated EPDS score. Review mood symptoms and self-harm item."],
    ["phq2_total_score", "PHQ-2", 3, "Positive depression prescreen. Consider fuller depression screening."],
    ["phqa_total_score", "PHQ-A", 10, "Moderate or higher adolescent depression range."],
    ["phq9_total_score", "PHQ-9", 10, "Moderate or higher depression range."],
    ["gad7_total_score", "GAD-7", 10, "Moderate or higher anxiety range."],
    ["ppsc_total_score", "PPSC", 9, "Elevated preschool behavioral symptom score."],
    ["psc17_total_score", "PSC-17", 15, "Positive PSC-17 total screen."],
    ["mchat_risk_score", "M-CHAT", 3, "Autism screening risk range. Review risk level and follow-up workflow."],
    ["crafft_part_b_yes_count", "CRAFFT Part B", 2, "Positive substance-use risk screen."],
    ["act_total_score", "ACT", 20, "ACT scores of 19 or less may indicate asthma is not controlled.", true],
    ["cact_total_score", "C-ACT", 20, "C-ACT scores of 19 or less may indicate asthma is not controlled.", true],
    ["asrs_part_a_positive_count", "ASRS Part A", 4, "Four or more positive Part A items is consistent with a positive adult ADHD screen."],
    ["ace_total_symptom_score", "ACE symptom score", 1, "Any new post-injury symptoms support clinical concussion review."],
    ["ace_red_flag_count", "ACE red flags", 1, "Any red flag should prompt urgent clinical review."]
  ];

  scoreRules.forEach(([key, label, threshold, detail, lowerIsConcerning]) => {
    const value = numberValue(scoredAnswers[key]);
    if (value === null) return;
    const concerning = lowerIsConcerning ? value < threshold : value >= threshold;
    addInsight(insights, key, label, value, concerning ? "below" : "above", concerning ? detail : "No automatic threshold flag from this score.");
  });

  ["child_scared", "parent_scared"].forEach((prefix) => {
    const label = prefix === "child_scared" ? "Child SCARED" : "Parent SCARED";
    const total = numberValue(scoredAnswers[`${prefix}_total_score`]);
    if (total !== null) {
      addInsight(insights, `${prefix}_total_score`, label, total, total >= 25 ? "below" : "above", total >= 25 ? "Total anxiety cutoff met." : "Total anxiety cutoff not met.");
    }
  });

  const vanderbiltPrefixes = [
    ["vanderbilt_parent", "Vanderbilt Parent"],
    ["vanderbilt_teacher", "Vanderbilt Teacher"],
    ["vanderbilt_parent_followup", "Vanderbilt Parent Follow-up"],
    ["vanderbilt_teacher_followup", "Vanderbilt Teacher Follow-up"]
  ];
  vanderbiltPrefixes.forEach(([prefix, label]) => {
    const impairment = scoredAnswers[`${prefix}_impairment_present`];
    if (impairment) {
      addInsight(insights, `${prefix}_impairment_present`, label, impairment, impairment === "Yes" ? "monitor" : "above", impairment === "Yes" ? "At least one performance item is in an impairment range." : "No performance impairment item was automatically identified.");
    }
  });

  if (!insights.length && form) {
    addInsight(insights, "no-scored-fields", form.name || form.title, "No score", "incomplete", "This form has no automatic scoring rules yet.");
  }

  return insights;
}
