---
name: explain
description: Write the explanation of a change as its pull-request description, so the reviewer genuinely understands it before merging - purpose, what to understand, math, a code walkthrough with permalinks, evidence, consequences and surprises. Use when a PR is ready for review, or when the reviewer asks to have a change or a piece of code explained.
---

# Explain

The PR description is the explanation, and on a squash merge it becomes the commit
message on `main`. Rules: `docs/process.md`, *Presentations* and *Approval*.

## Before writing

1. Everything is committed and pushed. Never rewrite the branch.
2. Note the head commit: `git rev-parse --short HEAD`. Every permalink uses it:
   `https://github.com/<owner>/<repo>/blob/<commit>/<path>#L10-L20`.
3. Read the full diff against `main` yourself (`git diff main...HEAD`). Explain what the
   code does, not what you meant it to do.
4. If the explanation will not fit one sitting (about fifteen minutes), say so and
   propose how to split the PR instead of writing a longer explanation.

## Structure

```markdown
Closes #<scope issue>   (or "Part of #<issue>")

## Purpose
Which plan goal this serves and why now.

## What you should understand after reading this
Two or three specific things, phrased so the reviewer can check themselves.

## Summary
One plain paragraph. Any deviation from the scope issue, stated up front.

## The math
Only what the code implements. Display math in fenced math blocks.

## Walkthrough
### Load-bearing: read these
- **<name>:** [file#Lx-Ly](permalink). What it does, and why it is written this way.
### Boilerplate: skim
- ...

## Evidence
Numbers and figures, each with the notebook cell or command that produced it.

## Consequences
What this commits us to or rules out.

## Surprises
Anything that does not work the way one would expect.

## Approval track
Proposed: trivial | read | full | fast, with one line of why.
```

Order the walkthrough by ideas, not by files. Leave a section out when it has nothing
to say (no math in a docs change), rather than filling it.

## Check before publishing

- Render the description with GitHub's own renderer and look for mangled math:
  `gh api markdown -f mode=gfm -f text="$(cat description.md)"`.
- Every permalink points at the head commit and the line range it claims.
- Publish with `gh pr edit <n> --body-file description.md`, then `gh pr ready <n>`.

## After the reviewer responds

- **Full track:** reply to their explain-back in the PR, comparing it with what the code
  does. Be specific about any mismatch; then explain again or change the code.
- **Fast track:** add the `understanding-debt` label, and after merge open an issue to
  work through the change properly; mark related wiki pages `needs-review`.
- **Review comments:** reply in each comment's own thread with a permalink to the fix.
  If commits were added, update the description's permalinks to the new head commit and
  add a "Changes after review" section.
- After merge: record the milestone (`journal` skill) and draft or update wiki pages
  (`understood` skill).
