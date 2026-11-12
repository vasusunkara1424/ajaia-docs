# AI Workflow Note

> **Draft.** Review and rewrite in your own words before submitting. Every claim below should be something you can explain in the walkthrough video. Delete this box when done.

## Tools used

- **Claude (Anthropic)** in an agentic coding environment with a shell: scaffolding, writing backend and frontend code, running tests, driving a headless browser for UI checks, drafting documentation.
- <!-- Add anything else you used: Cursor, Copilot, ChatGPT, etc. -->

## Where AI materially sped things up

- **Boilerplate across the stack.** Models, schemas, typed API client, CSS design tokens, Dockerfile, CI workflow. This is most of the line count and the least interesting part to write by hand.
- **Test scaffolding.** The permission-matrix tests and the in-memory `.docx` fixture (building a valid Word file from raw XML so tests need no binary files).
- **Verification loops.** Running the API with curl, then a Playwright script through the whole reviewer flow, then reading the screenshots, all in one loop instead of manual clicking.

## What I changed or rejected

<!-- Replace with your own judgment calls. These are real issues found during this build: -->

- **Timezone bug in generated code.** SQLite returns timestamps without a timezone, so the UI would have shown a just-edited document as "5 hours ago". Caught during the API smoke test; fixed with a UTC-normalizing type on all API timestamps (`schemas/types.py`).
- **Visual check caught a design bug.** Screenshots showed every avatar in the same color: the color hash collided for the seeded names. Replaced it with a proper string hash.
- **Weak test secret.** The first test run raised JWT warnings for a short signing key. Lengthened it, and added a startup guard so production refuses to run with the default secret.
- **Scope pushback.** Real-time collaboration was the obvious "impressive" feature. Rejected in favor of versioned saves with conflict detection: solves the actual data-loss risk in a fraction of the time.
- **Storage format.** Chose sanitized HTML over TipTap JSON so imports, export, and server-side XSS sanitization all work from one format (see ARCHITECTURE.md).
- **403 vs 404.** Changed "no access" responses to 404 so the API doesn't reveal that a private document exists.
- <!-- Add: anything you rewrote after reading the code, anything you disagreed with -->

## How I verified correctness, UX, and reliability

- **Automated tests:** 17 backend tests (pytest) on the riskiest logic: who can view/edit/share/delete, stale-version rejection, XSS stripping, import validation for each format and failure mode.
- **Type safety:** strict TypeScript; the build fails on type errors. CI runs tests and the frontend build on every push.
- **End-to-end in a real browser:** a Playwright script logs in as Alice, creates a doc, applies each format, reloads to confirm persistence, shares with Bob as a viewer, logs in as Bob in a separate session, confirms the doc appears under "Shared with me" and is read-only, then imports a Markdown file and checks a bad file type is rejected.
- **Visual review:** read every screenshot rather than trusting a passing script. That is how the avatar issue was caught.
- **Manual review:** <!-- describe what you read line by line, e.g. access.py, sanitizer.py, useAutosave.ts -->
