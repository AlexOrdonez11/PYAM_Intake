import { useEffect, useMemo, useState } from "react";
import { FormRenderer } from "../features/forms/FormRenderer";

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

function hasScoringSensitiveFields(template) {
  const markers = ["asq", "epds", "phq", "gad7", "psc17", "vanderbilt", "scared", "asrs", "ppsc", "mchat", "act", "cact", "crafft", "ace"];
  return (template.sections || []).some((section) =>
    (section.fields || []).some((field) => markers.some((marker) => String(field.id || "").toLowerCase().includes(marker)))
  );
}

function fieldMapForTemplate(template) {
  const fields = new Map();
  for (const section of template?.sections || []) {
    for (const field of section.fields || []) {
      fields.set(field.id, { ...field, section: section.title || "" });
    }
  }
  return fields;
}

function changedOptions(before = [], after = []) {
  return JSON.stringify(before || []) !== JSON.stringify(after || []);
}

function templateChangeSummary(original, draft) {
  const originalFields = fieldMapForTemplate(original);
  const draftFields = fieldMapForTemplate(draft);
  const added = [];
  const removed = [];
  const changed = [];
  let scoringSensitive = false;

  for (const [fieldId, field] of draftFields.entries()) {
    const previous = originalFields.get(fieldId);
    if (!previous) {
      added.push(field);
      continue;
    }
    const changes = [];
    if (previous.label !== field.label) changes.push("label");
    if (previous.type !== field.type) changes.push("type");
    if (Boolean(previous.required) !== Boolean(field.required)) changes.push("required");
    if ((previous.owner || "patient") !== (field.owner || "patient") || Boolean(previous.staffOnly) !== Boolean(field.staffOnly)) changes.push("owner");
    if (changedOptions(previous.options, field.options)) changes.push("options");
    if (changes.length) {
      changed.push({ field, changes });
      if (changes.some((change) => ["type", "options"].includes(change)) && hasScoringSensitiveFields({ sections: [{ fields: [field] }] })) {
        scoringSensitive = true;
      }
    }
  }

  for (const [fieldId, field] of originalFields.entries()) {
    if (!draftFields.has(fieldId)) {
      removed.push(field);
      if (hasScoringSensitiveFields({ sections: [{ fields: [field] }] })) scoringSensitive = true;
    }
  }

  const sectionCountChanged = (original?.sections || []).length !== (draft?.sections || []).length;
  return {
    added,
    removed,
    changed,
    sectionCountChanged,
    scoringSensitive,
    total: added.length + removed.length + changed.length + (sectionCountChanged ? 1 : 0)
  };
}

function updateArrayItem(items, index, updater) {
  return items.map((item, itemIndex) => (itemIndex === index ? updater(item) : item));
}

function moveArrayItem(items, fromIndex, toIndex) {
  if (toIndex < 0 || toIndex >= items.length) return items;
  const next = [...items];
  const [item] = next.splice(fromIndex, 1);
  next.splice(toIndex, 0, item);
  return next;
}

function templateIssues(template) {
  const issues = [];
  if (!template.id) issues.push({ severity: "error", text: "Template id is required." });
  if (!template.name) issues.push({ severity: "error", text: "Template name is required." });
  if (!template.category) issues.push({ severity: "error", text: "Category is required." });
  if (!(template.sections || []).length) issues.push({ severity: "error", text: "At least one section is required." });

  const fieldIds = [];
  (template.sections || []).forEach((section, sectionIndex) => {
    if (!section.title) issues.push({ severity: "error", text: `Section ${sectionIndex + 1} needs a title.` });
    (section.fields || []).forEach((field, fieldIndex) => {
      if (!field.id) issues.push({ severity: "error", text: `Field ${fieldIndex + 1} in ${section.title || `section ${sectionIndex + 1}`} needs an id.` });
      if (!field.label) issues.push({ severity: "error", text: `Field ${field.id || fieldIndex + 1} needs a label.` });
      if (!FIELD_TYPES.includes(field.type)) issues.push({ severity: "error", text: `${field.id || field.label} uses unsupported type ${field.type}.` });
      if (["radio", "select", "multicheck", "scale"].includes(field.type) && !(field.options || []).length) {
        issues.push({ severity: "warning", text: `${field.label || field.id} has no options yet.` });
      }
      if (field.id) fieldIds.push(field.id);
    });
  });

  const duplicates = [...new Set(fieldIds.filter((id, index) => fieldIds.indexOf(id) !== index))];
  duplicates.forEach((id) => issues.push({ severity: "error", text: `Duplicate field id: ${id}.` }));
  if (hasScoringSensitiveFields(template)) {
    issues.push({ severity: "warning", text: "Scoring-sensitive fields are present. Avoid changing field IDs or option text unless you also update scoring rules." });
  }
  return issues;
}

