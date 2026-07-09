export function TemplatesPage({ forms }) {
  return (
    <section className="view active" aria-label="Templates">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Template Library</h2>
            <p>Starter definitions are stored in backend/data/form-templates.json.</p>
          </div>
        </div>
        <div className="template-grid">
          {forms.map((form) => {
            const fieldCount = form.sections.reduce((count, section) => count + (section.fields || []).length, 0);
            const contentCount = form.sections.reduce((count, section) => count + (section.content || []).length, 0);
            return (
              <article className="template-card" key={form.id}>
                <strong>{form.name}</strong>
                <span>{form.description}</span>
                <div className="template-meta">
                  <span>{form.category}</span>
                  <span>{fieldCount} fields - {contentCount} notes</span>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
