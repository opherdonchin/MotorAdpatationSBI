---
name: explain
description: Write the explanation of a change as its pull-request description, so the reviewer genuinely understands it before merging - purpose, what to understand, math, a code walkthrough with permalinks, evidence, consequences and surprises. Use when a PR is ready for review, or when the reviewer asks to have a change or a piece of code explained.
---

# Explain

Rules: `docs/process.md`, *Presentations* and *Approval*. Format:
`.github/skills/templates/pr-explanation.md`. On a squash merge the description becomes
the commit message on `main`.

## Write

1. Commit and push everything. Never rewrite the branch.
2. Note the head commit (`git rev-parse --short HEAD`); every permalink uses it.
3. Read the whole diff against `main` (`git diff main...HEAD`). Explain what the code
   does, not what you meant it to do.
4. If it will not fit one sitting, say so and propose how to split the PR.
5. Fill the template. Order the walkthrough by ideas, not by files. Leave out a section
   that has nothing to say.

## Check, then publish

- Render it with GitHub's renderer and look for mangled math:
  `gh api markdown -f mode=gfm -f text="$(cat description.md)"`.
- Check that every permalink shows the lines it claims.
- GitHub closes an issue on merge whenever a closing keyword (`close`, `fix`,
  `resolve` and their variants) comes directly before `#<n>`, in any sentence. Keep
  those words away from issue numbers unless this PR finishes that issue.
- `gh pr edit <n> --body-file description.md`, then `gh pr ready <n>`.

## After the reviewer responds

- **Review comments:** reply in each comment's own thread, with a permalink to the fix.
  General comments get one reply comment. If commits were added, move the description's
  permalinks to the new head commit and add a *Changes after review* section.
- **Full track:** reply to their explain-back, comparing it with what the code does.
- **Fast track:** add the `understanding-debt` label; after merge, open an issue to work
  through the change, and mark related wiki pages `needs-review`.
- **After merge:** `journal` skill, then `understood` skill.
