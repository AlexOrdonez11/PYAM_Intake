import { calculateAsqScores } from "../scoring/asqScoring";
import { calculateEpdsTotal } from "../scoring/behavioralScoring";

export function reviewFlagsForSubmission(submission) {
  const answers = submission.answers || {};
  const flags = [];
  const asqScores = calculateAsqScores(submission.formId, answers);

  const belowCount = asqScores.filter((score) => score.zone.key === "below").length;
  const monitorCount = asqScores.filter((score) => score.zone.key === "monitor").length;
  const incompleteCount = asqScores.filter((score) => score.zone.key === "incomplete").length;

  if (belowCount) flags.push({ key: "asq-below", type: "asq", severity: "high", label: `${belowCount} ASQ delayed` });
  if (monitorCount) flags.push({ key: "asq-monitor", type: "asq", severity: "medium", label: `${monitorCount} ASQ monitor` });
  if (incompleteCount) flags.push({ key: "asq-incomplete", type: "asq", severity: "low", label: "ASQ incomplete" });

  const selfHarm = ["phqa_9_self_harm", "phqa_suicide_ever", "phqa_suicide_attempt"].some((key) => {
    const value = String(answers[key] || "");
    return value && value !== "No" && !value.startsWith("Not at all");
  });
  if (selfHarm) flags.push({ key: "self-harm", type: "behavioral", severity: "high", label: "Self-harm review" });

  const epdsTotal = calculateEpdsTotal(answers);
  if (epdsTotal !== null && epdsTotal >= 10) {
    flags.push({ key: "epds", type: "behavioral", severity: "medium", label: "EPDS elevated" });
  }
  const epdsSelfHarm = ["epds_10", "epds_self_harm"].some((key) => {
    const value = String(answers[key] || "");
    return value && !["Never", "No, never", "No, not at all"].some((safeValue) => value.startsWith(safeValue));
  });
  if (epdsSelfHarm) flags.push({ key: "epds-self-harm", type: "behavioral", severity: "high", label: "EPDS self-harm review" });

  const phqaModerate = Object.entries(answers).some(([key, value]) => key.startsWith("phqa_") && String(value).includes("(2)"));
  if (phqaModerate) flags.push({ key: "phqa", type: "behavioral", severity: "medium", label: "PHQ-A symptom review" });

  const crafftPositive = Object.entries(answers).some(([key, value]) => key.startsWith("crafft_") && value === "Yes");
  if (crafftPositive) flags.push({ key: "crafft", type: "behavioral", severity: "medium", label: "CRAFFT positive" });

  const gadScore = Number(answers.gad7_total_score || 0);
  if (gadScore >= 10) flags.push({ key: "gad7", type: "behavioral", severity: "medium", label: "GAD-7 elevated" });

  const phq9Score = Number(answers.phq9_total_score || 0);
  if (phq9Score >= 10) flags.push({ key: "phq9", type: "behavioral", severity: "medium", label: "PHQ-9 elevated" });

  if (answers.phq9_9_self_harm && !String(answers.phq9_9_self_harm).startsWith("Not at all")) {
    flags.push({ key: "phq9-self-harm", type: "behavioral", severity: "high", label: "PHQ-9 self-harm review" });
  }

  const ppscScore = Number(answers.ppsc_total_score || 0);
  if (ppscScore >= 9) flags.push({ key: "ppsc", type: "behavioral", severity: "medium", label: "PPSC elevated" });

  const mchatScore = Number(answers.mchat_risk_score || 0);
  if (mchatScore >= 8) flags.push({ key: "mchat-high", type: "behavioral", severity: "high", label: "M-CHAT high risk" });
  else if (mchatScore >= 3) flags.push({ key: "mchat-medium", type: "behavioral", severity: "medium", label: "M-CHAT medium risk" });

  if (answers.sdoh_help_wanted === "Yes") {
    flags.push({ key: "sdoh", type: "social", severity: "medium", label: "SDOH help requested" });
  }

  if (submission.status === "needs-follow-up") {
    flags.push({ key: "status-follow-up", type: "status", severity: "high", label: "Marked follow-up" });
  }

  const hasReviewFlag = flags.some((flag) => ["high", "medium"].includes(flag.severity));
  return {
    flags,
    status: hasReviewFlag ? "needs-review" : submission.status === "complete" ? "complete" : "routine",
    label: hasReviewFlag ? "Needs review" : submission.status === "complete" ? "Complete" : "Routine"
  };
}

export function enrichSubmission(submission) {
  const review = submission.answers ? reviewFlagsForSubmission(submission) : submission.review || { flags: [], status: "unknown", label: "Review pending" };
  return { ...submission, review };
}
