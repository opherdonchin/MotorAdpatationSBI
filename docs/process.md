# How we work

This is the working process between a human **reviewer** and an AI **agent** that writes
most of the code. Its aim is that the reviewer stays fully on top of the project: knows
what is being built and why, understands the code that exists, and can tell which parts
they understand less well. Documentation the reviewer can read is a byproduct.

This file is the single source for the process and is deliberately free of project
content. Project-specific rules (layout, coding conventions, the science) live in
[AGENTS.md](../AGENTS.md), which also names the reviewer.

## The life of a piece of work

```
scope issue ─► branch + draft PR ─► work in small commits ─► explanation
     ─► explain-back (or fast track) ─► final cleanup ─► squash merge
     ─► journal, plan, wiki updated
```

1. **Scope.** Every nontrivial development starts as an issue labelled `scope`: the
   contract for the work (see *Scope agreements*). The agent drafts it; the reviewer
   agrees or edits it. No work starts before agreement.
2. **Branch and draft PR.** The agent works on a branch named `<area>/<short-description>`
   and opens a draft PR that closes the scope issue as soon as the branch is first pushed,
   so every commit is retained by GitHub from the start.
3. **Work.** Small commits, each explaining why. Commits are cheap; the PR is where
   organization happens. PR branches are never rewritten (no force-push, no rebase), so
   any link to a branch commit stays valid. Superseded material on a branch moves to
   `archive/` instead of being deleted, so it stays at hand while the work continues.
4. **Explanation.** The agent writes the PR description as an explanation (see
   *Presentations*).
5. **Approval.** The reviewer approves on one of the tracks in *Approval*, in a PR
   comment.
6. **Final cleanup.** The last commit before merge deletes `archive/` and anything else
   temporary (see *Superseded material* under *Git and GitHub*).
7. **Squash merge.** The reviewer merges. `main` gets one commit per development, whose
   message is the PR's title and description: the explanation lives in `main`'s history.
8. **Record.** The agent brings the journal and plan up to date and drafts wiki pages for
   anything new or changed (see *Understanding map*).

Work done directly on `main` (small fixes, durable-state updates, anything the reviewer
asks for there) may be committed and pushed to `main`.

## Scope agreements

A scope issue says:

- **Goal:** what this development is for, and which goal in the plan it serves.
- **In scope:** what gets built and which files or directories it touches.
- **Out of scope:** what this work will not do.
- **Stopping points:** which of the standing stopping points (below) are lifted for this
  work, if any.
- **Done when:** how we will know it is finished.

Work inside an agreed scope is pre-approved. Anything outside it, the agent stops and
asks. If the scope turns out to be wrong, the agent proposes a change to the issue rather
than quietly drifting.

## Presentations

Proposals, explanations and orientations follow the same rules, so that each one is a
real check of the reviewer's understanding rather than a request for an OK.

1. **Purpose first.** Which goal this serves and why now. If it cannot be connected to a
   goal, say so: that is a warning sign.
2. **What you should understand.** Two or three things the reviewer should be able to
   explain by the end.
3. **Layers:** a plain summary paragraph; the math; a code walkthrough; the evidence
   (numbers and figures, each with the notebook or command that produced it); the
   consequences (what this commits us to or rules out); and surprises (anything that does
   not work the way one would expect).
4. **Permalinks.** Every claim about code links to the exact lines with a GitHub
   permalink (`https://github.com/<owner>/<repo>/blob/<commit>/<path>#L10-L20`).
5. **Load-bearing vs boilerplate.** The walkthrough labels code as *load-bearing — read
   this* or *boilerplate — skim*.
6. **One sitting.** If a change cannot be explained in about fifteen minutes, it is too
   big and gets split.
7. **"I don't get it" is always a good answer.** It means the explanation or the code
   needs work, never that the reviewer failed.
