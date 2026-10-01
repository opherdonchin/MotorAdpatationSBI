---
name: journal
description: Record a milestone in the project journal and bring the plan up to date. Use whenever a milestone happens - a sub-step is finished and pushed, a PR is opened, marked ready or merged, a significant result or dead end, a decision is made, or context has just been compacted - and when the reviewer asks to log the session.
---

# Journal

Rules: `docs/process.md`, *Durable state files*. Formats:
`.github/skills/templates/journal-entry.md` and `decision-record.md`.

1. **Find what is unrecorded:** compare the latest entry in `docs/journal/` with
   `git log` since the journal was last touched, the open PRs, and this session's work.
2. **Write it** in `docs/journal/YYYY-MM-DD.md` (today). Extend the current session's
   section if the file exists; a new session the same day gets `## Session N`.
3. **Decisions** that constrain future work get a record in `docs/decisions/`, linked
   from the entry. Smaller ones are a line in the entry.
4. **Update `docs/plan.md`** in place so *Current state* and *Next steps* are true now.
5. **Commit and push** on the branch where the work is (or `main` if it is merged).

Keep entries accurate and short. Nothing goes in report or status files elsewhere.
