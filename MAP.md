# agentsem-drift-prereg003 map

## Entry points
- `sim/drift_sim.py`: study 1 (`--check`, `score|metrics --prereg-sha`) -> `sim/results.json`.
- `sim/study003.py`: spec 003 (`--check`, `score --prereg-sha <sha>`, `verdicts <json>`) -> `sim/results_003.json`; verdicts in `sim/RESULTS-003.md`.
- `sim/attribution*.py` (r1-r5, each `--plan-sha`, plans `sim/ATTRIBUTION-PLAN*.md`) -> `sim/attribution*.json`. Exploratory.
- Other `sim/*_003.py` follow-ups (not `decide_003.py`) write `sim/*_003.json`, reports `sim/*-003.md`.
- `scripts/eval_authorship.py` (spec 002; API-calling runs: see its docstring) over `eval/authorship/cases.jsonl`.
- `pilot/trace_audit.py` -> `pilot/results.json`; needs absent `data/`.
- `paper/figures.py` -> `paper/fig*.svg`; draft `paper/DRAFT.md`.

## Tests
- `python3 -B sim/study003.py --check` (passes)
- `python3 -B sim/drift_sim.py --check` (cell c red since freeze, not a regression: `RUNLOG.md` 2026-10-11)
- `python3 -B sim/attribution_r5.py --check` (~1 min)
- `python3 -B scripts/eval_authorship.py --check` (no API, passes)
- `python3 -B pilot/trace_audit.py --check` (passes)
- `sh scripts/claims_lint.sh` (fails now on `paper/DRAFT.md` line 578, citation line)

## Invariants
- Frozen, never edit: `sim/PREREG.md`, `sim/PREREG-003.md`, `sim/drift_sim.py`, `sim/attribution.py`, `sim/study003.py`, `sim/decide_003.py`, `sim/tuning_003.json`, `sim/results_003.json`, `sim/RESULTS-003.md` (003 hashes: `sim/POST-EVALUATION-003.md` (h)).
- Seeds derive from PREREG sha256; `score` refuses on mismatch. Do not rerun `score`.
- Frozen verdicts and thresholds never change post-results (`sim/POST-EVALUATION-003.md`); follow-ups stay exploratory, reruns byte-identical.
- Future H3 uses the interval rule (`DECISIONS.md`).
- No clinical claims or condition names: `CLAIMS-ENVELOPE.md`.
- Eval harness sha drift needs person approval (`scripts/eval_authorship.py`); unscored = miss.

## Not here
- `data/`, API keys, registry lodging and submission (owner-only).