8. **Math that survives GitHub's markdown.** Display math goes in fenced ` ```math `
   blocks, whose content markdown leaves alone. In `$...$` and `$$...$$`, markdown eats
   a backslash before punctuation (`\,` `\;` `\!` `\{` become `,` `;` `!` `{`) and
   mangles `<`; avoid them there (write `y_{1:t-1}`, not `y_{<t}`). Check rendering
   with `gh api markdown` when in doubt.

| Presentation | When | Where |
|---|---|---|
| Proposal | Before nontrivial work | The scope issue |
| Explanation | Before merge | The PR description |
| Orientation | Start of every session (automatic) | Chat |
| Journal | At milestones | `docs/journal/` |

## Approval

Approval happens **in a PR comment**, so it is part of the PR's permanent record. (If it
happens in chat, the agent posts a short summary of it as a PR comment.) The agent cannot
merge, so approval is not enforced by the agent: it is the reviewer's own gate before
pressing merge. The PR description ends by proposing a track; the reviewer may choose
another.

| Track | For | The reviewer's comment | After merge |
|---|---|---|---|
| **Trivial** | Typo and wording fixes, dependency bumps within existing pins, `explore_` notebooks | Nothing needed | — |
| **Read** | Changes whose text *is* the content: documentation, process, decision records | "Read all changes", plus any questions | — |
| **Full** | Code, and anything whose behaviour is not visible by reading it | Explains back in a sentence or two what the change does and why | Wiki pages drafted or updated |
| **Fast** | Code, when moving quickly | Confirms the minimum: what it is for, what goes in and comes out, what it affects | `understanding-debt` label; an issue to work through it; related wiki pages `needs-review` |

On the full track the agent replies to the explanation, comparing it with what the code
does. A mismatch is a found gap: the agent explains again or the code changes. The
reviewer chooses the fast track whenever a full explain-back would cost more than the
change is worth right now; the debt it leaves is visible and gets scheduled. The trivial
list starts conservative and is calibrated over time.

## Understanding map

The repo's GitHub wiki records what the reviewer understands. It is cloned into a
gitignored `wiki/` folder in the repo.

- **Code pages**, one per load-bearing module or finalized notebook, with four sections:
  *What it does*, *How and why*, *How it fits the larger project*, *Invariants and
  pitfalls* (what must stay true if the code changes, and the mistakes that are easy to
  make). A header records which files the page covers, the `main` commit it was last
  understood at, and its status.
- **Concept pages** for the ideas the code relies on, linking code pages to the math.
- **Status** of each page: `stub`, `draft`, `understood`, `needs-review`, `stale`. A
  generated *Status board* page lists pages by status.
- **Who writes:** the agent drafts pages and entries; the reviewer edits them. A page is
  `understood` only when the reviewer says so.
- **Staleness:** a check compares each code page's recorded commit with the current
  code; pages whose code has changed materially become `stale`, and an issue is opened
  to review them.
- Code pages record `main` commits (code as it stands); journals and explanations may
  link to branch commits.

## Skills

The process is carried by skills in `.github/skills/` (one copy, readable by Claude
Code, GitHub Copilot and other agents that support Agent Skills):

| Skill | When |
|---|---|
| `orient` | Start of every session; "where are we?" |
| `scope` | Before any nontrivial development |
| `explain` | A PR is ready for review; something needs explaining |
| `journal` | At every milestone |
| `understood` | After a merge; a wiki page needs drafting or updating |
| `digest` | Periodically; when the repo starts to feel unwieldy |

## Durable state files

State lives in files, not in chat.

The agent cannot tell when a session will end, so the plan and journal are updated at
**milestones**, not at the end:

- a sub-step of agreed work is finished and pushed;
- a PR is opened, marked ready, or merged;
- a significant result, finding or dead end;
- a decision is made;
- context is compacted: hooks ask the summary to keep unrecorded milestones and remind
  the agent to record them straight afterwards;
- at the start of a session, if orientation finds the last session's work missing from
  the journal, the agent fills it in from git history before anything else.

