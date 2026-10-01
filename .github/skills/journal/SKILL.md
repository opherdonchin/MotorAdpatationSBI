---
name: journal
description: Record a milestone in the project journal and bring the plan up to date. Use whenever a milestone happens - a sub-step is finished and pushed, a PR is opened, marked ready or merged, a significant result or dead end, a decision is made, or context has just been compacted - and when the reviewer asks to log the session.
---

# Journal

The journal is the factual record of the work; the plan is the current state and next
steps. Rules and formats: `docs/process.md`, *Durable state files*.

The agent cannot see a session ending, so both are updated at milestones. An update is
small: extend today's entry, adjust the plan, commit, push.

## Steps

1. **Find what is unrecorded.** Compare the latest entry in `docs/journal/` with
   `git log` since the journal was last touched, the open PRs, and this session's work.
2. **Write the entry.** File `docs/journal/YYYY-MM-DD.md` (today). If it exists, extend
   the current session's section; a new session on the same day gets `## Session N`.
   Use the fields from `docs/process.md`: Goal, Done, Results, Decisions, Permission
   points (independent work only), Open questions / next.
   - Link commits, PRs, issues, notebooks and cell labels.
   - Every number names the notebook cell or command that produced it.
   - Record dead ends and findings worth not rediscovering.
   - Past entries are history: fix errors only, and say so.
3. **Decisions.** A choice that constrains future work and is not obvious from the code
   gets a record in `docs/decisions/` (format in `docs/process.md`), linked from the
   entry. Smaller choices are one line in the entry.
4. **Update the plan.** Rewrite `docs/plan.md` in place so *Current state* and *Next
   steps* are true now. Nothing else belongs there.
5. **Commit and push** the journal and plan on the branch where the work is (or on
   `main` if the work is merged).

## Do not

- Do not write reports, summaries or status files anywhere else.
- Do not pad: an entry that says less but is accurate is better.
