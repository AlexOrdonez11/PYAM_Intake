# PYAM Intake Backlog

Last updated: 2026-07-20

## Status Legend

- Done: implemented and locally verified
- Partial: usable prototype exists, but important gaps remain
- Next: recommended near-term work
- Later: important, but not blocking the prototype

## Product Areas

### Patient Intake

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Split patient/staff app modes | Patient and staff deployments can run from the same frontend with different `PYAM_APP_MODE` values. |
| Done | P0 | Start routing flow | DOB, visit type, clinic location, and extras route patients to recommended forms. |
| Done | P0 | Dynamic form renderer | Renders sections, notes, field types, required fields, signatures, choices, scales, and text fields from templates. |
| Done | P0 | Local autosave drafts | Patient form answers autosave locally per form. |
| Done | P1 | Server resume code drafts | Patients can save a server draft, receive a resume code/link, and reopen `/resume/{code}`. Prototype-level only. |
| Done | P1 | Section progress | Intake forms show overall completion and per-section progress chips. |
| Done | P1 | Review before submit | Bottom review panel checks required fields, sections, signatures, and incomplete ASQ groups before submit. |
| Done | P1 | Repeated demographic cleanup | Common repeated fields like name/DOB are autofilled or removed from patient-facing sections where appropriate. |
| Next | P0 | Submit server draft as final submission | Resume drafts currently save/update drafts. Final submit should convert the draft record instead of creating duplicates. |
| Next | P1 | Resume-code lookup UI | Add a small "Resume intake" entry point on the patient start page, not only direct `/resume/{code}` links. |
| Next | P1 | Multi-form resume bundle | Current resume support is form-level. Intake routing can recommend multiple forms, so resume should eventually cover the whole packet. |
| Later | P2 | Patient-friendly mobile refinements | Long forms need more mobile QA, sticky progress behavior, and keyboard/focus polish. |
| Later | P2 | Multi-language support | Not started. |

### Forms And Templates

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | React-based frontend structure | Frontend split into pages, components, features, API client, layout, and styles. |
| Done | P0 | Admin template editor | Admins can edit sections, questions, options, staff-only fields, notes, metadata, and JSON. |
| Done | P0 | Template snapshots on submissions | Submissions keep the template structure used at submission time. |
| Done | P1 | Draft template saving | Admins can save draft templates separate from active patient-facing templates. |
| Done | P1 | Admin draft manager | Admins can open, publish, or discard saved template drafts. |
| Done | P1 | Template version history | Admins can load active/draft/archived versions and open old versions as editable drafts. |
| Done | P1 | Publish guardrails | Editor warns on scoring-sensitive changes and requires confirmation before publishing. |
| Partial | P0 | Form mapping coverage | Many uploaded PDFs have been mapped, but every form still needs final QA against source PDFs. |
| Next | P0 | Form QA checklist per template | Track source PDF, mapped fields, staff-only fields, scoring rules, required fields, and QA status per form. |
| Next | P1 | Template diff view | Version history shows metadata, but does not yet show field-level diff between versions. |
| Next | P1 | Template rollback publish action | Older versions can be opened as draft, but there is no one-click rollback with audit reason. |
| Later | P2 | Template import workflow | No admin upload/import workflow for PDFs yet. Current mapping is code/data driven. |

### Staff Review

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Staff submissions queue | Staff can view submissions, search/filter/sort, and open dedicated detail pages. |
| Done | P0 | Dedicated submission detail route | `/submissions/{id}` loads a specific submission detail page. |
| Done | P0 | Staff-only response editing | Staff-only fields can be edited in the review panel. Calculated fields are read-only. |
| Done | P1 | Review checklist | Staff sidebar tracks patient answers reviewed, scoring reviewed, staff fields, status, saved review, and PDF export. |
| Done | P1 | Review ownership / soft lock | Review metadata records last reviewer, reviewed time, completed by, and soft lock window. |
| Done | P1 | Activity timeline | Submission detail shows audit history for creation, status changes, staff saves, and PDF export. |
| Done | P1 | Data quality warnings | Staff sidebar flags missing DOB/name/phone, age-form mismatch, incomplete scores, future dates, and missing staff fields. |
| Done | P1 | PDF export | Staff can open a printable/PDF summary from the submission detail page. |
| Next | P0 | Status transition guardrails | Marking `Completed` or `Ready for chart` should warn/block if checklist or data quality has high issues. |
| Next | P1 | Staff notes / internal comments | There is audit history, but no explicit staff note/comment thread yet. |
| Next | P1 | Assignment queue | No owner assignment, team queue, or "assigned to me" filtering yet. |
| Later | P2 | Bulk actions | No bulk status changes, export, or assignment. |

### Scoring And Clinical Logic

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Automatic calculated scores | Backend and frontend calculate ASQ, EPDS, PHQ, GAD, PSC/PPSC, M-CHAT, CRAFFT, ASRS, ACE, ACT/C-ACT, SCARED, Vanderbilt families. |
| Done | P0 | Staff visible scoring UI | Submission detail shows scoring cards, interpretation, thresholds, and ASQ tables. |
| Done | P1 | ASQ dynamic legend | ASQ score ranges show delayed/monitor/on-schedule colors and update with answers. |
| Done | P1 | Read-only calculated staff fields | Staff cannot edit calculated score fields directly. |
| Partial | P0 | Scoring coverage audit | Most scoring systems are implemented, but every PDF/template should be checked for hidden or nonstandard scoring. |
| Next | P0 | Scoring test fixtures | Add tests with known input/expected score outputs for every scoring system. |
| Next | P1 | Scoring provenance display | Staff should see which answers contributed to each score and how totals were derived. |
| Later | P2 | Clinical threshold configuration | Thresholds are coded today. Admin-editable scoring config is not started. |

