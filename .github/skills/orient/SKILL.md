---
name: orient
description: Present a start-of-session orientation - where the project stands, what changed since the reviewer last looked, what needs their attention, and what is next. Use at the start of every session (the session-start hook supplies the data) or when the reviewer asks "where are we?".
---

# Orient

Give the reviewer a short, honest picture of the project before any work starts. The
process this serves is in `docs/process.md` (*Presentations*).

## Get the data

The session-start hook runs `scripts/session_context.sh` and puts its output in your
context. If it is not there (another agent, or the hook did not run), run it yourself
from the repo root:

```bash
bash .github/skills/orient/scripts/session_context.sh
```

## Before presenting: catch up the record

If commits exist that the latest journal entry does not mention, the last session ended
before its milestone was recorded. Bring the journal and plan up to date from git
history first (see the `journal` skill), and say that you did.

## Present

Lead with what needs the reviewer, not with a recap. Keep it under about fifteen lines.

1. **Needs you:** PRs waiting for review (with their proposed approval track), scope
   issues waiting for agreement, open questions from the journal.
2. **Where we are:** the current goal from the plan and the state in one or two lines.
3. **Since last time:** what changed (commits, merged PRs), in plain words.
4. **Understanding debt:** open `understanding-debt` issues and stale or `needs-review`
   wiki pages, if any.
5. **Next:** the next step from the plan, and what you propose to do now.

Then wait. Do not start work until the reviewer responds, unless a scope already agreed
covers the next step and they have said to continue.
