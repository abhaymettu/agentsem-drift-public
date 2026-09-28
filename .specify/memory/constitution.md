# agentsem-drift: constitution

## Core principles

### I. No person's mental state is inferred from real data
The only real data this repo touches is Abhay's own agent-usage metadata (timestamps, lengths,
roles, authorship class), and it is used to measure the indicators, never the person. No real-data
output estimates mood, wellbeing or any other state. A request to do so needs his explicit
consent recorded in `DECISIONS.md`, not an edit elsewhere.

### II. Synthetic is labelled synthetic
Every simulation number is labelled synthetic where it appears. Simulation tests pipeline logic and
failure localization, not predictive validity, and no text in this repo says otherwise.

### III. Freeze before scoring
The case generator, its scenario families, the held-out split and the predictions are committed and
hashed before any architecture is scored. Post-run additions are tagged as such.

### IV. Source or mark it
Every citation comes from a URL opened in this lane or a file on disk, or it is marked unverified.
Prior-lane claims are cited by repo, file and commit, not restated as fresh checks.

### V. Build on the program, do not fork it
agentSEM Studies 1 to 6 (`~/code/agentsem-*`) and the 2026-09-24 decision lock (O1 to O10) are the
context. Where tonight's framing conflicts with the lock, the conflict is written into the decision
slate, not resolved silently.

### VI. Minimal code
numpy and the standard library only. One simulation module, one pilot module, one render script,
one runnable check each.

### VI-b. No diagnostic claims (his ruling, 2026-09-27 21:02)
No artifact makes a clinical diagnosis, screening or severity claim, or names a condition as a target.
The object is a within-person wellbeing/functioning drift signal, oriented toward help, referral and
reversible intervention. Conservative non-diagnostic language applies until the regulatory-boundary note
lands.

### VII. Nothing leaves the machine
No remote, no push, no upload, no outbound nudge to any person. Per-message pilot tables stay in
gitignored `data/`.

## Governance
`specs/001-drift-layer/spec.md` defines the deliverables. Deviations go in
`~/lanes/bridge-jobs/agentsem-overnight-20260927/receipts.md`.

**Version**: 1.0.0 | **Ratified**: 2026-09-27
