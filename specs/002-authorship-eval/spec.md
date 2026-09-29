# Spec 002: authorship-filter eval (lightweight)

## Why

The repo has no model call. `sim/drift_sim.py` is numpy only, and arm `B` (the language-model evidence reader)
is frozen as future work (PREREG, spec 001). A-fixed, the headline architecture, *assumes* an authorship filter
that labels user-role text as human or agent at se 0.9 / sp 0.95 for agent text (spec 001 (ii)). That filter
does not exist yet. Its operating point feeds contamination attenuation (P6) and every A-fixed sensitivity and
false-flag number. This eval measures whether a real Claude filter reaches that operating point.

## What

- **App:** `scripts/authorship_filter.py`, one Claude call per transcript entry, text in, label out
  (`human` | `agent`). It reads text only and estimates nothing about the person.
- **Cases:** `eval/authorship/cases.jsonl`, 54 synthetic user-role entries, 27 human and 27 agent, in 7
  subclasses that follow the pilot's authorship classes. They are synthetic because the real transcripts
  (`data/trace_entries.csv` points at them) are private, and sending their text to an API needs his
  go-ahead first.
- **Grader:** programmatic label match. Positive = agent text, matching the sim's convention. The runner
  reports sensitivity and specificity with Wilson 95% intervals next to the sim's assumed 0.90 / 0.95,
  plus accuracy and the majority-class baseline.
- **Split:** stratified by subclass, seed 20260929, about 40% held out as `test` (in `_state.json`),
  fixed once, never read during hillclimb.
- **Runner:** `scripts/eval_authorship.py`. It follows the build-eval contract (results.jsonl, traces/,
  errors.jsonl, resume at (case, rep), jittered backoff, a per-case ceiling, a served-model assertion, and a
  harness gate), and `--stub` modes check the harness without an API key.

## Out of scope

Condition-level labels of any kind, arm `B`, real-transcript cases, and feeding the measured se/sp back into
`drift_sim.py robust` (follow-ups).
