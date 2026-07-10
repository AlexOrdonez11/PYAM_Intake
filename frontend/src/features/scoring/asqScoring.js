import { ASQ_2_MONTH_SCORE_CONFIG } from "./asqConfig";

export function getAsqScoreConfig(formId) {
  return ASQ_2_MONTH_SCORE_CONFIG[formId] || [];
}

export function getAsqAnswerScore(value) {
  if (value === "Yes") return 10;
  if (value === "Sometimes") return 5;
  if (value === "Not Yet") return 0;
  return null;
}

export function getAsqZone(area, total) {
  if (total === null) return { key: "incomplete", label: "Incomplete", value: "" };
  if (total <= area.zones.belowMax) return { key: "below", label: "Delayed", value: "Delayed" };
  if (total <= area.zones.monitorMax) return { key: "monitor", label: "Close to cutoff", value: "Close to cutoff" };
  return { key: "above", label: "On schedule", value: "Above cutoff" };
}

export function calculateAsqScores(formId, answers) {
  return getAsqScoreConfig(formId).map((area) => {
    const itemScores = Array.from({ length: 6 }, (_, index) => {
      const value = answers[`${area.fieldPrefix}${index + 1}`];
      return getAsqAnswerScore(value);
    });
    const complete = itemScores.every((score) => score !== null);
    const total = complete ? itemScores.reduce((sum, score) => sum + score, 0) : null;
    const zone = getAsqZone(area, total);
    return { ...area, itemScores, complete, total, zone };
  });
}
