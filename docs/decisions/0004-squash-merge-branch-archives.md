# 0004 — Squash merges, with superseded material archived on branches

**Date:** 2026-10-01 · **Status:** Accepted

**Context:** We want cheap commits during development, a clean `main`, the ability to
recover superseded code, and links to commits (in journals, explanations, wiki pages)
that keep working.

**Decision:**

- Open a draft PR as soon as a branch is pushed; never rewrite a PR branch.
- On a branch, superseded material moves to `archive/` rather than being deleted; the
  final commit before merge deletes `archive/`.
- Merge by squash. The squash commit's message is the PR title and description (the
  explanation). Branches are deleted after merge.
- Repository settings enforce this: squash merging only, message from PR title and
  description, automatic branch deletion.

**Why:** GitHub keeps every commit pushed to a PR, even after the branch is deleted and
the PR squashed, so the full working history (archived material included) stays
recoverable through the PR, and permalinks to branch commits stay valid. `main` gets one
well-explained commit per development.

*Alternatives considered:*

- **Curating commits before a merge commit:** keeps chosen intermediate commits on
  `main`, but curation rewrites commit IDs and breaks links made during development.
- **Plain merge commits:** keep everything, cluttering `main`'s history.

**Consequences:** `main`'s history is one commit per PR, so finding older intermediate
states means going through the PR. Wiki code pages record `main` commits; journals and
explanations may link to branch commits.