### Authentication, Users, Roles

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Staff login prototype | Staff/admin login exists with hashed passwords and JWTs. |
| Done | P0 | First admin bootstrap | If no users exist, app supports first admin creation. |
| Done | P1 | Admin staff management | Admins can create staff/admin users. |
| Partial | P1 | Role model | Current roles are `admin` and `staff`; permissions exist but are basic. |
| Next | P0 | Password reset / invite flow | Missing. Required before real use. |
| Next | P0 | Session hardening | Add token rotation/expiry handling, logout invalidation strategy, and secure deployment settings. |
| Next | P1 | Granular permissions | Separate template editing, staff management, review, export, and admin access. |
| Later | P2 | SSO / identity provider | Not started. |

### Backend And Data

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | FastAPI backend | Backend handles auth, forms, submissions, staff, drafts, audit events, scoring, and static fallback. |
| Done | P0 | MongoDB support | App uses MongoDB when `MONGO_URI` is configured, with local JSON fallback for development. |
| Done | P0 | Dockerfile for Cloud Run | Root Dockerfile builds backend container. |
| Done | P1 | Database schema/init scripts | Scripts initialize collections/indexes and seed data. |
| Done | P1 | Audit events collection | Audit events are persisted for submissions and template actions. |
| Partial | P1 | Patients collection | Collection exists/planned, but reusable patient profile workflow is not fully implemented. |
| Next | P0 | Convert draft to final submission | Needed for resume code workflow and clean staff queue history. |
| Next | P1 | Backend data quality summaries | Data quality warnings are frontend-only today. Add summary fields to submission list API. |
| Next | P1 | API tests | Add backend tests for auth, forms, submissions, drafts, scoring, and CORS behavior. |
| Later | P2 | Background jobs | Not started. Useful for reminders, draft cleanup, and scheduled reporting. |

### Deployment And DevOps

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Split Vercel deployment plan | Patient and staff apps can deploy separately from `frontend/`. |
| Done | P0 | Cloud Run backend plan | Backend deploys as container with `MONGO_URI`, `JWT_SECRET`, and CORS settings. |
| Done | P1 | CORS support for production and previews | Supports configured origins and optional Vercel preview regex. |
| Done | P1 | Automatic Vercel deployment guidance | README documents using Vercel Git integration. |
| Partial | P0 | Production deployments | Several new backend routes require redeploy before prod matches local. |
| Next | P0 | Redeploy backend and frontends | Needed after recent resume, version history, draft manager, audit, and filter changes. |
| Next | P0 | Environment audit | Confirm Vercel env vars and Cloud Run env vars match current README. |
| Next | P1 | CI checks | Add GitHub Actions for frontend build, backend compile/tests, readiness checks, and secret scanning. |
| Later | P2 | Observability | Add structured logs, request IDs, error tracking, and health dashboard. |

### Security, Compliance, And Privacy

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | `.gitignore` and secret hygiene pass | GitGuardian warning prompted cleanup. |
| Done | P0 | Hashed staff passwords | Staff credentials are hashed in Mongo. |
| Partial | P0 | Prototype auth only | Auth is not production/compliance ready. |
| Partial | P0 | Audit trail | Audit history exists, but final compliance-grade audit controls are not complete. |
| Next | P0 | Secret rotation | Rotate any secrets that may have been exposed before cleanup. |
| Next | P0 | PHI/PII risk review | Define allowed environments, storage policy, logging rules, retention, and access model before pilot. |
| Next | P0 | Access control hardening | Verify every staff/admin route has correct permissions. |
| Next | P0 | Secure patient resume | Current resume code is prototype-only. Needs stronger design before real patients. |
| Later | P1 | HIPAA/compliance architecture | Final hosting, BAA, encryption, backups, retention, audit exports, and policies are outside current prototype scope. |

### UX And Design

| Status | Priority | Item | Notes |
| --- | --- | --- | --- |
| Done | P0 | Official PYAM logo integration | Logo added across login/start/intake surfaces. |
| Done | P1 | Dark blue modern visual style | App styling moved toward a more polished clinic platform feel. |
| Done | P1 | Better patient form section separation | Larger section headings, underlines, stronger separators. |
| Done | P1 | Better form filter/search | Form and submissions filters are more production-like. |
| Partial | P1 | Mobile responsiveness | Existing responsive CSS exists, but needs route-by-route QA. |
| Next | P1 | Staff dashboard polish | Add clearer queue summaries, owner filters, and data quality counts. |
| Next | P1 | Empty/loading/error states | Improve all network error states and retry actions. |
| Later | P2 | Accessibility review | Keyboard, screen reader, color contrast, focus states, and form errors need a dedicated pass. |

## Immediate Recommended Sprint

1. Redeploy backend and both Vercel frontends so production has the recent API/UI changes.
2. Implement draft-to-final conversion for patient resume drafts.
3. Add resume-code entry on the patient start page.
4. Add status transition guardrails for `Ready for chart` and `Completed`.
5. Add backend tests for scoring and patient draft APIs.
6. Start a form QA tracker for all 50 active templates.

## Known Production Blockers

- Auth is prototype-level and missing password reset/invites.
- Patient resume codes are not secure enough for real patient use.
- Compliance/HIPAA deployment architecture is not finalized.
- Backend needs redeploy after recent API route additions.
- No automated CI test suite yet.
- No formal source-PDF QA tracker for every mapped form.
