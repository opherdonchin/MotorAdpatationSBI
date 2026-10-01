---
name: understood
description: Draft or update a page of the understanding map (the repo wiki) for the reviewer to edit - a code page for a load-bearing module or finalized notebook, or a concept, process, guide or resource page. Use after a PR merges, when the reviewer says they understand (or do not understand) something, or when a wiki page is stale.
---

# Understood

Rules (page kinds, statuses and who may set them, when the wiki is committed):
`docs/process.md`, *Understanding map*. Formats:
`.github/skills/templates/wiki-code-page.md` and `wiki-page.md`.

The wiki is a separate git repository cloned into `wiki/` (URL in `AGENTS.md`).

1. **Pull first:** `git -C wiki pull --ff-only`. The reviewer edits pages in the browser.
2. **Draft or update** the page from its template.
   - Code pages: write from the code itself, not from memory of writing it. *As of* is
     a commit on `main` (`git rev-parse --short origin/main`), never a branch commit.
   - Updating a stale page: show the reviewer what changed,
     `git diff <as-of> origin/main -- <covered files>`.
   - Link related pages with `[[Page-name]]`; create a `stub` for any that is missing.
   - New pages are `draft`. Never set `understood` yourself; when the reviewer confirms
     a page, set it and move *As of* to the current `main` commit.
3. **Add the page** to `Home.md` and `_Sidebar.md` under its kind.
4. **Refresh the board and publish:**

   ```bash
   python3 .github/skills/scripts/wiki_status.py --write
   git -C wiki add -A && git -C wiki commit -m "<what changed>" && git -C wiki push
   ```

5. **Tell the reviewer** which pages are waiting for them, with links.
