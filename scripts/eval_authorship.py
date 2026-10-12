"""Eval runner for the authorship filter (spec 002). Run from the repo root.

    python3 scripts/eval_authorship.py --variant baseline            # needs ANTHROPIC_API_KEY (or an `ant auth` profile)
    python3 scripts/eval_authorship.py --variant baseline --approve-harness   # first run only; the person running it approves
    python3 scripts/eval_authorship.py --stub oracle|inverse|constant|empty   # harness self-check, no API call
    python3 scripts/eval_authorship.py --check                               # grader self-check, no API call

Writes .claude/hillclimb/authorship/<variant>/{results.jsonl, traces/, errors.jsonl, confusion.json}.
Positive class = agent text (the sim's convention). Grades are label matches; nothing here estimates anything
about a person. Held-out ids live in _state.json `test_ids` and are never read during hillclimb.
"""

import argparse
import asyncio
import hashlib
import json
import math
import random
import re
import shutil
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import authorship_filter as app  # noqa: E402

FLOW = ROOT / ".claude" / "hillclimb" / "authorship"
CASES = ROOT / "eval" / "authorship" / "cases.jsonl"
SIM_ASSUMED = {"sensitivity": 0.90, "specificity": 0.95}  # spec 001 (ii)
MAX_ATTEMPTS = 5


def check_harness(state, approve):
    """sha over this runner + _state.json harness_paths; refuses on drift until a person re-approves."""
    paths = [Path(__file__).resolve()] + [ROOT / p for p in state.get("harness_paths", [])]
    h = hashlib.sha256()
    for p in sorted(set(paths)):
        h.update(str(p.relative_to(ROOT)).encode() + b"\0" + p.read_bytes())
    sha = h.hexdigest()
    if state.get("harness_sha") == sha:
        return
    if approve:
        state["harness_sha"] = sha
        (FLOW / "_state.json").write_text(json.dumps(state, indent=2) + "\n")
        print(f"harness approved: {sha[:12]}", file=sys.stderr)
        return
    print(f"harness sha {sha[:12]} is not the approved one ({str(state.get('harness_sha'))[:12]}). "
          "Review the harness, then re-run with --approve-harness.", file=sys.stderr)
    sys.exit(2)


def served_ok(requested, served):
    return served == requested or re.fullmatch(re.escape(requested) + r"[-@]\d{8}", served or "") is not None


def stub_response(kind, case, model):
    truth = case["label"]
    label = {"oracle": truth, "inverse": "human" if truth == "agent" else "agent", "constant": "human"}.get(kind)
    text = json.dumps({"label": label}) if label else ""
    return SimpleNamespace(model=model, stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)],
                           usage=SimpleNamespace(input_tokens=1, output_tokens=1))


def transient(e):
    import anthropic
    if isinstance(e, (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError)):
        return True
    return isinstance(e, anthropic.APIStatusError) and e.status_code in (408, 409, 529)


