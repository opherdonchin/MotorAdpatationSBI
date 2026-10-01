---
name: scope
description: Draft a scope agreement as a GitHub issue before starting any nontrivial development - goal, what is in and out of scope, stopping points, and how we will know it is done. Use when the reviewer asks for something to be built, when work is about to exceed an agreed scope, or when they say "scope this".
---

# Scope

A scope issue is the contract for a piece of work (`docs/process.md`, *Scope
agreements*). Work inside an agreed scope is pre-approved; nothing starts before
agreement.

## Before drafting

- Read `docs/plan.md`: which goal does this serve? If none, say so to the reviewer
  before going further.
- Check `docs/decisions/` for records that constrain the work.
- Settle open design questions in conversation first. The issue records an agreement;
  it is not the place to discover one.

## Draft the issue

Title: `Scope: <short description>`. Label: `scope`. Body:

```markdown
## Goal
What this is for, and which plan goal it serves.

## In scope
What gets built; the files and directories it touches. If it needs more than one PR,
list them: each PR must be explainable in one sitting.

## Out of scope
What this work will not do.

## Stopping points
Which standing stopping points are lifted for this work (new classes, helper functions,
directories, dependencies...). Everything not listed still applies.

## Done when
Checkable conditions. For scientific work, the correctness checks agreed with the
reviewer.
```

Create it with `gh issue create --label scope`, then tell the reviewer in chat what it
says and what you are *not* going to do until they agree.

## While working

- Anything outside the scope: stop and ask.
- If the scope proves wrong, propose the change as a comment on the issue and wait for
  agreement. Do not drift.
- The PR that finishes the work says `Closes #<issue>`.
