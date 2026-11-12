# AI Workflow Note

## Tools I used

I built this with Claude, running in an agent setup where it could use a shell and a browser. I used it to help plan the scope, write most of the code, write and run the tests, and draft the docs. I ran and reviewed everything locally in VS Code and Terminal.

## Where AI actually saved me time

The biggest win was the boilerplate. Models, schemas, the API client, routes, CSS, the Dockerfile, the Render config and CI are a lot of code but not a lot of decisions. Having AI write that let me spend my time on the parts that matter: scope, permissions, and making sure nothing loses data.

It also sped up testing a lot. Instead of clicking through every flow by hand, I had it run the API with curl and then a scripted browser walkthrough of the whole reviewer flow, and I reviewed the screenshots. When the first deploy failed, it read the Render log with me and pointed straight at the cause.

## What I changed, pushed back on, or decided myself

The first decision was scope. It's tempting to chase real-time co-editing because it looks impressive, but that's days of work. I cut it, along with comments and version history, and focused on doing editing, import, sharing and persistence properly.

To still handle two people editing the same doc, I went with a simpler approach: every save carries a version number, and if someone saves an outdated version, they get a conflict and are asked to reload. Nobody silently overwrites anyone else.

I chose to store documents as cleaned-up HTML instead of the editor's JSON. That way imports, Markdown export, and protection against malicious content all work off one format.

I also made a small security call: if you don't have access to a document, the API says "not found" instead of "forbidden", so it doesn't even confirm the document exists.

A few things the AI got wrong that I caught and fixed:

- Timestamps were saved without a timezone, so a document I had just edited showed as "5 hours ago". We fixed it by treating every timestamp as UTC.
- Looking at the screenshots, every user's avatar was the same color. The color logic was too simple, so I replaced it.
- The tests warned that the signing key was too short. I made it longer, and I added a check so the app won't start in production with the default key.

On the deployment side, the first Render deploy built fine but crashed on startup because the database URL had been pasted with extra characters. I fixed the environment variable and it went live.

## How I checked that it works

I didn't want to trust "it compiles" or "the AI says it's done", so I checked it a few ways:

- **17 automated tests** for the riskiest logic: who can view, edit, share and delete; rejecting outdated saves; stripping harmful HTML; and importing .txt, .md and .docx, including bad, empty and oversized files.
- **Strict TypeScript and CI**, so a type error or failing test blocks the build on every push.
- **A full browser run-through**: log in as Alice, create and format a document, refresh to make sure the formatting stays, share it with Bob as a viewer, then log in as Bob and confirm he sees it under "Shared with me" and can't edit it.
- **Looking at the screenshots myself** instead of just trusting a green test. That's how I spotted the avatar bug.
- **Testing the live site**: login, creating and editing, data saved in Postgres, sharing, and making sure strangers and viewers are blocked.
- **Reading the important code myself**: the permissions module (`access.py`), the HTML sanitizer, and the autosave logic (`useAutosave.ts`), because those are where a bug would actually hurt.