async def call_with_backoff(client, case, args):
    """Returns (resp, latency_s of the final request, attempts). Raises after MAX_ATTEMPTS."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        t0 = time.monotonic()
        try:
            if args.stub:
                resp = stub_response(args.stub, case, args.model)
            else:
                resp = await app.classify(client, case["text"], model=args.model)
            return resp, time.monotonic() - t0, attempt
        except Exception as e:
            if args.stub or not transient(e) or attempt == MAX_ATTEMPTS:
                e.attempts = attempt
                raise
            await asyncio.sleep(min(60, 2 ** attempt) * random.uniform(0.5, 1.5))


def usage_dict(u):
    keys = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    return {k: getattr(u, k, 0) or 0 for k in keys}


def append(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


async def run_case(client, case, rep, split, out, args, sem):
    key = f"{case['id']}_rep{rep}"
    async with sem:
        try:
            resp, latency, attempts = await asyncio.wait_for(call_with_backoff(client, case, args), args.timeout_s)
        except asyncio.TimeoutError:
            append(out / "errors.jsonl", {"prompt_id": case["id"], "rep": rep, "failure_class": "timeout"})
            return
        except Exception as e:
            append(out / "errors.jsonl", {"prompt_id": case["id"], "rep": rep, "failure_class": "harness_or_serving",
                                          "error": f"{type(e).__name__}: {e}", "attempts": getattr(e, "attempts", 1)})
            return

    usage = usage_dict(resp.usage)
    fallback = any(getattr(i, "type", "") == "fallback_message" for i in (getattr(resp.usage, "iterations", None) or []))
    if not fallback and not served_ok(args.model, resp.model):
        append(out / "errors.jsonl", {"prompt_id": case["id"], "rep": rep, "failure_class": "model_mismatch",
                                      "model": resp.model, "usage": usage})
        return
    predicted = app.parse_label(resp)
    status = {"refusal": "refusal", "max_tokens": "truncated"}.get(resp.stop_reason, "fallback" if fallback else "ok")
    if status == "ok" and predicted is None:
        append(out / "errors.jsonl", {"prompt_id": case["id"], "rep": rep, "failure_class": "unparseable",
                                      "model": resp.model, "usage": usage})
        return

    thinking = "\n".join(getattr(b, "thinking", "") for b in resp.content if b.type == "thinking").strip()
    answer = next((b.text for b in resp.content if b.type == "text"), "")
    trace = [{"role": "system", "content": app.SYSTEM},
             {"role": "user", "content": f"<entry>\n{case['text']}\n</entry>"},
             {"role": "assistant", "content": answer, **({"thinking": thinking} if thinking else {})}]
    (out / "traces" / f"{key}.json").write_text(json.dumps(trace, indent=2))
    append(out / "results.jsonl", {
        "prompt_id": case["id"], "rep": rep, "prompt": case["text"], "split": split,
        "tags": [case["subclass"], case["label"], "synthetic"],
        "status": status, "stop_reason": resp.stop_reason,
        "grade": {"correct": int(predicted == case["label"])},
        "model": resp.model, "usage": usage, "latency_s": round(latency, 3),
        "in_tokens": usage["input_tokens"], "out_tokens": usage["output_tokens"],
        "meta": {"label": case["label"], "predicted": predicted, "attempts": attempts},
    })


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - w, c + w


def summarize(out, expected):
    """`expected`: {(prompt_id, rep): (label, split)} for every case the run was asked to score. The *_itt
    figures count each expected case without an ok row (refusal, truncation, fallback, unparseable, timeout,
    error) as a miss, so a filter cannot raise its score by not answering the cases it would get wrong."""
    rows = [json.loads(l) for l in (out / "results.jsonl").read_text().splitlines() if l.strip()]
    n_err = sum(1 for _ in open(out / "errors.jsonl")) if (out / "errors.jsonl").exists() else 0
    ok = [r for r in rows if r["status"] == "ok"]
    report = {"rows": len(rows), "scored": len(ok), "not_scored": len(rows) - len(ok), "error_attempts": n_err}
    for split in ("train", "test", "all"):
        rs = [r for r in ok if split == "all" or r["split"] == split]
        pos = [r for r in rs if r["meta"]["label"] == "agent"]
        neg = [r for r in rs if r["meta"]["label"] == "human"]
        tp = sum(r["meta"]["predicted"] == "agent" for r in pos)
        tn = sum(r["meta"]["predicted"] == "human" for r in neg)
        exp = {k: lab for k, (lab, s) in expected.items() if split == "all" or s == split}
        hit = {(r["prompt_id"], r["rep"]) for r in rs if (r["prompt_id"], r["rep"]) in exp
               and r["meta"]["predicted"] == r["meta"]["label"]}
        n_pos = sum(lab == "agent" for lab in exp.values())
        tp_itt = sum(exp[k] == "agent" for k in hit)
        report[split] = {"n": len(rs), "tp": tp, "fn": len(pos) - tp, "tn": tn, "fp": len(neg) - tn,
                         "sensitivity": wilson(tp, len(pos)), "specificity": wilson(tn, len(neg)),
                         "accuracy": wilson(tp + tn, len(rs)),
                         "majority_baseline": max(len(pos), len(neg)) / len(rs) if rs else float("nan"),
                         "n_expected": len(exp), "sensitivity_itt": wilson(tp_itt, n_pos),
                         "specificity_itt": wilson(len(hit) - tp_itt, len(exp) - n_pos),
                         "accuracy_itt": wilson(len(hit), len(exp))}
    (out / "confusion.json").write_text(json.dumps(report, indent=2))
    print(f"{out.name}: {report['scored']} scored, {report['not_scored']} not scored "
          f"(refusal/truncated/fallback), {n_err} failed attempts in errors.jsonl")
    for split in ("test", "train", "all"):
        s = report[split]
        if not s["n"]:
            continue
        f = lambda m: "{:.2f} [{:.2f}, {:.2f}]".format(*s[m])
        print(f"  {split:5} n={s['n']:3}  sens {f('sensitivity')}  spec {f('specificity')}  "
              f"acc {f('accuracy')}  majority {s['majority_baseline']:.2f}")
        print(f"        unscored = miss, n={s['n_expected']:3}  sens {f('sensitivity_itt')}  "
              f"spec {f('specificity_itt')}  acc {f('accuracy_itt')}")
    print(f"  sim assumes sens {SIM_ASSUMED['sensitivity']:.2f} / spec {SIM_ASSUMED['specificity']:.2f} "
          "(spec 001 (ii)); the headline is the test split, unscored = miss.")


def self_check():
    """Grader regression, no API: a filter that answers only the cases it gets right must not score 1.0."""
    import tempfile
    cases = [(f"c{i}", "agent" if i % 2 else "human") for i in range(20)]
    expected = {(i, 0): (lab, "test") for i, lab in cases}
    for name, answers, want in (("oracle", lambda lab: True, 1.0), ("abstain-when-wrong", lambda lab: lab == "human", 0.5)):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            for i, lab in cases:
                if answers(lab):
                    append(out / "results.jsonl", {"prompt_id": i, "rep": 0, "split": "test", "status": "ok",
                                                   "meta": {"label": lab, "predicted": lab}})
                else:
                    append(out / "errors.jsonl", {"prompt_id": i, "rep": 0, "failure_class": "unparseable"})
            summarize(out, expected)
            got = json.loads((out / "confusion.json").read_text())["test"]["accuracy_itt"][0]
            if got != want:
                sys.exit(f"CHECK FAILED: {name} accuracy_itt {got} != {want}")
    print("check OK: oracle scores 1.0; a filter that leaves every agent case unanswered scores 0.5, not 1.0")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="baseline")
    ap.add_argument("--model", default=app.MODEL)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--timeout-s", type=float, default=180)
    ap.add_argument("--approve-harness", action="store_true")
    ap.add_argument("--stub", choices=("oracle", "inverse", "constant", "empty"))
    ap.add_argument("--check", action="store_true", help="grader self-check on synthetic rows, no API call")
    args = ap.parse_args()
    if args.check:
        return self_check()

    state = json.loads((FLOW / "_state.json").read_text())
    if args.stub:
        args.variant = f"_stub-{args.stub}"  # not baseline/vN, so the report builder ignores it
        shutil.rmtree(FLOW / args.variant, ignore_errors=True)
        client = None
    else:
        if not re.fullmatch(r"baseline|v\d+", args.variant):
            sys.exit("--variant must be baseline or v<N>")
        check_harness(state, args.approve_harness)
        import anthropic
        client = anthropic.AsyncAnthropic(max_retries=0)  # retries are ours, with jitter, and counted

    out = FLOW / args.variant
    (out / "traces").mkdir(parents=True, exist_ok=True)
    split_of = {i: "test" for i in state["test_ids"]} | {i: "train" for i in state["train_ids"]}
    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()]
    done = set()
    if (out / "results.jsonl").exists():
        done = {(r["prompt_id"], r["rep"]) for r in map(json.loads, (out / "results.jsonl").read_text().splitlines())}
    todo = [(c, k) for k in range(args.reps) for c in cases if (c["id"], k) not in done]
    print(f"{len(todo)} to run ({len(done)} already done) on {args.model} -> {out.relative_to(ROOT)}", file=sys.stderr)
    sem = asyncio.Semaphore(args.concurrency)
    await asyncio.gather(*(run_case(client, c, k, split_of[c["id"]], out, args, sem) for c, k in todo))
    if (out / "results.jsonl").exists():
        summarize(out, {(c["id"], k): (c["label"], split_of[c["id"]]) for k in range(args.reps) for c in cases})
    else:
        print(f"{out.name}: nothing scored; see {(out / 'errors.jsonl').relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())
