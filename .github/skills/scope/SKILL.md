---
name: scope
description: Draft a scope agreement as a GitHub issue before starting any nontrivial development - goal, what is in and out of scope, stopping points, and how we will know it is done. Use when the reviewer asks for something to be built, when work is about to exceed an agreed scope, or when they say "scope this".
---

# Scope

Rules: `docs/process.md`, *Scope agreements*. Format:
`.github/skills/templates/scope-issue.md`.

1. **Prepare.** Read `docs/plan.md` (which goal does this serve? if none, tell the
   reviewer before going further) and check `docs/decisions/` for records that constrain
   the work. Settle open design questions in conversation first: the issue records an
   agreement, it is not the place to discover one.
2. **Draft** the issue from the template and create it:
   `gh issue create --label scope --title "Scope: ..." --body-file <file>`.
3. **Tell the reviewer** in chat what it says and what you will not do until they agree.
4. **While working:** outside the scope, stop and ask. If the scope proves wrong,
   propose the change as a comment on the issue and wait; do not drift.
