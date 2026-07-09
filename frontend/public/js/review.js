function reviewFlagsForSubmission(submission) {
  const answers = submission.answers || {};
  const flags = [];
  const asqScores = calculateAsqScores(submission.formId, answers);

  const belowCount = asqScores.filter((score) => score.zone.key === "below").length;
  const monitorCount = asqScores.filter((score) => score.zone.key === "monitor").length;
  const incompleteCount = asqScores.filter((score) => score.zone.key === "incomplete").length;

  if (belowCount) flags.push({ key: "asq-below", type: "asq", severity: "high", label: `${belowCount} ASQ below cutoff` });
  if (monitorCount) flags.push({ key: "asq-monitor", type: "asq", severity: "medium", label: `${monitorCount} ASQ monitor` });
  if (incompleteCount) flags.push({ key: "asq-incomplete", type: "asq", severity: "low", label: "ASQ incomplete" });

  const selfHarm = ["phqa_9_self_harm", "phqa_suicide_ever", "phqa_suicide_attempt"].some((key) => {
    const value = String(answers[key] || "");
    return value && value !== "No" && !value.startsWith("Not at all");
  });
  if (selfHarm) flags.push({ key: "self-harm", type: "behavioral", severity: "high", label: "Self-harm review" });

  const phqaModerate = Object.entries(answers).some(([key, value]) => key.startsWith("phqa_") && String(value).includes("(2)"));
  if (phqaModerate) flags.push({ key: "phqa", type: "behavioral", severity: "medium", label: "PHQ-A symptom review" });

  const crafftPositive = Object.entries(answers).some(([key, value]) => key.startsWith("crafft_") && value === "Yes");
  if (crafftPositive) flags.push({ key: "crafft", type: "behavioral", severity: "medium", label: "CRAFFT positive" });

  const gadScore = Number(answers.gad7_total_score || 0);
  if (gadScore >= 10) flags.push({ key: "gad7", type: "behavioral", severity: "medium", label: "GAD-7 elevated" });

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

function enrichSubmission(submission) {
  const review = submission.answers ? reviewFlagsForSubmission(submission) : submission.review || { flags: [], status: "unknown", label: "Review pending" };
  return { ...submission, review };
}

