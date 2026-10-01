---
name: understood
description: Draft or update a page of the understanding map (the repo wiki) for the reviewer to edit - a code page for a load-bearing module or finalized notebook, or a concept page for an idea the code relies on. Use after a PR merges, when the reviewer says they understand (or do not understand) something, or when a wiki page is stale.
---

# Understood

The wiki records what the reviewer understands (`docs/process.md`, *Understanding
map*). The agent drafts; the reviewer edits. **Only the reviewer can make a page
`understood`.** Never set that status yourself.

The wiki is a separate git repository, cloned into `wiki/` (gitignored). If the folder
is missing, clone it from the URL in `AGENTS.md`.

## Page names and header

- Code pages: `Code-<name>.md`. Concept pages: `Concept-<name>.md`.
- Every page starts with the header table from the template. `wiki_status.py` reads it:

  | Field | Meaning |
  |---|---|
  | **Kind** | `code` or `concept` |
  | **Status** | `stub`, `draft`, `needs-review`, `understood` or `stale` |
  | **Covers** | code pages: the files described, as backticked repo paths |
  | **As of** | code pages: the short `main` commit the page describes |

Templates: `templates/code-page.md` and `templates/concept-page.md` in this skill.

## Drafting a code page

1. Use a commit on `main` for **As of** (`git rev-parse --short origin/main`), never a
   branch commit.
2. Fill the four sections from the code itself, not from memory of writing it:
   - **What it does:** inputs, outputs, in plain words.
   - **How and why:** the method and the reasons, with permalinks to the lines.
   - **How it fits the larger project:** what calls it, what it depends on, which goal.
   - **Invariants and pitfalls:** what must stay true if the code changes, and the
     mistakes that are easy to make.
3. Link concept pages with `[[Concept-name]]`; create a `stub` for any that is missing.
4. Status is `draft`.
5. Math: fenced math blocks for display math (`docs/process.md`, *Presentations*).

## Statuses

| Status | Set by | Meaning |
|---|---|---|
| `stub` | agent | The page exists as a placeholder to be written. |
| `draft` | agent | Written by the agent; the reviewer has not confirmed it. |
| `understood` | reviewer | The reviewer has read, edited and confirmed it. |
| `needs-review` | either | Merged on the fast track, or the reviewer is no longer sure. |
| `stale` | script | The code changed materially since **As of**. |

When the reviewer confirms a page, set `understood` and update **As of** to the current
`main` commit. When updating a stale page, show the reviewer what changed in the code
since the old commit (`git diff <as-of> origin/main -- <covered files>`).

## Publish

```bash
python3 .github/skills/digest/scripts/wiki_status.py --write   # refresh the status board
git -C wiki add -A && git -C wiki commit -m "<what changed>" && git -C wiki push
```

Tell the reviewer which pages are waiting for them, with links.
