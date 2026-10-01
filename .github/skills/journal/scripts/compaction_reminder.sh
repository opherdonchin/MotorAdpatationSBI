#!/usr/bin/env bash
# Hook helper for context compaction. The agent cannot record a milestone "before"
# compaction (a hook cannot make it work), so the reminder is carried across it:
#   pre  - printed before compaction, as guidance for what the summary must keep
#   post - printed when the session resumes after compaction, into the agent's context
case "${1:-}" in
    pre)
        echo "When summarizing, keep every milestone not yet recorded in docs/journal/"
        echo "or docs/plan.md: finished and pushed sub-steps, PR state changes, results,"
        echo "findings, dead ends, decisions, and any open question for the reviewer."
        ;;
    post)
        echo "Context was just compacted. Before continuing, bring docs/journal/ and"
        echo "docs/plan.md up to date with any milestone they do not yet record (see the"
        echo "'journal' skill), using the summary above and git log."
        ;;
    *)
        echo "usage: compaction_reminder.sh pre|post" >&2
        exit 1
        ;;
esac
