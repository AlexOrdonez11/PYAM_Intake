# PYAM Intake

Patient intake prototype with a static frontend, FastAPI backend, MongoDB-ready persistence, and staff login.

## Structure

```text
frontend/
  public/              Static UI deployed to Vercel
  scripts/             Build-time config writer
  vercel.json          Vercel settings

backend/
  data/                Versioned form templates and local fallback JSON
  main.py              FastAPI API, auth, submissions, static fallback

Dockerfile             Cloud Run container from the repo root
```

## Local Development

```powershell
npm run dev
```

Then open:

```text
http://localhost:5177
```

Without `MONGO_URI`, the backend uses local JSON files in `backend/data/` so the prototype still runs. With `MONGO_URI`, staff users and submissions are saved in MongoDB. `MONGODB_URI` also works as a local fallback alias.

## Environment

Copy `.env.example` into your deployment environment and set:

- `MONGO_URI`: MongoDB Atlas connection string
- `MONGODB_DB`: database name, defaults to `pyam_intake`
- `JWT_SECRET`: long random secret for staff login tokens
- `CORS_ORIGINS`: comma-separated frontend URLs allowed to call the API
- `CORS_ORIGIN_REGEX`: optional regex for allowed browser origins, useful for Vercel preview URLs
- `PYAM_API_BASE_URL`: Vercel frontend build variable pointing to the Cloud Run URL

## Staff Login

Use **Staff login**. If no users exist yet, the app shows **Create First Admin**. After the first admin exists, public registration closes and admins create additional staff/admin users from the **Staff** screen. Passwords are hashed before storage. This is good enough for the prototype, but production should add account invites, password reset, audit controls, and stronger role management.

Roles:

- `admin`: can review intakes, view templates, and create staff/admin users
- `staff`: can review intakes and view templates

## MongoDB Collections

Initialize or update the MongoDB structure from your local `.env`:

```powershell
.\.venv\Scripts\python.exe backend\scripts\init_db.py
```

The app uses these collections:

- `users`: staff login credentials, roles, active status, and password hashes
- `staff_profiles`: staff display/profile data and permissions
- `form_templates`: versioned intake form definitions seeded from `backend/data/form-templates.json`
- `intake_forms`: submitted patient intake records and answers
- `patients`: reusable patient contact/demographic records for the next phase
- `audit_events`: cross-collection audit trail for future staff actions

## Deployment Plan

1. Create MongoDB Atlas database and copy the connection string.
2. Deploy the root `Dockerfile` to GCP Cloud Run with `MONGO_URI`, `MONGODB_DB`, `JWT_SECRET`, `CORS_ORIGINS`, and optionally `CORS_ORIGIN_REGEX`.
3. Deploy `frontend/` to Vercel with `PYAM_API_BASE_URL` set to the Cloud Run service URL.
4. Create the first staff account through the app.
5. Improve one intake form at a time in `backend/data/form-templates.json`, starting with the highest-priority clinic workflow.

## Automatic Vercel Deployments

Use Vercel's native GitHub integration for automatic frontend deployments. This avoids storing a Vercel CLI token in GitHub.

In Vercel:

1. Open the `frontend` project.
2. Go to **Settings -> Git**.
3. Connect the GitHub repository.
4. Set the project root directory to `frontend`.
5. Keep the build settings as:

```text
Install Command: npm ci
Build Command: npm run build
Output Directory: dist
```

After that, pushes to the connected production branch deploy automatically, and pull requests create preview deployments. Keep `PYAM_API_BASE_URL` configured in the Vercel project environment variables.

## Cloud Run

From the repo root:

```powershell
gcloud run deploy pyam-intake-api `
  --source . `
  --region us-central1 `
  --allow-unauthenticated
```

Set runtime environment variables in the provider console or with your secret manager. Do not paste real connection strings or token secrets into committed files. After deploy, copy the backend service URL into the frontend environment as `PYAM_API_BASE_URL`.

For the current Vercel prototype, Cloud Run must allow the Vercel browser origin. At minimum:

```text
CORS_ORIGINS=http://localhost:5177,http://127.0.0.1:5177,http://localhost:5178,http://127.0.0.1:5178,https://frontend-ruddy-eight-66.vercel.app
```

After redeploying the backend with this repo version, you can also allow Vercel preview deployments with:

```text
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

## Current Features

- Patient-facing routing questions
- Dynamic intake form rendering
- Staff-only submission review
- Staff login/register prototype
- MongoDB persistence for users and submissions when configured
- Local JSON fallback for fast local work
