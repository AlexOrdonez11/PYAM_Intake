import { calculateAsqScores, getAsqScoreConfig } from "./asqScoring";

export function AsqScoreTable({ formId, answers = {}, submitted = false }) {
  const config = getAsqScoreConfig(formId);
  if (!config.length) return null;

  const scores = calculateAsqScores(formId, answers);

  return (
    <section className="score-panel" data-staff-only={!submitted ? true : undefined}>
      <div className="score-panel-header">
        <div>
          <p className="eyebrow">Staff scoring</p>
          <h3>ASQ-3 Score Summary</h3>
        </div>
        <span className="score-help">{submitted ? "Calculated from submitted answers" : "Auto-calculates from patient answers"}</span>
      </div>
      <div className="score-table-wrap">
        <table className="score-table" aria-label="ASQ-3 score summary">
          <thead>
            <tr>
              <th>Area</th>
              <th>Cutoff</th>
              <th>Total</th>
              <th>Interpretation</th>
              <th>Answered</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((score) => {
              const answered = score.itemScores.filter((value) => value !== null).length;
              return (
                <tr key={score.key} className={`score-row ${score.zone.key}`}>
                  <td>{score.label}</td>
                  <td>{score.cutoff.toFixed(2)}</td>
                  <td>{score.total === null ? "-" : score.total}</td>
                  <td><span className="score-zone">{score.zone.label}</span></td>
                  <td>{answered}/6</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
