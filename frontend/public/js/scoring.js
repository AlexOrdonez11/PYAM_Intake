function getAsqScoreConfig(formId) {
  return ASQ_2_MONTH_SCORE_CONFIG[formId] || [];
}

function getAsqAnswerScore(value) {
  if (value === "Yes") return 10;
  if (value === "Sometimes") return 5;
  if (value === "Not Yet") return 0;
  return null;
}

function getAsqZone(area, total) {
  if (total === null) return { key: "incomplete", label: "Incomplete", value: "" };
  if (total <= area.zones.belowMax) return { key: "below", label: "Below cutoff", value: "Below cutoff" };
  if (total <= area.zones.monitorMax) return { key: "monitor", label: "Close to cutoff", value: "Close to cutoff" };
  return { key: "above", label: "On schedule", value: "Above cutoff" };
}

function calculateAsqScores(formId, answers) {
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

function renderAsqScoreTable(formId) {
  const config = getAsqScoreConfig(formId);
  if (!config.length) return "";

  return `
    <section class="score-panel" data-staff-only>
      <div class="score-panel-header">
        <div>
          <p class="eyebrow">Staff scoring</p>
          <h3>ASQ-3 Score Summary</h3>
        </div>
        <span class="score-help">Auto-calculates from patient answers</span>
      </div>
      <div class="score-table-wrap">
        <table class="score-table" aria-label="ASQ-3 score summary">
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
            ${config
              .map(
                (area) => `
                  <tr data-score-area="${area.key}" class="score-row incomplete">
                    <td>${escapeHtml(area.label)}</td>
                    <td>${area.cutoff.toFixed(2)}</td>
                    <td class="score-total">-</td>
                    <td><span class="score-zone">Incomplete</span></td>
                    <td class="score-answered">0/6</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderAsqSubmissionScoreTable(formId, answers) {
  const scores = calculateAsqScores(formId, answers || {});
  if (!scores.length) return "";

  return `
    <section class="score-panel">
      <div class="score-panel-header">
        <div>
          <p class="eyebrow">Staff scoring</p>
          <h3>ASQ-3 Score Summary</h3>
        </div>
        <span class="score-help">Calculated from submitted answers</span>
      </div>
      <div class="score-table-wrap">
        <table class="score-table" aria-label="Submitted ASQ-3 score summary">
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
            ${scores
              .map((score) => {
                const answered = score.itemScores.filter((value) => value !== null).length;
                return `
                  <tr class="score-row ${score.zone.key}">
                    <td>${escapeHtml(score.label)}</td>
                    <td>${score.cutoff.toFixed(2)}</td>
                    <td>${score.total === null ? "-" : score.total}</td>
                    <td><span class="score-zone">${escapeHtml(score.zone.label)}</span></td>
                    <td>${answered}/6</td>
                  </tr>
                `;
              })
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function syncAsqScores() {
  const form = getSelectedForm();
  if (!form) return;
  const config = getAsqScoreConfig(form.id);
  if (!config.length) return;

  const answers = collectAnswers(form);
  const scores = calculateAsqScores(form.id, answers);

  scores.forEach((score) => {
    const row = els.intakeForm.querySelector(`[data-score-area="${CSS.escape(score.key)}"]`);
    const answered = score.itemScores.filter((value) => value !== null).length;
    if (row) {
      row.className = `score-row ${score.zone.key}`;
      row.querySelector(".score-total").textContent = score.total === null ? "-" : String(score.total);
      row.querySelector(".score-zone").textContent = score.zone.label;
      row.querySelector(".score-answered").textContent = `${answered}/6`;
    }

    [score.totalFieldId, score.summaryFieldId].forEach((fieldId) => {
      const control = els.intakeForm.querySelector(`[name="${CSS.escape(fieldId)}"]`);
      if (control) control.value = score.total === null ? "" : String(score.total);
    });

    const zoneControl = els.intakeForm.querySelector(`[name="${CSS.escape(score.zoneFieldId)}"]`);
    if (zoneControl) zoneControl.value = score.zone.value;
  });
}

