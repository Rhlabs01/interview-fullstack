# Setup Instructions

Complete this setup **before** you start the timed exercise. The same steps are
in the setup guide you received; this file is the in-repo copy.

## Architecture

The app is a clinician visit tracker. A Docker image builds the React (Vite)
frontend and serves it from a FastAPI backend. A [Render](https://render.com)
Blueprint (`render.yaml`) provisions:

- a **Free** web service (API + UI)
- a **Free** Postgres database
- `DATABASE_URL` connected automatically

On boot the container runs Alembic migrations, then starts the API. You do not
run migrations by hand. Later pushes to the connected branch auto-deploy.

## Prerequisites

- GitHub account
- Render account (free Hobby plan): [render.com](https://render.com)
- An LLM provider API key (for example OpenAI). A few cents of usage is enough.

You do not need a credit card for Render. You do not need a separate database
provider. Render’s free Postgres expires **30 days** after creation, which is
enough for this interview. Each Render workspace can have **one** free Postgres
at a time.

---

## Step 1: Fork the repository

You will receive access to
[github.com/Rhlabs01/interview-fullstack](https://github.com/Rhlabs01/interview-fullstack).
Create a **private** fork on your personal GitHub account. Work only on that
fork.

---

## Step 2: Deploy to Render

1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Sign up or log in with your **GitHub** account.
3. Click **New** → **Blueprint**.
4. Select your **forked** repository.
5. Confirm Render will create a Free web service and Free Postgres, with
   `DATABASE_URL` already connected.
6. Click **Apply** / **Deploy**.
7. Wait for the first deploy (about 3–5 minutes). The URL looks like
   `https://visit-tracker-xxxx.onrender.com`.

If Blueprint is unavailable: create **Postgres** (Free) and a **Web Service**
(Docker, Free) separately. On the web service, set `DATABASE_URL` to the
database’s **Internal Database URL**, and keep both resources in the **same
region**.

---

## Step 3: Verify the app

1. Open the Render URL. The first request on a sleeping free instance can take
   about one minute.
2. The bottom status bar should show **Database connected** (green).
3. Click **Initialize Database** to seed sample data.
4. Select a clinician, open a patient, then open a visit. Notes render as plain
   text.
5. From the dashboard, **RxNorm Catalog** browses the reference concepts. Click
   **Import full RxNorm** to pull the ~15k-concept ingredient set from RxNav (a
   couple of minutes, in the background).

Invite **yunus@rogerhealthcare.com**, **keyur@rogerhealthcare.com**, and
**shawn@rogerhealthcare.com** to the GitHub fork.

---

## Step 4: LLM environment variables

You will use an LLM during the exercise. Add these on the Render web service
under **Environment** (and in `backend/.env` for local development; see
`backend/.env.example`):

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...
```

You can add the key when you start the timed exercise. Redeploy after you
change environment variables.

---

## Step 5: Submit

The brief you receive when you start lists the full deliverables. Reply to your
interview email with:

- Your deployed Render URL
- A URL to a short video: a quick product demo, your technical decisions, and
  how you used a coding agent
- A design doc on the options you considered and why you shipped the
  implementation you did
- A link to your forked repo

---

## Troubleshooting

**First load is slow or a blank loading page:** Free Render web services sleep
after 15 minutes idle and take about a minute to wake. Wait, then refresh.

**Database connection fails (red status bar):** Wait until Blueprint has
finished creating both the web service and Postgres. Expand the status bar and
click **Retry Connection**. If you created resources by hand, `DATABASE_URL`
must be the **internal** URL from the Render Postgres dashboard, same region as
the web service.

**Blueprint fails (already have a free database):** Render allows one free
Postgres per workspace. Delete or upgrade the existing free database, then
retry.

**Build fails:** Check Render deploy logs. Do not delete the `Dockerfile` or
the `frontend/` / `backend/` folders.

**Initialize Database fails:** Expand the status bar and click Retry Connection.
Confirm the Postgres instance is running in the Render dashboard.

**Refreshing `/dashboard` or a patient URL 404s:** The Docker image may not have
copied the frontend build. Check that `npm run build` succeeded in the Render
logs.

---

Once setup is complete, start the timed exercise when you are ready. Push to
your fork; Render auto-deploys. We will review the work at the same URL.
