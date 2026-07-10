import { calculateAsqScores } from "./asqScoring";
import { calculateBehavioralScores } from "./behavioralScoring";

export function addCalculatedScores(formId, answers) {
  const next = { ...answers };

  for (const score of calculateAsqScores(formId, answers)) {
    next[score.totalFieldId] = score.total === null ? "" : String(score.total);
    next[score.summaryFieldId] = score.total === null ? "" : String(score.total);
    next[score.zoneFieldId] = score.zone.value;
  }

  Object.assign(next, calculateBehavioralScores(answers));
  return next;
}
