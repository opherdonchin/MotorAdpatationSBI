---
name: digest
description: Review the state of the repository for the reviewer - what exists, what is stale, badly named, unused or harder to follow than it should be - and propose what to cut or fix. Also checks the understanding map for stale pages. Use periodically, when the reviewer asks for a "state of the repo", or when the project starts to feel unwieldy.
---

# Digest

The aim is a repo the reviewer can hold in their head. This produces a report with
proposals; it changes nothing except refreshing the wiki status board.

The standards are not listed here. They are the rules in `AGENTS.md` (*Working style and
repo hygiene* names the sections to audit against) and in `docs/process.md`. A new
habit worth checking is added there, and the digest then checks it.

1. **Understanding map.** `git -C wiki pull --ff-only`, then
   `python3 .github/skills/scripts/wiki_status.py --write`.
   - For each page newly `stale`, open an issue: `Review wiki page <name>: <n> lines
     changed since <commit>`.
   - List load-bearing modules and finalized notebooks with no code page.
   - List open `understanding-debt` issues.
   - Commit and push the wiki if anything changed.
2. **Audit.** Go through the tracked files (`git ls-files`) and check the repo against
   each rule in those sections. Also check the record against itself: plan,
   decision records, model docs, wiki and code should not disagree, and no rule should
   be stated in more than one place (`docs/process.md`, *Where each thing lives*).
3. **Report** in chat, shortest first: a one-paragraph verdict (is the repo getting
   easier or harder to hold in the head?); a table of findings (what, where, which rule,
   proposed action); proposed cuts, most valuable first.
4. **Follow up.** Fix nothing beyond trivial changes. Each accepted proposal becomes a
   scope issue or joins one. Record the digest as a milestone (`journal` skill).
