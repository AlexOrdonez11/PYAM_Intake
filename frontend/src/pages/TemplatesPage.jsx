import { useEffect, useMemo, useState } from "react";

const FIELD_TYPES = ["text", "email", "tel", "date", "number", "datetime-local", "textarea", "select", "radio", "multicheck", "checkbox", "scale", "signature"];

function cloneTemplate(template) {
  return JSON.parse(JSON.stringify(template || {}));
}

function fieldCount(form) {
  return (form.sections || []).reduce((count, section) => count + (section.fields || []).length, 0);
}

function contentCount(form) {
  return (form.sections || []).reduce((count, section) => count + (section.content || []).length, 0);
}

function toOptionsText(options = []) {
  return options.join("\n");
}

function fromOptionsText(text) {
  return text.split("\n").map((item) => item.trim()).filter(Boolean);
}

function updateArrayItem(items, index, updater) {
  return items.map((item, itemIndex) => (itemIndex === index ? updater(item) : item));
}

function AdminOnlyNotice() {
  return (
    <div className="empty-state">
      <h2>Template editor is admin only</h2>
      <p>Staff can view template structure here. Admin users can edit fields and questions.</p>
    </div>
  );
}

function TemplateEditor({ draft, onChange, onSave, onReset, saving, message, error }) {
  const [jsonOpen, setJsonOpen] = useState(false);
  const [jsonDraft, setJsonDraft] = useState("");

  useEffect(() => {
    setJsonDraft(JSON.stringify(draft, null, 2));
  }, [draft]);

  function patchTemplate(updater) {
    onChange(updater(cloneTemplate(draft)));
  }

  function patchSection(sectionIndex, updater) {
    patchTemplate((next) => {
      next.sections = updateArrayItem(next.sections || [], sectionIndex, updater);
      return next;
    });
  }

  function patchField(sectionIndex, fieldIndex, updater) {
    patchSection(sectionIndex, (section) => {
      section.fields = updateArrayItem(section.fields || [], fieldIndex, updater);
      return section;
    });
  }

  function addSection() {
    patchTemplate((next) => {
      next.sections = [...(next.sections || []), { title: "New section", fields: [], content: [] }];
      return next;
    });
  }

  function addField(sectionIndex) {
    patchSection(sectionIndex, (section) => {
      const nextNumber = (section.fields || []).length + 1;
      section.fields = [
        ...(section.fields || []),
        { id: `new_field_${Date.now()}_${nextNumber}`, label: "New question", type: "text", required: false }
      ];
      return section;
    });
  }

  function addNote(sectionIndex) {
    patchSection(sectionIndex, (section) => {
      section.content = [...(section.content || []), { type: "note", title: "Note", text: "", variant: "disclaimer" }];
      return section;
    });
  }

  function applyJson() {
    try {
      onChange(JSON.parse(jsonDraft));
      setJsonOpen(false);
    } catch {
      window.alert("The JSON is not valid yet.");
    }
  }

  return (
    <article className="template-editor">
      <div className="detail-header">
        <div>
          <p className="eyebrow">Admin template editor</p>
          <h2>{draft.name || "Untitled form"}</h2>
          <p>{fieldCount(draft)} fields - {contentCount(draft)} notes</p>
        </div>
        <div className="detail-actions">
          <button className="secondary-button" type="button" onClick={() => setJsonOpen((open) => !open)}>Advanced JSON</button>
          <button className="secondary-button" type="button" onClick={onReset}>Reset</button>
          <button className="primary-button" type="button" onClick={onSave} disabled={saving}>{saving ? "Saving" : "Save changes"}</button>
        </div>
      </div>

      {message ? <div className={`message ${error ? "error" : ""}`} role="status">{message}</div> : null}

      <div className="template-editor-grid">
        <label className="field">
          <span>Name</span>
          <input className="field-control" value={draft.name || ""} onChange={(event) => patchTemplate((next) => ({ ...next, name: event.target.value }))} />
        </label>
        <label className="field">
          <span>Category</span>
          <input className="field-control" value={draft.category || ""} onChange={(event) => patchTemplate((next) => ({ ...next, category: event.target.value }))} />
        </label>
        <label className="field">
          <span>Estimated minutes</span>
          <input className="field-control" type="number" value={draft.estimatedMinutes || ""} onChange={(event) => patchTemplate((next) => ({ ...next, estimatedMinutes: event.target.value ? Number(event.target.value) : null }))} />
        </label>
        <label className="field">
          <span>Status</span>
          <select className="field-control" value={draft.status || "active"} onChange={(event) => patchTemplate((next) => ({ ...next, status: event.target.value }))}>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
          </select>
        </label>
        <label className="field full">
          <span>Description</span>
          <textarea className="field-control" value={draft.description || ""} onChange={(event) => patchTemplate((next) => ({ ...next, description: event.target.value }))} />
        </label>
      </div>

      {jsonOpen ? (
        <section className="template-json-editor">
          <textarea className="field-control" value={jsonDraft} onChange={(event) => setJsonDraft(event.target.value)} />
          <div className="detail-actions">
            <button className="secondary-button" type="button" onClick={() => setJsonDraft(JSON.stringify(draft, null, 2))}>Revert JSON</button>
            <button className="primary-button" type="button" onClick={applyJson}>Apply JSON to editor</button>
          </div>
        </section>
      ) : null}

      <div className="template-section-list">
        {(draft.sections || []).map((section, sectionIndex) => (
          <section className="template-section-editor" key={`${section.title}-${sectionIndex}`}>
            <div className="template-section-header">
              <input
                className="field-control section-title-input"
                value={section.title || ""}
                onChange={(event) => patchSection(sectionIndex, (nextSection) => ({ ...nextSection, title: event.target.value }))}
              />
              <div className="detail-actions">
                <button className="secondary-button" type="button" onClick={() => addNote(sectionIndex)}>Add note</button>
                <button className="secondary-button" type="button" onClick={() => addField(sectionIndex)}>Add field</button>
                <button className="ghost-button" type="button" onClick={() => patchTemplate((next) => ({ ...next, sections: next.sections.filter((_, index) => index !== sectionIndex) }))}>Remove</button>
              </div>
            </div>

            {(section.content || []).map((note, noteIndex) => (
              <div className="template-note-editor" key={`note-${noteIndex}`}>
                <input className="field-control" placeholder="Note title" value={note.title || ""} onChange={(event) => patchSection(sectionIndex, (nextSection) => ({ ...nextSection, content: updateArrayItem(nextSection.content || [], noteIndex, (nextNote) => ({ ...nextNote, title: event.target.value })) }))} />
                <textarea className="field-control" placeholder="Note text" value={note.text || ""} onChange={(event) => patchSection(sectionIndex, (nextSection) => ({ ...nextSection, content: updateArrayItem(nextSection.content || [], noteIndex, (nextNote) => ({ ...nextNote, text: event.target.value })) }))} />
                <button className="ghost-button" type="button" onClick={() => patchSection(sectionIndex, (nextSection) => ({ ...nextSection, content: (nextSection.content || []).filter((_, index) => index !== noteIndex) }))}>Remove note</button>
              </div>
            ))}

            <div className="template-field-list">
              {(section.fields || []).map((field, fieldIndex) => (
                <article className="template-field-editor" key={field.id || fieldIndex}>
                  <div className="template-field-topline">
                    <label>
                      <span>Question label</span>
                      <input className="field-control" value={field.label || ""} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, label: event.target.value }))} />
                    </label>
                    <label>
                      <span>Field id</span>
                      <input className="field-control" value={field.id || ""} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, id: event.target.value }))} />
                    </label>
                    <label>
                      <span>Type</span>
                      <select className="field-control" value={field.type || "text"} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, type: event.target.value }))}>
                        {FIELD_TYPES.map((type) => <option value={type} key={type}>{type}</option>)}
                      </select>
                    </label>
                  </div>
                  <div className="template-field-flags">
                    <label className="choice-option"><input type="checkbox" checked={Boolean(field.required)} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, required: event.target.checked }))} /><span>Required</span></label>
                    <label className="choice-option"><input type="checkbox" checked={field.owner === "staff" || field.staffOnly === true} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, owner: event.target.checked ? "staff" : "patient", staffOnly: event.target.checked || undefined }))} /><span>Staff-only</span></label>
                    <button className="ghost-button" type="button" onClick={() => patchSection(sectionIndex, (nextSection) => ({ ...nextSection, fields: (nextSection.fields || []).filter((_, index) => index !== fieldIndex) }))}>Remove field</button>
                  </div>
                  {["radio", "select", "multicheck", "scale"].includes(field.type) ? (
                    <label className="field full">
                      <span>Options, one per line</span>
                      <textarea className="field-control" value={toOptionsText(field.options || [])} onChange={(event) => patchField(sectionIndex, fieldIndex, (nextField) => ({ ...nextField, options: fromOptionsText(event.target.value) }))} />
                    </label>
                  ) : null}
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
      <button className="secondary-button" type="button" onClick={addSection}>Add section</button>
    </article>
  );
}

