# Ajaia Docs

A lightweight collaborative document editor: create, format, import, and share documents.

**Live app:** `<LIVE_URL>` (free tier: first load after idle can take ~50s while the server wakes)

| Demo account | Password |
|---|---|
| alice@ajaia.dev | demo1234 |
| bob@ajaia.dev | demo1234 |
| carol@ajaia.dev | demo1234 |

The login page has one-click buttons for each account. To test sharing, sign in as Alice in a normal window and Bob in a private window.

---

## What it does

| Area | What works |
|---|---|
| **Documents** | Create, rename (click the title), edit, delete; autosave with a visible save status; reopen from the dashboard |
| **Formatting** | Bold, italic, underline, strikethrough, Heading 1–3, bulleted and numbered lists, quotes, undo/redo, keyboard shortcuts |
| **File import** | Upload **.txt, .md, or .docx (max 2 MB)** to create a new editable document. Headings, lists, and bold/italic carry over |
| **Sharing** | Owner shares by email as **Editor** or **Viewer**; can change roles or remove access. Dashboard separates **My documents** from **Shared with me** |
| **Access control** | Viewers get a read-only editor and the API rejects their writes (403). Users without access get 404 |
| **Persistence** | Postgres in production, SQLite locally. Formatting is stored as sanitized HTML |
| **Conflict safety** | Every save carries a version number; a stale save is rejected (409) and the user is asked to reload instead of silently overwriting |
| **Export** (stretch) | Download any document as Markdown |

## Run locally

Requirements: **Python 3.12+**, **Node 20+**.

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

# 2. Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The API docs (Swagger) are at **http://localhost:8000/docs**.

No database setup needed: a local SQLite file is created and the demo users are seeded on first start.

### Production-style run (one server, like the deployment)

```bash
cd frontend && npm install && npm run build
cd ../backend && SECRET_KEY=any-long-random-string ENVIRONMENT=production uvicorn app.main:app --port 8000
```

Then open http://localhost:8000. Or with Docker:

```bash
docker build -t ajaia-docs .
docker run -p 8000:8000 -e SECRET_KEY=any-long-random-string ajaia-docs
```

### Tests

```bash
cd backend && python -m pytest
```

17 tests covering the sharing permission matrix, version conflicts, HTML sanitization, title validation, all three import formats, file validation, and Markdown export. CI runs them plus a frontend type-check/build on every push (`.github/workflows/ci.yml`).

## Deployment

One Docker container on **Render** (free) serves both the API and the built React app, backed by a free **Neon** Postgres database.

1. Create a Neon project and copy its connection string.
2. On Render: **New → Blueprint**, point it at this repo (uses `render.yaml`).
3. Set `DATABASE_URL` to the Neon string. `SECRET_KEY` is generated automatically.

Tables and demo users are created on first boot.

## Project layout

```
backend/
  app/
    core/        config, database, security, domain errors
    models/      SQLAlchemy models: User, Document, DocumentShare
    schemas/     Pydantic request/response contracts
    services/    business logic: access policy, documents, sharing, import, export, sanitizer
    api/         FastAPI routes (thin: validate, call a service, shape the response)
    main.py      app factory, error mapping, static frontend serving
  tests/
frontend/
  src/
    api/         typed API client and endpoint functions
    auth/        session context
    features/    editor (toolbar, autosave), documents (list, import), sharing (dialog)
    components/  layout and UI primitives
    pages/       Login, Dashboard, Editor
docs/screenshots/
```

## Known limitations

See [ARCHITECTURE.md](ARCHITECTURE.md#what-i-deliberately-left-out) for the full list and reasoning. In short: no real-time co-editing, no self-service signup, no images or tables in documents, and no database migrations yet.
