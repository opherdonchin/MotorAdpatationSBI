---
name: digest
description: Review the state of the repository for the reviewer - what exists, what is stale, badly named, unused or harder to follow than it should be - and propose what to cut or fix. Also checks the understanding map for stale pages. Use periodically, when the reviewer asks for a "state of the repo", or when the project starts to feel unwieldy.
---

# Digest

The aim is a repo the reviewer can hold in their head. This is a report with
proposals; it changes nothing by itself except refreshing the wiki status board.

## 1. Understanding map

```bash
python3 .github/skills/digest/scripts/wiki_status.py --write
```

- For each page newly marked `stale`, open an issue: `Review wiki page <name>: <n>
  lines changed since <commit>`.
- List load-bearing modules and finalized notebooks that have **no** code page.
- List open `understanding-debt` issues.
- Commit and push the wiki if the board changed.

## 2. Inventory

Go through the tracked files (`git ls-files`) against the layout in `AGENTS.md`.

- **Stale files:** not referenced by anything, superseded, or describing a state that
  no longer holds (documents included).
- **Misplaced or badly named files:** a name that promises more or something other
  than the content; a file outside its home.
- **Abstraction without a second use:** helpers, wrappers, classes or parameters that
  only one caller needs.
- **Hard-to-follow code:** where what the code is doing is hidden behind boilerplate.
  Say which function and why.
- **Drifting notebooks:** exploration notebooks whose result has been captured
  elsewhere; finalized notebooks that no longer run from a clean kernel.
- **Unclear currency:** results or figures where it is not obvious which commit, seed
  or notebook produced them.
- **Record drift:** places where the plan, decision records, model docs and code
  disagree.

## 3. Report

In chat, shortest first:

1. One-paragraph verdict: is the repo getting easier or harder to hold in the head?
2. A table of findings: what, where (linked), why it matters, proposed action.
3. Proposed cuts, most valuable first.

Do not fix anything beyond trivial changes. Each proposed fix the reviewer accepts
becomes a scope issue or is added to an existing one. Record the digest as a
milestone (`journal` skill).
