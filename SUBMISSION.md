# Submission: Ajaia Docs

**Candidate:** Venkata Srinivas Sunkara
**Live app:** `<LIVE_URL>`
**Walkthrough video:** see `VIDEO_URL.txt`

## Test accounts

| Email | Password |
|---|---|
| alice@ajaia.dev | demo1234 |
| bob@ajaia.dev | demo1234 |
| carol@ajaia.dev | demo1234 |

**Quick sharing test:** sign in as Alice → New document → type and format → Share → `bob@ajaia.dev` as Viewer. Open a private window, sign in as Bob → "Shared with me" → document opens read-only.

## What's included

| Item | Location |
|---|---|
| Source code | `backend/`, `frontend/` |
| Setup and run instructions | `README.md` |
| Architecture note | `ARCHITECTURE.md` |
| AI workflow note | `AI_WORKFLOW.md` |
| This file | `SUBMISSION.md` |
| Walkthrough video link | `VIDEO_URL.txt` |
| Screenshots | `docs/screenshots/` |
| Automated tests | `backend/tests/` (17 tests) |
| Deployment config | `Dockerfile`, `render.yaml` |
| CI | `.github/workflows/ci.yml` |

## Status

**Working end to end**
- Create, rename, edit, delete, autosave, reopen documents
- Rich text: bold, italic, underline, strikethrough, H1–H3, bulleted/numbered lists, quotes
- Import .txt / .md / .docx into a new editable document
- Sharing with Editor/Viewer roles; change or revoke access; Owned vs Shared views
- Server-enforced permissions; version-based conflict detection
- Persistence across refresh (Postgres in production)
- Export to Markdown (stretch)

**Intentionally not built**
Real-time co-editing, comments, version history, signup/password reset, images and tables. Reasoning in `ARCHITECTURE.md`.

**Next with 2–4 more hours**
Database migrations, version history with restore, a presence indicator, frontend tests for autosave.
