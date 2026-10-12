"""The visuomotor adaptation Task: what a Model needs to know about it.

Reaching to a target with cursor feedback, where the cursor can be rotated (a
perturbation) or hidden. Every Schedule holds the Conditions in `CONDITION_VARS` on every
Trial, and every Sitting adds the Observations in `OBSERVATION_VARS`. Units: the
perturbation size. Terms: docs/glossary.md.
"""

# p: perturbation of the cursor; v: vision flag, 1 if the cursor is shown, 0 if not.
CONDITION_VARS = ("p", "v")

# y: error, where the cursor went relative to the target. On a Trial without vision the
# cursor is not shown, and y is where it would have gone. The movement angle is y - p.
OBSERVATION_VARS = ("y",)
