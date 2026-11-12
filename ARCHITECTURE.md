# Architecture Note

## The product slice I chose

The prompt lists five areas. I treated **editing** and **sharing** as the core of the product and went deep on them: a usable editor that never loses work, and an access model that is enforced on the server, not just hidden in the UI. Import, persistence, and deployment are implemented solidly but simply. Everything else was cut on purpose.

## System overview

```
Browser (React + TipTap)
      │  JSON over HTTPS, Bearer token
      ▼
FastAPI  ──  routes (thin)  →  services (policy + logic)  →  SQLAlchemy  →  Postgres / SQLite
      │
      └── serves the built React app (same origin, no CORS in production)
```

One container, one URL. For a reviewer-facing demo this removes a whole class of deployment problems (CORS, two services, two cold starts).

## Key decisions

**1. Store documents as sanitized HTML, not editor JSON.**
TipTap can store either. HTML won because imports (.md, .docx) naturally produce HTML, Markdown export works from HTML, and the server can sanitize it. Every write, whether from the editor or an import, goes through one allow-list sanitizer (`services/sanitizer.py`, using `nh3`). That is the XSS boundary: a shared document is rendered in someone else's browser, so the server cannot trust what the client sends.

**2. One module owns the access policy.**
`services/access.py` resolves a user's level on a document (owner / editor / viewer / none) and every route goes through it. The policy is readable in one screen and tested as a matrix.
- Owner: view, edit, share, delete. Editor: view, edit. Viewer: view.
- No access returns **404, not 403**, so the API never confirms that a private document exists.
- The UI hides controls based on the `permissions` the API returns, but the server is the enforcement point.

**3. Optimistic concurrency instead of real-time sync.**
Real-time co-editing (CRDTs/OT plus websockets) is a multi-day problem. Instead, each document has a `version`. Every save sends the version it was based on; a stale save gets `409 Conflict` and the editor stops autosaving and asks the user to reload. Two people editing at once cannot silently overwrite each other. It is the smallest design that is honest about concurrency.

**4. Autosave that is debounced and serialized.**
`useAutosave` merges edits into one pending patch, saves 800ms after typing stops, and keeps only one request in flight. Edits made during a save are sent right after with the new version, which prevents the client from conflicting with itself. The header shows Saved / Saving / Unsaved / Failed, and the browser warns before closing with unsaved work.

**5. Layered backend, framework-free business logic.**
Routes validate input and shape responses. Services hold the rules and raise domain errors (`NotFoundError`, `ConflictError`, ...), which `main.py` maps to a single error shape: `{"detail": {"code", "message"}}`. The frontend shows `message` directly, so every error a user sees is a sentence a human wrote.

**6. Seeded users with real tokens instead of full auth.**
The prompt allows mocked users. I used three seeded accounts with hashed passwords (PBKDF2) and signed JWTs, so sharing is tested with real identity checks without spending time on signup, email verification, or password reset.

## Validation and error handling

- Titles: trimmed, 1–200 characters. Empty rename reverts in the UI.
- Content: 1 MB cap, sanitized on every write.
- Uploads: extension allow-list, 2 MB limit (checked in the browser for fast feedback, enforced on the server while reading the stream), UTF-8 check for text, ZIP signature check for .docx, empty-file and no-content detection. Each failure has a specific message and status (413, 415, 422).
- Sharing: unknown email (404), sharing with the owner (422), invalid role (422). Re-sharing updates the role instead of duplicating.
- Login: same message for unknown email and wrong password.
- Production refuses to start with the default secret key.

## Testing strategy

Tests target the logic where a bug would hurt most: the permission matrix, lost-update protection, sanitization, and file import validation (17 API-level tests through FastAPI's test client against a real SQLite database). I also ran a scripted browser walkthrough (Playwright) of the full reviewer flow: create, format, reload, share, view as a second user, import. Screenshots in `docs/screenshots/` come from that run.

## What I deliberately left out

| Cut | Why |
|---|---|
| Real-time co-editing and presence | Multi-day problem; versioned saves prevent data loss at a fraction of the cost |
| Comments, suggestions, version history | Valuable, but each needs its own data model and UI; would have thinned out the core |
| Signup, password reset, org/user management | Not needed to demonstrate sharing; seeded users cover it |
| Images, tables, links toolbar | Expands the sanitizer and import surface; text formatting covers the brief |
| Database migrations (Alembic) | Schema is created on boot. Fine for a fixed schema; first thing to add before any schema change |
| Pagination and search on the dashboard | Not needed at demo scale |

## What I would build next (2–4 hours)

1. **Alembic migrations** so the schema can evolve safely.
2. **Version history**: snapshot on save, list and restore. The `version` column is already there.
3. **Presence indicator**: "Bob is viewing" via a lightweight heartbeat endpoint, a step toward real-time.
4. **Frontend tests** for the autosave hook (conflict and retry paths) with Vitest.
5. **Share link with role**, so documents can be shared with people who aren't users yet.
