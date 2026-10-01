---
name: orient
description: Present a start-of-session orientation - where the project stands, what changed since the reviewer last looked, what needs their attention, and what is next. Use at the start of every session (the session-start hook supplies the data) or when the reviewer asks "where are we?".
---

# Orient

Rules: `docs/process.md`, *Presentations*.

1. **Get the data.** The session-start hook has already put the output of
   `.github/skills/scripts/session_context.sh` in your context. If it is not there, run
   that script from the repo root.
2. **Catch up the record.** If the data shows commits the journal does not mention, or
   wiki changes that are not pushed, fix that first (`journal` and `understood` skills)
   and say that you did.
3. **Present,** in under about fifteen lines, leading with what needs the reviewer:
   - **Needs you:** PRs waiting for review (with their proposed approval track), scope
     issues waiting for agreement, open questions from the journal, wiki pages waiting
     to be read.
   - **Where we are:** the current goal and state, in one or two lines.
   - **Since last time:** what changed, in plain words.
   - **Understanding debt:** `understanding-debt` issues; `stale` or `needs-review` pages.
   - **Next:** the next step in the plan, and what you propose to do now.
4. **Wait.** Do not start work until the reviewer responds, unless an agreed scope
   covers the next step and they have said to continue.
