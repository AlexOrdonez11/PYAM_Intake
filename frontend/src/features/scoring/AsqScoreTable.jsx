import { calculateAsqScores, getAsqScoreConfig } from "./asqScoring";

const SCORE_MAX = 60;
const SCORE_TICKS = [0, 15, 30, 45, 60];

function percent(value) {
  return `${Math.max(0, Math.min(SCORE_MAX, value)) / SCORE_MAX * 100}%`;
}

function ScoreLegendRow({ score }) {
  const belowWidth = percent(score.zones.belowMax);
  const monitorLeft = percent(score.zones.belowMax);
  const monitorWidth = percent(score.zones.monitorMax - score.zones.belowMax);
  const aboveLeft = percent(score.zones.monitorMax);
  const totalLeft = score.total === null ? "0%" : percent(score.total);

  return (
    <div className={`asq-range-row ${score.zone.key}`}>
      <div className="asq-range-label">
        <strong>{score.label}</strong>
        <span>{score.total === null ? "Incomplete" : `${score.total}/60`}</span>
      </div>
      <div className="asq-range-track" aria-label={`${score.label} scoring range`}>
        <span className="asq-range below" style={{ width: belowWidth }} />
        <span className="asq-range monitor" style={{ left: monitorLeft, width: monitorWidth }} />
        <span className="asq-range above" style={{ left: aboveLeft, width: percent(SCORE_MAX - score.zones.monitorMax) }} />
        {score.total !== null ? (
          <span className="asq-score-marker" style={{ left: totalLeft }}>
            <span>{score.total}</span>
          </span>
        ) : null}
      </div>
    </div>
  );
}

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
      <div className="asq-legend" aria-label="ASQ-3 score range legend">
        <div className="asq-legend-head">
          <div>
            <h4>Score Range Legend</h4>
            <p>Marker moves as answers update. Ranges follow the cutoff table for this visit.</p>
          </div>
          <div className="asq-legend-key">
            <span><i className="below" /> Below cutoff</span>
            <span><i className="monitor" /> Monitor</span>
            <span><i className="above" /> On schedule</span>
          </div>
        </div>
        <div className="asq-scale">
          {SCORE_TICKS.map((tick) => <span key={tick} style={{ left: percent(tick) }}>{tick}</span>)}
        </div>
        <div className="asq-range-list">
          {scores.map((score) => <ScoreLegendRow key={score.key} score={score} />)}
        </div>
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