export function TemplatesPage({ forms, user, onSaveTemplate }) {
  const [selectedFormId, setSelectedFormId] = useState(forms[0]?.id || "");
  const selectedForm = useMemo(() => forms.find((form) => form.id === selectedFormId) || forms[0], [forms, selectedFormId]);
  const [draft, setDraft] = useState(() => cloneTemplate(selectedForm));
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    if (!selectedFormId && forms[0]?.id) setSelectedFormId(forms[0].id);
  }, [forms, selectedFormId]);

  useEffect(() => {
    setDraft(cloneTemplate(selectedForm));
    setMessage("");
    setError(false);
  }, [selectedForm]);

  async function saveTemplate() {
    if (!selectedForm || !isAdmin) return;
    setSaving(true);
    setMessage("");
    setError(false);
    try {
      const saved = await onSaveTemplate(draft);
      setDraft(cloneTemplate(saved));
      setMessage("Template saved. New patient submissions will use the updated questions.");
    } catch (saveError) {
      setError(true);
      setMessage(saveError.message || "Unable to save template.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="view active" aria-label="Templates">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>Admin Forms</h2>
            <p>Edit patient questions, staff-only review fields, sections, and template metadata.</p>
          </div>
          <select className="select-input template-picker" value={selectedForm?.id || ""} onChange={(event) => setSelectedFormId(event.target.value)}>
            {forms.map((form) => <option value={form.id} key={form.id}>{form.name}</option>)}
          </select>
        </div>

        <div className="template-admin-layout">
          <aside className="template-admin-list">
            {forms.map((form) => (
              <button className={`template-card compact ${form.id === selectedForm?.id ? "active" : ""}`} key={form.id} onClick={() => setSelectedFormId(form.id)} type="button">
                <strong>{form.name}</strong>
                <span>{form.category}</span>
                <small>{fieldCount(form)} fields - {contentCount(form)} notes</small>
              </button>
            ))}
          </aside>
          <div>
            {!isAdmin ? <AdminOnlyNotice /> : selectedForm ? (
              <TemplateEditor
                draft={draft}
                onChange={setDraft}
                onSave={saveTemplate}
                onReset={() => setDraft(cloneTemplate(selectedForm))}
                saving={saving}
                message={message}
                error={error}
              />
            ) : <div className="empty-state"><h2>No template selected</h2><p>Choose a form to edit.</p></div>}
          </div>
        </div>
      </div>
    </section>
  );
}