function initialPreviewAnswers(form) {
  const answers = {};
  for (const section of form.sections || []) {
    for (const field of section.fields || []) {
      answers[field.id] = field.type === "multicheck" ? [] : field.type === "checkbox" ? false : "";
    }
  }
  return answers;
}

function AdminOnlyNotice() {
  return (
    <div className="empty-state">
      <h2>Template editor is admin only</h2>
      <p>Staff can view template structure here. Admin users can edit fields and questions.</p>
    </div>
  );
}

function DraftManager({ drafts, selectedDraftId, onOpenDraft, onDeleteDraft }) {
  return (
    <section className="template-draft-manager">
      <div>
        <p className="eyebrow">Draft manager</p>
        <h3>{drafts.length} saved draft{drafts.length === 1 ? "" : "s"}</h3>
      </div>
      {drafts.length ? (
        <div className="template-draft-list">
          {drafts.map((draft) => (
            <article className={`template-draft-card ${selectedDraftId === draft.id ? "active" : ""}`} key={draft.id}>
              <div>
                <strong>{draft.name}</strong>
                <span>{draft.category} - v{draft.version || 1}</span>
                <small>{draft.updatedAt ? `Saved ${new Date(draft.updatedAt).toLocaleString()}` : `${fieldCount(draft)} fields`}</small>
              </div>
              <div className="template-draft-actions">
                <button className="secondary-button" type="button" onClick={() => onOpenDraft(draft)}>Open</button>
                <button className="ghost-button" type="button" onClick={() => onDeleteDraft(draft)}>Discard</button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="template-draft-empty">Saved template drafts will appear here before they are published.</p>
      )}
    </section>
  );
}

function TemplateVersionHistory({ versions, activeVersion, onOpenVersion, onRefresh }) {
  return (
    <section className="template-version-history">
      <div className="template-version-header">
        <div>
          <p className="eyebrow">Version history</p>
          <h3>{versions.length ? `${versions.length} saved version${versions.length === 1 ? "" : "s"}` : "No history loaded"}</h3>
        </div>
        <button className="secondary-button" type="button" onClick={onRefresh}>Refresh</button>
      </div>
      {versions.length ? (
        <div className="template-version-list">
          {versions.map((version) => (
            <article className={`template-version-card ${version.status || "archived"}`} key={`${version.status}-${version.version}-${version.updatedAt || version.createdAt}`}>
              <div>
                <strong>v{version.version || 1} - {version.status || "archived"}</strong>
                <span>{fieldCount(version)} fields - {contentCount(version)} notes</span>
                <small>{version.updatedAt ? `Updated ${new Date(version.updatedAt).toLocaleString()}` : "No update timestamp"}</small>
              </div>
              <div className="template-version-actions">
                {activeVersion?.version === version.version && activeVersion?.status === version.status ? <span className="template-version-current">Open</span> : null}
                <button className="secondary-button" type="button" onClick={() => onOpenVersion(version)}>Open as draft</button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="template-draft-empty">Refresh to load active, draft, and archived versions for the selected form.</p>
      )}
    </section>
  );
}

function ChangeSummary({ summary }) {
  if (!summary.total) {
    return (
      <section className="template-change-panel quiet">
        <div>
          <p className="eyebrow">Change summary</p>
          <h3>No unsaved changes</h3>
        </div>
        <p>The draft matches the selected active template.</p>
      </section>
    );
  }

  return (
    <section className={`template-change-panel ${summary.scoringSensitive ? "sensitive" : ""}`}>
      <div>
        <p className="eyebrow">Change summary</p>
        <h3>{summary.total} unsaved change{summary.total === 1 ? "" : "s"}</h3>
      </div>
      <div className="template-change-grid">
        <span><strong>{summary.added.length}</strong> added</span>
        <span><strong>{summary.changed.length}</strong> changed</span>
        <span><strong>{summary.removed.length}</strong> removed</span>
        <span><strong>{summary.sectionCountChanged ? "Yes" : "No"}</strong> section layout</span>
      </div>
      {summary.scoringSensitive ? <p className="template-sensitive-note">Scoring-sensitive fields changed. Save a draft and preview before publishing.</p> : null}
      <ul className="template-change-list">
        {summary.added.slice(0, 3).map((field) => <li key={`added-${field.id}`}>Added: {field.label || field.id}</li>)}
        {summary.changed.slice(0, 3).map(({ field, changes }) => <li key={`changed-${field.id}`}>Changed: {field.label || field.id} ({changes.join(", ")})</li>)}
        {summary.removed.slice(0, 3).map((field) => <li key={`removed-${field.id}`}>Removed: {field.label || field.id}</li>)}
      </ul>
    </section>
  );
}

function TemplateEditor({ original, draft, onChange, onSave, onSaveDraft, onReset, saving, message, error }) {
  const [jsonOpen, setJsonOpen] = useState(false);
  const [jsonDraft, setJsonDraft] = useState("");
  const [activeTab, setActiveTab] = useState("builder");
  const [previewMode, setPreviewMode] = useState("patient");
  const [previewAnswers, setPreviewAnswers] = useState({});
  const [publishConfirmed, setPublishConfirmed] = useState(false);
  const issues = templateIssues(draft);
  const publishErrors = issues.filter((issue) => issue.severity === "error");
  const changeSummary = templateChangeSummary(original, draft);
  const publishBlockedByConfirmation = changeSummary.scoringSensitive && !publishConfirmed;

  useEffect(() => {
    setJsonDraft(JSON.stringify(draft, null, 2));
    setPreviewAnswers(initialPreviewAnswers(draft));
    setPublishConfirmed(false);
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

  function duplicateField(sectionIndex, fieldIndex) {
    patchSection(sectionIndex, (section) => {
      const fields = section.fields || [];
      const source = cloneTemplate(fields[fieldIndex]);
      const copy = {
        ...source,
        id: `${source.id || "field"}_copy_${Date.now()}`,
        label: `${source.label || "Question"} copy`
      };
      section.fields = [...fields.slice(0, fieldIndex + 1), copy, ...fields.slice(fieldIndex + 1)];
      return section;
    });
  }

  function moveSection(sectionIndex, direction) {
    patchTemplate((next) => {
      next.sections = moveArrayItem(next.sections || [], sectionIndex, sectionIndex + direction);
      return next;
    });
  }

  function moveField(sectionIndex, fieldIndex, direction) {
    patchSection(sectionIndex, (section) => {
      section.fields = moveArrayItem(section.fields || [], fieldIndex, fieldIndex + direction);
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
          <p>Version {draft.version || 1} - {fieldCount(draft)} fields - {contentCount(draft)} notes</p>
        </div>
        <div className="detail-actions">
          <button className="secondary-button" type="button" onClick={() => setJsonOpen((open) => !open)}>Advanced JSON</button>
          <button className="secondary-button" type="button" onClick={onReset}>Reset</button>
          <button className="secondary-button" type="button" onClick={onSaveDraft} disabled={saving || publishErrors.length > 0}>{saving ? "Saving" : "Save draft"}</button>
          <button className="primary-button" type="button" onClick={onSave} disabled={saving || publishErrors.length > 0 || publishBlockedByConfirmation}>{saving ? "Publishing" : "Publish new version"}</button>
        </div>
      </div>

      {message ? <div className={`message ${error ? "error" : ""}`} role="status">{message}</div> : null}
      <ChangeSummary summary={changeSummary} />
      {changeSummary.scoringSensitive ? (
        <label className="template-publish-confirm">
          <input type="checkbox" checked={publishConfirmed} onChange={(event) => setPublishConfirmed(event.target.checked)} />
          <span>I reviewed scoring-sensitive changes and verified the preview.</span>
        </label>
      ) : null}
      <div className="template-editor-tabs" role="tablist" aria-label="Template editor views">
        {[
          ["builder", "Builder"],
          ["preview", "Preview"],
          ["readiness", `Readiness ${publishErrors.length ? `(${publishErrors.length})` : ""}`]
        ].map(([tab, label]) => (
          <button className={activeTab === tab ? "active" : ""} key={tab} type="button" onClick={() => setActiveTab(tab)}>{label}</button>
        ))}
      </div>

      {issues.length ? (
        <div className="template-issue-list" role="note">
          {issues.slice(0, activeTab === "readiness" ? issues.length : 3).map((issue, index) => (
            <span className={issue.severity} key={`${issue.text}-${index}`}>{issue.text}</span>
          ))}
        </div>
      ) : (
        <div className="template-ready-banner" role="note">Template looks ready to publish.</div>
      )}

      {activeTab === "preview" ? (
        <section className="template-preview-panel">
          <div className="template-preview-toolbar">
            <div>
              <p className="eyebrow">Live preview</p>
              <h3>{previewMode === "staff" ? "Staff view" : "Patient view"}</h3>
            </div>
            <div className="segmented-control">
              {["patient", "staff"].map((mode) => (
                <button className={previewMode === mode ? "active" : ""} type="button" key={mode} onClick={() => setPreviewMode(mode)}>{mode}</button>
              ))}
            </div>
          </div>
          <FormRenderer
            form={draft}
            answers={previewAnswers}
            mode={previewMode}
            onAnswerChange={(fieldId, value) => setPreviewAnswers((current) => ({ ...current, [fieldId]: value }))}
            onSubmit={(event) => event.preventDefault()}
            onClear={() => setPreviewAnswers(initialPreviewAnswers(draft))}
            message=""
            error={false}
          />
        </section>
      ) : null}

      {activeTab === "readiness" ? (
        <section className="template-readiness-panel">
          <h3>Publish readiness</h3>
          <p>{publishErrors.length ? "Resolve the blocking items before publishing." : "No blocking issues found. Warnings are reminders for careful clinical review."}</p>
          <div className="template-readiness-grid">
            <span><strong>{(draft.sections || []).length}</strong> sections</span>
            <span><strong>{fieldCount(draft)}</strong> fields</span>
            <span><strong>{contentCount(draft)}</strong> notes</span>
            <span><strong>{publishErrors.length}</strong> blocking issues</span>
          </div>
        </section>
      ) : null}

      {activeTab === "builder" ? (
      <>
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
                <button className="secondary-button icon-button-text" type="button" onClick={() => moveSection(sectionIndex, -1)} disabled={sectionIndex === 0}>Move up</button>
                <button className="secondary-button icon-button-text" type="button" onClick={() => moveSection(sectionIndex, 1)} disabled={sectionIndex === (draft.sections || []).length - 1}>Move down</button>
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
                    <button className="secondary-button icon-button-text" type="button" onClick={() => moveField(sectionIndex, fieldIndex, -1)} disabled={fieldIndex === 0}>Move up</button>
                    <button className="secondary-button icon-button-text" type="button" onClick={() => moveField(sectionIndex, fieldIndex, 1)} disabled={fieldIndex === (section.fields || []).length - 1}>Move down</button>
                    <button className="secondary-button icon-button-text" type="button" onClick={() => duplicateField(sectionIndex, fieldIndex)}>Duplicate</button>
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
      </>
      ) : null}
    </article>
  );
}

export function TemplatesPage({ forms, templateDrafts = [], templateVersions = {}, user, onSaveTemplate, onLoadDrafts, onLoadVersions, onDeleteDraft }) {
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

  useEffect(() => {
    if (isAdmin) onLoadDrafts?.();
  }, [isAdmin, onLoadDrafts]);

  useEffect(() => {
    if (isAdmin && selectedForm?.id) onLoadVersions?.(selectedForm.id);
  }, [isAdmin, onLoadVersions, selectedForm?.id]);

  function openDraft(templateDraft) {
    setSelectedFormId(templateDraft.id);
    setDraft(cloneTemplate(templateDraft));
    setMessage(`Opened saved draft for ${templateDraft.name}.`);
    setError(false);
  }

  function openPublishedForm(form) {
    setSelectedFormId(form.id);
    setDraft(cloneTemplate(form));
    setMessage("");
    setError(false);
  }

  function openVersion(version) {
    setSelectedFormId(version.id);
    setDraft(cloneTemplate({ ...version, status: "draft" }));
    setMessage(`Opened version ${version.version || 1} as an editable draft. Save draft or publish to keep changes.`);
    setError(false);
  }

  async function discardDraft(templateDraft) {
    const confirmed = window.confirm(`Discard the saved draft for ${templateDraft.name}? The active published form will stay unchanged.`);
    if (!confirmed) return;
    setSaving(true);
    setMessage("");
    setError(false);
    try {
      await onDeleteDraft(templateDraft.id);
      if (selectedForm?.id === templateDraft.id) setDraft(cloneTemplate(selectedForm));
      setMessage(`Draft discarded for ${templateDraft.name}.`);
    } catch (deleteError) {
      setError(true);
      setMessage(deleteError.message || "Unable to discard draft.");
    } finally {
      setSaving(false);
    }
  }

  async function saveTemplate() {
    if (!selectedForm || !isAdmin) return;
    setSaving(true);
    setMessage("");
    setError(false);
    try {
      const payload = await onSaveTemplate(draft);
      setDraft(cloneTemplate(payload.form));
      setMessage([
        `Version ${payload.form.version} published. New patient submissions will use the updated questions.`,
        ...(payload.warnings || [])
      ].join(" "));
    } catch (saveError) {
      setError(true);
      setMessage(saveError.message || "Unable to save template.");
    } finally {
      setSaving(false);
    }
  }

  async function saveDraft() {
    if (!selectedForm || !isAdmin) return;
    setSaving(true);
    setMessage("");
    setError(false);
    try {
      const payload = await onSaveTemplate(draft, { publish: false });
      setDraft(cloneTemplate(payload.form));
      setMessage([
        `Draft saved for ${payload.form.name}. Patient-facing forms are unchanged until you publish.`,
        ...(payload.warnings || [])
      ].join(" "));
    } catch (saveError) {
      setError(true);
      setMessage(saveError.message || "Unable to save draft.");
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
            {isAdmin ? (
              <>
                <DraftManager
                  drafts={templateDrafts}
                  selectedDraftId={draft?.status === "draft" ? draft.id : ""}
                  onOpenDraft={openDraft}
                  onDeleteDraft={discardDraft}
                />
                {selectedForm ? (
                  <TemplateVersionHistory
                    versions={templateVersions[selectedForm.id] || []}
                    activeVersion={draft}
                    onOpenVersion={openVersion}
                    onRefresh={() => onLoadVersions?.(selectedForm.id)}
                  />
                ) : null}
              </>
            ) : null}
            {forms.map((form) => (
              <button className={`template-card compact ${form.id === selectedForm?.id && draft?.status !== "draft" ? "active" : ""}`} key={form.id} onClick={() => openPublishedForm(form)} type="button">
                <strong>{form.name}</strong>
                <span>{form.category}</span>
                <small>{fieldCount(form)} fields - {contentCount(form)} notes{templateDrafts.some((item) => item.id === form.id) ? " - draft saved" : ""}</small>
              </button>
            ))}
          </aside>
          <div>
            {!isAdmin ? <AdminOnlyNotice /> : selectedForm ? (
              <TemplateEditor
                original={selectedForm}
                draft={draft}
                onChange={setDraft}
                onSave={saveTemplate}
                onSaveDraft={saveDraft}
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