### Plan — `docs/plan.md`

- **What:** current goals, current state, and the ordered next steps. Nothing else.
- **When to update:** at milestones (above), whenever a goal, the state, or the next steps
  change.
- **How:** rewrite in place; the old versions are in `main`'s history (see *Git and
  GitHub*).
- **When to read:** at the start of every session.

### Journal — `docs/journal/YYYY-MM-DD.md`

- **What:** a factual log of the work. One file per day; a second session on the same day
  adds a new `## Session N` section.
- **When to update:** at milestones (above). Each update adds to the current session's
  section, so the entry is always complete up to the last milestone.
- **Format:**

  ```markdown
  # YYYY-MM-DD

  ## Session 1 — <topic>

  **Goal:** what we set out to do.
  **Done:** what changed, with links to commits, PRs, notebooks (and cell labels).
  **Results:** numbers and figures, each with the notebook/command that produced it.
  **Decisions:** one line each, linking to `docs/decisions/` records where one exists.
  **Permission points:** (independent work only) where permission would normally have
  been asked, and what was decided.
  **Open questions / next:** what is unresolved; update docs/plan.md to match.
  ```

- **When to read:** the latest entry at startup; earlier entries when resuming a thread
  of work (search by topic).
- Entries are history: do not rewrite past entries except to fix errors, and say so.

### Decision records — `docs/decisions/NNNN-short-title.md`

- **What:** choices that constrain future work and are not obvious from the code: tools,
  model formulations, conventions, rejected alternatives worth remembering.
- **When to write:** when the decision is made (drafted by the agent, accepted by the
  reviewer). Small choices go in the journal's *Decisions* line instead.
- **Format:**

  ```markdown
  # NNNN — <title>

  **Date:** YYYY-MM-DD · **Status:** Proposed | Accepted | Superseded by NNNN

  **Context:** the problem and constraints.
  **Decision:** what we chose.
  **Why:** the reasons, including alternatives considered.
  **Consequences:** what this commits us to or rules out.
  ```

- **Superseding:** write a new record and set the old one's status to `Superseded by
  NNNN`. Decision records are kept, not deleted: the history of why is the point.
- **When to read:** before changing anything in an area a record covers (check titles
  with `ls docs/decisions`).

## Autonomy

- **Routine, no need to ask:** reads, searches, local edits, running notebooks and tests,
  normal git, and creating, commenting on and closing issues.
- **Standing stopping points** — ask first, unless lifted by a scope agreement or by the
  reviewer: new classes or helper functions, new directories or new kinds of auxiliary
  files, dependency changes, anything destructive or hard to undo, anything with external
  side effects beyond issues and this repo's own branches and PRs.
- **Independent work.** When asked to work independently, the agent keeps going without
  asking for any permission, including destructive changes within the repo, and records
  every point where permission would normally have been asked, and what was decided, in
  the journal's *Permission points*.
- For non-obvious tradeoffs, explain briefly and choose the simpler, less stateful option.

## Git and GitHub

- Before starting, decide whether the work needs a branch, say what was decided, and
  commit any pending work.
- Branches merge into `main` only with the reviewer's approval, through a pull request,
  as a squash merge.
- Never stop work while waiting for a merge: continue on the branch or start the next
  piece of work.
- All work must be recoverable on another machine: push at every milestone.
- **Superseded material** — the one rule, referred to elsewhere:
  - on a branch, move it to `archive/` so it stays at hand while the work continues;
  - the final commit before merge deletes `archive/`; the material stays reachable
    through the PR's commits;
  - on `main`, delete superseded files rather than keeping `old` copies; git history is
    the archive. Update or remove references in the same change.
  - Exception: decision records are kept and marked superseded.
- Commit messages explain why, not just what.
- When the agent acts through the reviewer's GitHub account, its comments start with
  **🤖 Claude:** (or the agent's name) so it is clear who wrote what.
- Replies to review comments go in the comment's own thread, with permalinks to the fix.
