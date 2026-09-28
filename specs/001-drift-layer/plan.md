# Plan 001: drift layer

Stack: Python 3 stdlib + numpy (sim), stdlib (pilot), one static HTML file (demo), Markdown (paper).

| step | output | depends on | gate |
|---|---|---|---|
| 1 | Opus design review, edits applied, `sim/PREREG.md` committed and hashed | spec | review verdict is FREEZE or FREEZE WITH EDITS, edits applied |
| 2 | `sim/drift_sim.py` + `--check`, run grid, `sim/results.json`, `sim/RESULTS.md` | 1 | `--check` passes; every prediction reported PASS/FAIL against the frozen text |
| 3 | `pilot/trace_audit.py` + `--check`, `pilot/RESULTS.md` | spec section 7 | no message text in any output (grep test) |
| 4 | `demo/index.html` built from `sim/cases/*.json` by `demo/build.py` | 2 | opens offline; every number shown comes from a case file |
| 5 | `paper/DRAFT.md` | 2, 3 | every number resolves to an artifact path (claims table) |
| 6 | ponytail review, commit | 2 to 5 | hook gate |
