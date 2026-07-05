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

Without `MONGODB_URI`, the backend uses local JSON files in `backend/data/` so the prototype still runs. With `MONGODB_URI`, staff users and submissions are saved in MongoDB.

## Environment

Copy `.env.example` into your deployment environment and set:

- `MONGODB_URI`: MongoDB Atlas connection string
- `MONGODB_DB`: database name, defaults to `pyam_intake`
- `JWT_SECRET`: long random secret for staff login tokens
- `CORS_ORIGINS`: comma-separated frontend URLs allowed to call the API
- `PYAM_API_BASE_URL`: Vercel frontend build variable pointing to the Cloud Run URL

## Staff Login

Use **Staff view**, then create the first staff account. Passwords are hashed before storage. This is good enough for the prototype, but production should add account invites, password reset, audit controls, and stronger role management.

## Deployment Plan

1. Create MongoDB Atlas database and copy the connection string.
2. Deploy the root `Dockerfile` to GCP Cloud Run with `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET`, and `CORS_ORIGINS`.
3. Deploy `frontend/` to Vercel with `PYAM_API_BASE_URL` set to the Cloud Run service URL.
4. Create the first staff account through the app.
5. Improve one intake form at a time in `backend/data/form-templates.json`, starting with the highest-priority clinic workflow.

## Cloud Run

From the repo root:

```powershell
gcloud run deploy pyam-intake-api `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars MONGODB_URI="YOUR_MONGODB_URI",MONGODB_DB="pyam_intake",JWT_SECRET="YOUR_LONG_RANDOM_SECRET",CORS_ORIGINS="https://your-vercel-app.vercel.app"
```

After deploy, copy the Cloud Run service URL into Vercel as `PYAM_API_BASE_URL`.

## Current Features

- Patient-facing routing questions
- Dynamic intake form rendering
- Staff-only submission review
- Staff login/register prototype
- MongoDB persistence for users and submissions when configured
- Local JSON fallback for fast local work
