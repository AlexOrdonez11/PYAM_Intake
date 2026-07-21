import { FormRenderer } from "../features/forms/FormRenderer";
import { BrandLogo } from "../components/layout/BrandLogo";

export function IntakePage({
  forms,
  selectedForm,
  selectedFormId,
  setSelectedFormId,
  search,
  setSearch,
  showAllForms,
  routingComplete,
  recommendedFormIds,
  completedFormIds,
  answers,
  mode,
  onAnswerChange,
  onSubmit,
  onClear,
  onStartOver,
  message,
  error,
  completionNotice,
  draftNotice,
  resumeSaving,
  onSaveResumeDraft,
  onDiscardDraft
}) {
  const query = search.trim().toLowerCase();
  const baseForms = showAllForms ? forms : forms.filter((form) => recommendedFormIds.includes(form.id));
  const visibleForms = baseForms.filter((form) => [form.name, form.category, form.description].join(" ").toLowerCase().includes(query));

  return (
    <section className="view active" aria-label="Patient Intake">
      <div className="intake-brand-row">
        <BrandLogo tone="light" />
      </div>
      <div className="workspace">
        <section className="panel form-picker-panel" aria-label="Available forms">
          <div className="panel-header">
            <div>
              <h2>{showAllForms ? "All Forms" : "Forms to Complete"}</h2>
              <p>
                {showAllForms
                  ? "Staff view is active. All available forms are visible."
                  : routingComplete
                    ? `${visibleForms.length} pending form${visibleForms.length === 1 ? "" : "s"} for this intake.`
                    : "Complete the start questions above to see the right forms."}
              </p>
            </div>
            <div className="form-filter" role="search">
              <label htmlFor="form-search">Search forms</label>
              <div className="form-filter-control">
                <input
                  id="form-search"
                  className="search-input"
                  type="search"
                  placeholder="Search by form or keyword"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
                {search ? <button className="filter-clear" type="button" onClick={() => setSearch("")}>Clear</button> : null}
              </div>
            </div>
          </div>
          <div className="form-list">
            {visibleForms.length ? visibleForms.map((form) => (
              <button className={`form-card ${form.id === selectedFormId ? "active" : ""} ${completedFormIds.includes(form.id) ? "completed" : ""}`} key={form.id} onClick={() => setSelectedFormId(form.id)} type="button">
                <strong>
                  {form.name}
                  {completedFormIds.includes(form.id) ? <span className="form-card-status">Complete</span> : null}
                </strong>
                <span className="form-card-meta-line">
                  <span>{form.category}</span>
                  <span className="form-card-duration">{form.estimatedMinutes} min</span>
                </span>
              </button>
            )) : (
              <div className="empty-state compact-empty">
                <h2>{routingComplete ? "No matching forms" : "Start above"}</h2>
                <p>{routingComplete ? "Adjust the start questions or use staff override." : "Patients will only see forms after routing."}</p>
              </div>
            )}
          </div>
        </section>

        <section className="panel intake-panel" aria-label="Selected form">
          <FormRenderer
            form={selectedForm}
            answers={answers}
            mode={mode}
            onAnswerChange={onAnswerChange}
            onSubmit={onSubmit}
            onClear={onClear}
            onStartOver={onStartOver}
            message={message}
            error={error}
            completionNotice={completionNotice}
            draftNotice={draftNotice}
            resumeSaving={resumeSaving}
            onSaveResumeDraft={onSaveResumeDraft}
            onDiscardDraft={onDiscardDraft}
          />
        </section>
      </div>
    </section>
  );
}
