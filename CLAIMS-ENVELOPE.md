# Claims envelope (binding)

Source: `~/lanes/bridge-jobs/agentsem-overnight-20260927/regulatory_boundary_note.md` (2026-09-27), and his
21:02 ruling: no clinical diagnosis claims; frame the work as helping people. This file binds every artifact
in this repo, and the paper and brief most of all. `scripts/claims_lint.sh` enforces the avoid-list on the
person-facing and translational artifacts.

## Two directions, two envelopes

- **Method claims (paper body):** detection sensitivity to planted drift, false flags per tracked
  person-month, calibration under probe schedules, measurement invariance, and authorship contamination
  of indicators. CUSUM `h`, `k` and other cutoffs are method parameters. Allowed. Outside simulation
  (real traces, the corpus audit), a change recovered from the indicators is called a change in
  engagement regime, not in wellbeing or functioning, unless an independent anchor supports the link
  (spec 001 section 11.6, 2026-10-03).
- **Person-facing claims (the brief, the demo, any translational paragraph):** the wellness envelope
  only. No condition names, no clinical thresholds, no screening, diagnosis, monitoring or management
  intended use, no alerts that recommend clinical action, and no clinical-equivalence claims.

## Use

- "well-being signals", "behavioral patterns", "wellness trends", "within-person change from the person's
  own baseline"
- "tracks trends and baselines over time"
- "may help people notice changes worth discussing with a professional"
- "this method is a measurement research tool, not a diagnostic instrument"
- "signals are screening-level; any individual-level concern warrants professional evaluation" (in the
  paper's single translational paragraph, with the standard disclaimer)

## Avoid

The following are listed in the note as disqualifiers or as device-side terms:
- "detects", "screens for" or "monitors" a named condition;
- "early warning system" for a condition;
- "risk score";
- disease-specific alerts;
- "clinical-grade", "clinically validated", "as accurate as a clinician", or instrument equivalence;
- "helps manage" or "helps treat" a condition;
- "continuous ... monitoring";
- "diagnostic", "pathological" or "abnormal" near any person-facing output.

Condition names appear only where the paper cites prior literature, never as this work's target or
result.

## Referral carve-out: the only permitted wording for the referral action

> When the patterns the tool tracks move outside their usual range, it can let the person know that
> talking with a healthcare professional might be helpful - without naming any condition, labeling the
> change as abnormal, or recommending any treatment.

The demo's referral suggestion text, verbatim:
"Your recent patterns look different from your usual ones. If anything is weighing on you, talking with
someone you trust or a healthcare professional might help."

## Tripwires (note section 5)

1. Direction of inference: person-facing claims use the wellness envelope.
2. Say "tracking trends", not "monitoring".
3. No numeric cutoff is ever presented to a person as indicating a state.
