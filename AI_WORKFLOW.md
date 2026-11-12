# AI Workflow Note

## Tools used

- **Claude (Anthropic)**, in an agentic setup with shell and browser access. I used it to plan scope, generate the backend and frontend code, write tests, run them, drive a headless browser for end-to-end checks, and draft the documentation.
- **VS Code and Terminal** to run, read and review the code locally.

## Where AI materially sped up my work

- **Scaffolding the full stack.** Models, schemas, typed API client, routes, styling, Dockerfile, Render blueprint and CI. This is most of the line count and the least decision-heavy part of the project.
- **Tests.** The permission-matrix tests and an in-memory `.docx` fixture (a valid Word file built from raw XML, so the tests need no binary files).
- **Verification loops.** Running the API with curl, then a scripted Playwright walkthrough of the whole reviewer flow, then reviewing the screenshots, without clicking through every case manually.
- **Deployment debugging.** Reading the Render build log to pinpoint why the first deploy failed.

## What I changed, rejected, or decided myself

- **Scope.** I kept the product to one slice: editing, import, sharing and persistence done well. I rejected real-time co-editing, comments and version history for this timebox.
- **Concurrency instead of real-time sync.** Rather than build live collaboration, every save carries a version number and stale saves are rejected with a conflict. This protects against lost updates at a fraction of the cost.
- **Storage format.** Documents are stored as sanitized HTML, not editor JSON, so imports, Markdown export and server-side XSS protection all work from one format.
- **404 instead of 403 for no access.** A user with no access to a document gets "not found", so the API doesn't confirm that a private document exists.
- **Bugs caught during review and fixed:**
  - Timestamps came back from SQLite without a timezone, so a just-edited document showed as "5 hours ago". Fixed by normalizing all API timestamps to UTC.
  - Screenshots showed every user's avatar in the same color because of a weak hash. Replaced it with a proper string hash.
  - The first test run flagged a short JWT signing key. I lengthened it and added a startup check so production refuses to run with the default secret.
- **Deployment issue.** The first Render deploy built successfully but crashed on startup: the database connection string had been pasted with extra characters. I fixed the environment variable and redeployed.

## How I verified correctness, UX, and reliability

- **Automated tests:** 17 backend tests (pytest) covering who can view, edit, share and delete; stale-version rejection; HTML sanitization; title validation; import of .txt, .md and .docx; and rejection of unsupported, empty, corrupt and oversized files.
- **Type safety and CI:** strict TypeScript (the build fails on type errors), plus a GitHub Actions workflow running the tests and the frontend build on every push.
- **End-to-end browser test:** logged in as Alice, created and formatted a document, reloaded to confirm formatting persisted, shared it with Bob as a viewer, then logged in as Bob to confirm it appears under "Shared with me" and is read-only. Also imported a Markdown file and confirmed an unsupported file is rejected.
- **Visual review:** I looked at the screenshots instead of trusting a passing script. That's how the avatar issue was caught.
- **Live deployment check:** on the production URL, verified login, create, edit, persistence in Postgres, sharing, and that the API returns 404 for a stranger and 403 when a viewer tries to edit.
- **Manual review:** I read the access-control module (`access.py`), the sanitizer, and the autosave hook (`useAutosave.ts`) myself, since those carry the riskiest logic.
