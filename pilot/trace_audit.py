#!/usr/bin/env python3
"""pilot/trace_audit.py -- metadata-only audit of Abhay's own Claude Code transcripts.

Binding documents: specs/001-drift-layer/spec.md sections 7 and 9,
.specify/memory/constitution.md.

HARD RULE, enforced by construction, not by convention: this script never writes any
message text, snippet, or content-derived string anywhere -- not to data/trace_entries.csv,
not to pilot/RESULTS.md or pilot/results.json, not to stdout. The only things that ever
leave an in-memory `text` variable are: booleans (marker / overlap present or not), integer
char counts, short controlled-vocabulary reason codes, and sha256 hex digests computed
for comparison against locally-stored lane-prompt files (compared and discarded, never
printed). `origin.body` and `toolUseResult` content fields are never read. No mental-state,
mood, or health inference is made anywhere in this file: it measures INDICATORS of how
much of the "user" stream is machine-authored and how usage-pattern change points line up
with dated agent-infrastructure events, never the person. Per spec.md section 9 / Stage 2,
this is diligence work that precedes and gates any real-trace demo (Stage 3), which stays
out of scope here.

Reads (read-only):
    ~/.claude/projects/**/*.jsonl
    ~/.instinct/lanes/prompts/*.txt   (compared by hash/prefix only, never persisted)
Writes:
    data/trace_entries.csv  (gitignored)
    pilot/results.json
    pilot/RESULTS.md

Usage:
    python3 pilot/trace_audit.py            # full audit
    python3 pilot/trace_audit.py --check    # classifier self-test on synthetic data only
"""

import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")
LANE_PROMPTS_DIR = os.path.expanduser("~/.instinct/lanes/prompts")
LOCAL_TZ_NAME = "America/Chicago"
LOCAL_TZ = ZoneInfo(LOCAL_TZ_NAME)
LANE_PREFIX_LEN = 200

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PILOT_DIR = os.path.join(REPO_ROOT, "pilot")
CSV_PATH = os.path.join(DATA_DIR, "trace_entries.csv")
JSON_PATH = os.path.join(PILOT_DIR, "results.json")
MD_PATH = os.path.join(PILOT_DIR, "RESULTS.md")
INDICATOR4_PATH = os.path.join(PILOT_DIR, "indicator4_params.json")

# Markers whose presence anywhere in the user-authored text means the WHOLE entry is
# system/hook/tool machinery injected into the transcript, not something typed by Abhay.
FULL_INJECTION_MARKERS = [
    "<system-reminder>",
    "<command-name>",
    "<command-message>",
    "<local-command-stdout>",
    "hook success",
    "<task-notification>",
    "Caveat: The messages below were generated",
    "[Request interrupted",
]
# The paste marker gets its own branch rather than being folded into the list above,
# because it can appear INSIDE an otherwise human-typed message (see classify_terminal).
PASTE_MARKER = "<pasted_content"
PASTE_BLOCK_RE = re.compile(r"<pasted_content[^>]*>.*?</pasted_content>", re.DOTALL)

# Tool names (infra identifiers, not message content) treated as "third-party surface"
# tool results: results of calling a tool that talks to other people's messages/calendars.
THIRD_PARTY_TOOL_KEYWORDS = (
    "gmail", "imessage", "slack", "calendar", "sms", "telegram",
    "whatsapp", "discord", "mail", "messaging",
)

CLASSES = ("tool-result", "injected", "lane-prompt", "sidechain", "human-typed", "human+paste")

# Pasted-agent-draft overlap check (Opus review item c): bounded, in-memory only.
DRAFT_WINDOW = 200
DRAFT_STRIDE = 40
DRAFT_BUFFER_TURNS = 5  # only compare against the last N assistant turns of the session

CSV_FIELDS = [
    "timestamp_utc", "date_local", "month_local", "hour_local",
    "session_id", "project_slug", "entry_type", "role",
    "is_sidechain", "is_meta", "is_subagent_file", "session_kind",
    "class", "classification_reason", "chars", "typed_chars", "pasted_chars",
    "paste_split_clean", "has_paste_marker", "third_party_tool_result",
    "pasted_agent_draft", "provenance_prompt_source", "provenance_turn_origin",
]


# --------------------------------------------------------------------------
# Lane-prompt corpus: loaded once, compared only via hash / prefix, never persisted.
# --------------------------------------------------------------------------

def load_lane_prompts(prompts_dir=LANE_PROMPTS_DIR):
    hashes, prefixes = set(), set()
    if not os.path.isdir(prompts_dir):
        return hashes, prefixes
    for fn in os.listdir(prompts_dir):
        path = os.path.join(prompts_dir, fn)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", errors="replace") as fh:
                raw = fh.read()
        except OSError:
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        hashes.add(hashlib.sha256(stripped.encode("utf-8", "replace")).hexdigest())
        prefixes.add(stripped[:LANE_PREFIX_LEN])
    return hashes, prefixes


def matches_lane_prompt(stripped_text, hashes, prefixes):
    if not stripped_text:
        return False
    digest = hashlib.sha256(stripped_text.encode("utf-8", "replace")).hexdigest()
    if digest in hashes:
        return True
    for p in prefixes:
        if p and stripped_text.startswith(p):
            return True
    return False


# --------------------------------------------------------------------------
# Content walking. `text` lives only in local variables, used for marker/hash
# checks, and is discarded the moment a row is finalized.
# --------------------------------------------------------------------------

def extract_text_and_chars(content):
    """Walk message['content'] (str, or list of text/tool_result/image/... blocks).

    Returns (joined_text, total_chars, has_tool_result). Only 'text'-type blocks (and
    plain string content) contribute text/chars; image, tool_reference, tool_use and
    thinking blocks contribute 0 (no prose payload, or -- for tool_use/thinking -- a
    payload we deliberately do not treat as authored text). tool_result content is
    walked too (so `chars` reflects what was actually shown) but never re-inspected for
    markers, since has_tool_result already forces the 'tool-result' class.
    NEVER reads a `toolUseResult` field -- that lives on the raw JSON line object, not
    inside message.content, and this function is never pointed at it.
    """
    parts = []
    state = {"chars": 0, "has_tool_result": False}

    def walk(node):
        if node is None:
            return
        if isinstance(node, str):
            parts.append(node)
            state["chars"] += len(node)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, dict):
            btype = node.get("type")
            if btype == "tool_result":
                state["has_tool_result"] = True
                walk(node.get("content"))
                return
            if btype in ("image", "tool_reference", "tool_use", "thinking"):
                return
            if btype == "text":
                txt = node.get("text")
                if isinstance(txt, str):
                    parts.append(txt)
                    state["chars"] += len(txt)
                return
            # Unknown block shape: best-effort fall back to a 'text' field or
            # nested 'content', otherwise contributes nothing.
            txt = node.get("text")
            if isinstance(txt, str):
                parts.append(txt)
                state["chars"] += len(txt)
            if "content" in node:
                walk(node["content"])
            return
        return  # numbers/bools/etc: no text

    walk(content)
    return "".join(parts), state["chars"], state["has_tool_result"]


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

def split_paste(text):
    """Split text containing PASTE_MARKER into (remaining, typed_chars, pasted_chars, clean)."""
    matches = list(PASTE_BLOCK_RE.finditer(text))
    if matches:
        pasted_chars = sum(len(m.group(0)) for m in matches)
        remaining = PASTE_BLOCK_RE.sub("", text)
        return remaining, len(remaining), pasted_chars, True
    idx = text.find(PASTE_MARKER)
    remaining = text[:idx]
    pasted_chars = len(text) - len(remaining)
    return remaining, len(remaining), pasted_chars, False


def classify_terminal(is_subagent_file, is_sidechain, is_meta, has_tool_result, text,
                       prompt_source=None, turn_origin=None):
    """Return (class, typed_chars, pasted_chars, paste_split_clean, reason), or None if
    the entry is 'pending' (its class depends on whether it is the first real user text
    of its session -- resolved by resolve_pending()).

    Priority order (each entry gets exactly one class):
      1. sidechain    -- isSidechain true, or the entry lives in a subagents/ file.
      2. tool-result  -- content contains a tool_result block.
      3. provenance   -- promptSource == 'sdk' or turnOrigin == 'sdk' (PRIMARY signal,
                          per Opus review item a): the transcript itself says this turn
                          was submitted programmatically, not typed. Coverage of these
                          fields is sparse (see RESULTS.md) so this only decides the
                          ~4% of entries where the field is present and says 'sdk'.
      4. injected     -- isMeta true, or text contains a full-message injection marker
                          (only reached when provenance did not already decide).
      5. human+paste / injected -- text contains a pasted_content block.
      6. pending -- everything else with text; resolved per-session in pass 2.
    """
    if is_subagent_file or is_sidechain:
        return ("sidechain", None, None, None, "structural-sidechain")
    if has_tool_result:
        return ("tool-result", None, None, None, "structural-tool-result")
    if prompt_source == "sdk" or turn_origin == "sdk":
        return ("injected", None, None, None, "provenance-sdk")
    if is_meta:
        return ("injected", None, None, None, "ismeta")
    for marker in FULL_INJECTION_MARKERS:
        if marker in text:
            return ("injected", None, None, None, "marker")
    if PASTE_MARKER in text:
        remaining, typed_chars, pasted_chars, clean = split_paste(text)
        if remaining.strip():
            if clean:
                return ("human+paste", typed_chars, pasted_chars, True, "paste-clean")
            return ("human+paste", None, None, False, "paste-dirty")
        return ("injected", None, None, None, "paste-pure")
    return None


def resolve_pending(pending, hashes, prefixes):
    """Resolve the pending (lane-prompt vs human-typed) records in place, grouped by
    session, ordered by timestamp. Only the chronologically first pending record of a
    session is ever checked against the lane-prompt corpus."""
    by_session = defaultdict(list)
    for rec in pending:
        key = rec.get("session_id") or ("__nosession__", rec["_line_idx"])
        by_session[key].append(rec)

    for _key, recs in by_session.items():
        recs.sort(key=lambda r: ((r.get("timestamp_utc") or ""), r["_line_idx"]))
        first = recs[0]
        if matches_lane_prompt(first["_text_stripped"], hashes, prefixes):
            first["class"] = "lane-prompt"
            first["typed_chars"] = None
            first["classification_reason"] = "lane-prompt-match"
        else:
            first["class"] = "human-typed"
            first["typed_chars"] = first["chars"]
            first["classification_reason"] = "human-typed-default"
        first["pasted_chars"] = None
        first["paste_split_clean"] = None
        for rec in recs[1:]:
            rec["class"] = "human-typed"
            rec["typed_chars"] = rec["chars"]
            rec["pasted_chars"] = None
            rec["paste_split_clean"] = None
            rec["classification_reason"] = "human-typed-default"
    return pending


def compute_pasted_overlap(user_text, assistant_texts, window=DRAFT_WINDOW, stride=DRAFT_STRIDE):
    """Boolean only: does user_text contain a >=window-char span that also appears in
    one of assistant_texts (the session's last few assistant turns)? Everything here is
    local variables, discarded on return; only the boolean survives."""
    if not user_text or len(user_text) < window:
        return False
    shingles = set()
    for atext in assistant_texts:
        if not atext or len(atext) < window:
            continue
        for i in range(0, len(atext) - window + 1, stride):
            shingles.add(atext[i:i + window])
    if not shingles:
        return False
    for i in range(0, len(user_text) - window + 1, stride):
        if user_text[i:i + window] in shingles:
            return True
    return False


# --------------------------------------------------------------------------
# Corpus walk
# --------------------------------------------------------------------------

def discover_files(root=PROJECTS_ROOT):
    out = []
    for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        rel = os.path.relpath(path, root)
        parts = rel.split(os.sep)
        project_slug = parts[0] if parts else ""
        is_subagent_file = "subagents" in parts[:-1]
        out.append((path, project_slug, is_subagent_file))
    return out


def run_audit():
    t_start = time.time()
    hashes, prefixes = load_lane_prompts()
    files = discover_files()
    stats = {
        "files_found": len(files),
        "files_opened": 0,
        "files_failed_to_open": 0,
        "lines_read": 0,
        "user_entries": 0,
        "assistant_entries": 0,
        "parse_errors": 0,
        "unparseable_timestamps": 0,
        "provenance_coverage": {"promptSource": 0, "turnOrigin": 0, "entrypoint": 0, "userType": 0},
    }

    finalized = []
    pending = []
    line_idx = 0

    version_first_seen = {}   # version string -> earliest date_local
    model_first_seen = {}     # message.model string -> earliest date_local
    session_assistant_buffer = defaultdict(list)   # session_id -> [recent assistant text]
    session_tool_names = defaultdict(dict)         # session_id -> {tool_use_id: name}

    def note_version(date_local, version):
        if version is None:
            return
        cur = version_first_seen.get(version)
        if cur is None or (date_local and date_local < cur):
            version_first_seen[version] = date_local

    def note_model(date_local, model):
        if model is None:
            return
        cur = model_first_seen.get(model)
        if cur is None or (date_local and date_local < cur):
            model_first_seen[model] = date_local

    for path, project_slug, is_subagent_file in files:
        try:
            fh = open(path, "r", errors="replace")
        except OSError:
            stats["files_failed_to_open"] += 1
            continue
        stats["files_opened"] += 1
        with fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                stats["lines_read"] += 1
                try:
                    obj = json.loads(line)
                except Exception:
                    stats["parse_errors"] += 1
                    continue

                entry_type = obj.get("type")
                if entry_type not in ("user", "assistant"):
                    continue

                ts_raw = obj.get("timestamp")
                ts = None
                if ts_raw:
                    try:
                        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    except ValueError:
                        pass
                date_local = ts.astimezone(LOCAL_TZ).date().isoformat() if ts is not None else None
                note_version(date_local, obj.get("version"))

                session_id = obj.get("sessionId")

                if entry_type == "assistant":
                    stats["assistant_entries"] += 1
                    message = obj.get("message")
                    if not isinstance(message, dict) or message.get("role") != "assistant":
                        continue
                    note_model(date_local, message.get("model"))
                    text, _chars, _htr = extract_text_and_chars(message.get("content"))
                    if text and session_id:
                        buf = session_assistant_buffer[session_id]
                        buf.append(text)
                        if len(buf) > DRAFT_BUFFER_TURNS:
                            del buf[0]
                    content = message.get("content")
                    if isinstance(content, list) and session_id:
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "tool_use":
                                tid, nm = b.get("id"), b.get("name")
                                if tid and nm:
                                    session_tool_names[session_id][tid] = nm
                    continue

                # entry_type == "user"
                message = obj.get("message")
                if not isinstance(message, dict) or message.get("role") != "user":
                    continue
                stats["user_entries"] += 1
                line_idx += 1

                if ts is None:
                    stats["unparseable_timestamps"] += 1

                is_sidechain = bool(obj.get("isSidechain"))
                is_meta = bool(obj.get("isMeta"))
                prompt_source = obj.get("promptSource")
                turn_origin = obj.get("turnOrigin")
                for fname, fval in (("promptSource", prompt_source), ("turnOrigin", turn_origin),
                                    ("entrypoint", obj.get("entrypoint")), ("userType", obj.get("userType"))):
                    if fval is not None:
                        stats["provenance_coverage"][fname] += 1

                text, chars, has_tool_result = extract_text_and_chars(message.get("content"))

                third_party_tool_result = None
                if has_tool_result:
                    names_used = []
                    content = message.get("content")
                    if isinstance(content, list):
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "tool_result":
                                tid = b.get("tool_use_id")
                                nm = session_tool_names.get(session_id, {}).get(tid)
                                if nm:
                                    names_used.append(nm)
                    third_party_tool_result = any(
                        any(kw in nm.lower() for kw in THIRD_PARTY_TOOL_KEYWORDS) for nm in names_used
                    )

                row = {
                    "timestamp_utc": ts.astimezone(timezone.utc).isoformat() if ts else None,
                    "session_id": session_id,
                    "project_slug": project_slug,
                    "entry_type": entry_type,
                    "role": message.get("role"),
                    "is_sidechain": is_sidechain,
                    "is_meta": is_meta,
                    "is_subagent_file": is_subagent_file,
                    "chars": chars,
                    "has_paste_marker": PASTE_MARKER in text,
                    "third_party_tool_result": third_party_tool_result,
                    "provenance_prompt_source": prompt_source,
                    "provenance_turn_origin": turn_origin,
                }
                if ts is not None:
                    local = ts.astimezone(LOCAL_TZ)
                    row["date_local"] = local.date().isoformat()
                    row["month_local"] = local.strftime("%Y-%m")
                    row["hour_local"] = local.hour
                else:
                    row["date_local"] = None
                    row["month_local"] = None
                    row["hour_local"] = None

                terminal = classify_terminal(is_subagent_file, is_sidechain, is_meta,
                                              has_tool_result, text, prompt_source, turn_origin)
                if terminal is not None:
                    cls, typed_chars, pasted_chars, clean, reason = terminal
                    row["class"] = cls
                    row["typed_chars"] = typed_chars
                    row["pasted_chars"] = pasted_chars
                    row["paste_split_clean"] = clean
                    row["classification_reason"] = reason
                    row["pasted_agent_draft"] = None
                    finalized.append(row)
                else:
                    draft_flag = compute_pasted_overlap(
                        text, session_assistant_buffer.get(session_id, [])
                    )
                    row["pasted_agent_draft"] = draft_flag
                    row["_text_stripped"] = text.strip()
                    row["_line_idx"] = line_idx
                    pending.append(row)

    resolve_pending(pending, hashes, prefixes)
    for rec in pending:
        rec.pop("_text_stripped", None)
        rec.pop("_line_idx", None)
        finalized.append(rec)

    # session_kind: autonomous (0 human activity) / mixed (started as lane-prompt but a
    # human joined) / interactive (started human). Subagent-file rows are excluded from
    # session identity; only rows describing a session's own top-level traffic count.
    session_rows = defaultdict(list)
    for r in finalized:
        if not r["is_subagent_file"] and r["session_id"]:
            session_rows[r["session_id"]].append(r)
    session_kind = {}
    for sid, recs in session_rows.items():
        recs.sort(key=lambda r: r.get("timestamp_utc") or "")
        human_activity = any(r["class"] in ("human-typed", "human+paste") for r in recs)
        if not human_activity:
            session_kind[sid] = "autonomous"
        elif recs[0]["class"] == "lane-prompt":
            session_kind[sid] = "mixed"
        else:
            session_kind[sid] = "interactive"
    for r in finalized:
        r["session_kind"] = session_kind.get(r["session_id"]) if r["session_id"] else None

    stats["elapsed_seconds"] = time.time() - t_start
    stats["lane_prompt_files"] = len(hashes) or len(prefixes)

    infra = {
        "versions": sorted(({"value": k, "first_seen_date": v} for k, v in version_first_seen.items()),
                            key=lambda x: (x["first_seen_date"] or "")),
        "models": sorted(({"value": k, "first_seen_date": v} for k, v in model_first_seen.items()),
                          key=lambda x: (x["first_seen_date"] or "")),
    }
    return finalized, stats, infra


# --------------------------------------------------------------------------
# Aggregation helpers
# --------------------------------------------------------------------------

def iqr(values):
    if len(values) < 2:
        return None
    qs = statistics.quantiles(values, n=4, method="inclusive")
    return qs[2] - qs[0]


def summary_stats(values):
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0, "mean": None, "median": None, "iqr": None}
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "iqr": iqr(values),
    }


def safe_correlation(xs, ys):
    if len(xs) < 2 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None


def build_day_indicator_series(rows, only_human_typed=False):
    """Return {date: {'late_share', 'fragmentation', 'mean_log_len'}} using either all
    rows that day (naive) or human-typed rows only (filtered)."""
    buckets = defaultdict(lambda: {"late": 0, "n": 0, "chars_log": [], "hour_sessions": defaultdict(set)})
    for r in rows:
        date = r["date_local"]
        hour = r["hour_local"]
        if date is None or hour is None:
            continue
        if only_human_typed and r["class"] != "human-typed":
            continue
        b = buckets[date]
        b["n"] += 1
        if hour < 5:
            b["late"] += 1
        b["chars_log"].append(math.log1p(r["chars"]))
        sid = r["session_id"]
        if sid:
            b["hour_sessions"][hour].add(sid)

    out = {}
    for date, b in buckets.items():
        n = b["n"]
        if n == 0:
            continue
        frag_vals = [len(v) for v in b["hour_sessions"].values()]
        out[date] = {
            "late_share": b["late"] / n,
            "fragmentation": statistics.fmean(frag_vals) if frag_vals else None,
            "mean_log_len": statistics.fmean(b["chars_log"]) if b["chars_log"] else None,
            "n": n,
        }
    return out


def indicator_correlation_report(naive_by_day, filtered_by_day):
    naive_days = set(naive_by_day)
    filtered_days = set(filtered_by_day)
    report = {}
    for key in ("late_share", "fragmentation", "mean_log_len"):
        paired_days = sorted(d for d in naive_days if d in filtered_days
                              and naive_by_day[d][key] is not None and filtered_by_day[d][key] is not None)
        naive_vals = [naive_by_day[d][key] for d in paired_days]
        filtered_vals = [filtered_by_day[d][key] for d in paired_days]
        corr = safe_correlation(naive_vals, filtered_vals)
        mad = statistics.fmean(abs(a - b) for a, b in zip(naive_vals, filtered_vals)) if paired_days else None
        naive_all = [naive_by_day[d][key] for d in naive_days if naive_by_day[d][key] is not None]
        filtered_all = [filtered_by_day[d][key] for d in filtered_days if filtered_by_day[d][key] is not None]
        report[key] = {
            "n_paired_days": len(paired_days),
            "correlation_naive_vs_filtered": corr,
            "mean_abs_difference": mad,
            "naive_distribution": summary_stats(naive_all),
            # NOTE: per Opus review item (f), filtered-series LEVEL statistics
            # (mean/median/IQR of the human-typed-only series) are intentionally
            # NOT included here -- only the naive distribution, and the
            # naive-vs-filtered correlation/difference, which describe contamination,
            # not the underlying (state-adjacent) level.
            "filtered_distribution_n_only": filtered_all.__len__(),
        }
    share_naive_only = (
        len(naive_days - filtered_days) / len(naive_days) if naive_days else None
    )
    return report, share_naive_only, len(naive_days), len(filtered_days)


# --------------------------------------------------------------------------
# Change-point detection: penalized binary segmentation on the mean (BIC).
# stdlib only. Applied to TRAIN only; magnitudes are used internally for the
# persistence check but are never surfaced (see render_results_md / item f).
# --------------------------------------------------------------------------

def _seg_negloglik(vals):
    m = len(vals)
    if m == 0:
        return 0.0
    mean = sum(vals) / m
    var = sum((v - mean) ** 2 for v in vals) / m
    if var <= 1e-12:
        var = 1e-12
    return 0.5 * m * math.log(2 * math.pi * var) + 0.5 * m


def binary_segmentation(vals, min_len=5):
    """Return sorted list of change-point indices (0-based, index of first point in the
    new segment) found by recursive penalized binary segmentation, BIC penalty."""
    change_points = []

    def recurse(lo, hi):
        seg = vals[lo:hi]
        n = len(seg)
        if n < 2 * min_len:
            return
        cost0 = _seg_negloglik(seg)
        best = None
        for t in range(min_len, n - min_len + 1):
            cost1 = _seg_negloglik(seg[:t]) + _seg_negloglik(seg[t:])
            if best is None or cost1 < best[1]:
                best = (t, cost1)
        if best is None:
            return
        t, cost1 = best
        gain = cost0 - cost1
        penalty = math.log(n)  # BIC, one extra mean parameter
        if gain > penalty:
            change_points.append(lo + t)
            recurse(lo, lo + t)
            recurse(lo + t, hi)

    recurse(0, len(vals))
    return sorted(change_points)


def detect_change_points(train_dates, train_vals, test_dates, test_vals, min_len=5):
    """Run binary segmentation on train_vals; for each change point, report only its
    DATE (mapped from train_dates) plus a persistence boolean computed from an internal
    (never-surfaced) comparison of test-period mean to the pre/post train-segment means."""
    idxs = binary_segmentation(train_vals, min_len=min_len)
    out = []
    for idx in idxs:
        pre = train_vals[:idx]
        post = train_vals[idx:]
        pre_mean = statistics.fmean(pre) if pre else None
        post_mean = statistics.fmean(post) if post else None
        persists = None
        if test_vals and pre_mean is not None and post_mean is not None:
            test_mean = statistics.fmean(test_vals)
            persists = abs(test_mean - post_mean) < abs(test_mean - pre_mean)
        out.append({"date": train_dates[idx], "persists_in_test": persists})
    return out


# --------------------------------------------------------------------------
# Infra-event matching
# --------------------------------------------------------------------------

BACKUP_DATE_RE = re.compile(r"bak-(\d{8})")
GENERIC_DATE_RE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")


def collect_infra_events(infra_versions, infra_models):
    events = []  # list of (date_str, category)
    for v in infra_versions:
        if v["first_seen_date"]:
            events.append((v["first_seen_date"], "cli-version-change"))
    for m in infra_models:
        if m["first_seen_date"]:
            events.append((m["first_seen_date"], "model-change"))

    lanes_dir = os.path.expanduser("~/.instinct/lanes")
    if os.path.isdir(lanes_dir):
        for fn in os.listdir(lanes_dir):
            m = BACKUP_DATE_RE.search(fn)
            if m:
                d = m.group(1)
                events.append((f"{d[0:4]}-{d[4:6]}-{d[6:8]}", "dated-backup"))
        policy_path = os.path.join(lanes_dir, "POLICY.md")
        if os.path.isfile(policy_path):
            try:
                with open(policy_path, "r", errors="replace") as fh:
                    for m in GENERIC_DATE_RE.finditer(fh.read()):
                        events.append((f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "policy-dated-section"))
            except OSError:
                pass

    hooks_dir = os.path.expanduser("~/.claude/hooks")
    if os.path.isdir(hooks_dir):
        for fn in os.listdir(hooks_dir):
            fp = os.path.join(hooks_dir, fn)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(fp), tz=timezone.utc)
                events.append((mtime.astimezone(LOCAL_TZ).date().isoformat(), "hook-file-mtime"))
            except OSError:
                pass

    # de-duplicate identical (date, category) pairs
    return sorted(set(events))


def nearest_infra_event(date_str, events, max_gap_days=3):
    if not date_str:
        return None
    target = datetime.fromisoformat(date_str).date()
    best = None
    for ev_date_str, category in events:
        try:
            ev_date = datetime.fromisoformat(ev_date_str).date()
        except ValueError:
            continue
        gap = abs((target - ev_date).days)
        if gap <= max_gap_days and (best is None or gap < best[0]):
            best = (gap, category, ev_date_str)
    if best is None:
        return None
    return {"gap_days": best[0], "category": best[1], "event_date": best[2]}


# --------------------------------------------------------------------------
# Top-level aggregation
# --------------------------------------------------------------------------

def aggregate(rows, infra):
    total = len(rows)
    by_class = defaultdict(lambda: {"entries": 0, "chars": 0})
    by_class_month = defaultdict(lambda: defaultdict(lambda: {"entries": 0, "chars": 0}))

    human_chars = 0
    human_or_mixed_chars = 0
    human_days = set()
    all_days = set()
    unparsed_ts_rows = 0

    sessions_all = set()
    sessions_by_kind = defaultdict(set)

    third_party_tool_result_count = 0
    has_paste_marker_count = 0
    pasted_agent_draft_count = 0
    pasted_agent_draft_eligible = 0

    for r in rows:
        cls = r["class"]
        by_class[cls]["entries"] += 1
        by_class[cls]["chars"] += r["chars"]
        month = r["month_local"]
        if month:
            by_class_month[month][cls]["entries"] += 1
            by_class_month[month][cls]["chars"] += r["chars"]

        if cls == "human-typed":
            human_chars += r["chars"]
            human_or_mixed_chars += r["chars"]
        elif cls == "human+paste" and r.get("typed_chars") is not None:
            human_or_mixed_chars += r["typed_chars"]

        date = r["date_local"]
        if date:
            all_days.add(date)
            if cls == "human-typed":
                human_days.add(date)
        else:
            unparsed_ts_rows += 1

        if not r["is_subagent_file"] and r["session_id"]:
            sessions_all.add(r["session_id"])
            if r.get("session_kind"):
                sessions_by_kind[r["session_kind"]].add(r["session_id"])

        if r.get("third_party_tool_result"):
            third_party_tool_result_count += 1
        if r.get("has_paste_marker"):
            has_paste_marker_count += 1
        if cls == "human-typed":
            pasted_agent_draft_eligible += 1
            if r.get("pasted_agent_draft"):
                pasted_agent_draft_count += 1

    total_chars = sum(v["chars"] for v in by_class.values())

    shares = {
        "entries_human_typed_strict": (by_class.get("human-typed", {}).get("entries", 0) / total) if total else None,
        "entries_human_typed_or_mixed": (
            (by_class.get("human-typed", {}).get("entries", 0) + by_class.get("human+paste", {}).get("entries", 0)) / total
        ) if total else None,
        "chars_human_typed_strict": (human_chars / total_chars) if total_chars else None,
        "chars_human_typed_or_mixed": (human_or_mixed_chars / total_chars) if total_chars else None,
    }

    # naive vs filtered day-level indicators, ALL DATA (no split)
    naive_by_day_all = build_day_indicator_series(rows, only_human_typed=False)
    filtered_by_day_all = build_day_indicator_series(rows, only_human_typed=True)
    indicator_report_all, share_naive_only_all, naive_days_all, filtered_days_all = \
        indicator_correlation_report(naive_by_day_all, filtered_by_day_all)

    # train/test split: first 70% of days (chronological) that have >=1 human-typed entry
    human_days_sorted = sorted(human_days)
    n_human_days = len(human_days_sorted)
    cutoff_date = None
    if n_human_days >= 2:
        cutoff_idx = max(0, math.ceil(0.7 * n_human_days) - 1)
        cutoff_date = human_days_sorted[cutoff_idx]
    train_rows = [r for r in rows if r["date_local"] and cutoff_date and r["date_local"] <= cutoff_date]
    test_rows = [r for r in rows if r["date_local"] and cutoff_date and r["date_local"] > cutoff_date]

    split_report = {}
    for split_name, split_rows in (("train", train_rows), ("test", test_rows)):
        naive_d = build_day_indicator_series(split_rows, only_human_typed=False)
        filtered_d = build_day_indicator_series(split_rows, only_human_typed=True)
        rep, share_naive_only, n_naive_days, n_filtered_days = indicator_correlation_report(naive_d, filtered_d)
        split_report[split_name] = {
            "indicators": rep,
            "share_days_naive_only": share_naive_only,
            "n_naive_days": n_naive_days,
            "n_filtered_days": n_filtered_days,
        }

    # change-point detection on TRAIN, checked for persistence in TEST, matched to infra events
    infra_events = collect_infra_events(infra["versions"], infra["models"])
    change_point_report = {}
    naive_train = build_day_indicator_series(train_rows, only_human_typed=False)
    filtered_train = build_day_indicator_series(train_rows, only_human_typed=True)
    naive_test = build_day_indicator_series(test_rows, only_human_typed=False)
    filtered_test = build_day_indicator_series(test_rows, only_human_typed=True)
    for series_name, train_map, test_map in (("naive", naive_train, naive_test),
                                              ("filtered", filtered_train, filtered_test)):
        for key in ("late_share", "fragmentation", "mean_log_len"):
            dates_sorted = sorted(train_map)
            vals = [train_map[d][key] for d in dates_sorted if train_map[d][key] is not None]
            dates_used = [d for d in dates_sorted if train_map[d][key] is not None]
            test_dates_sorted = sorted(test_map)
            test_vals = [test_map[d][key] for d in test_dates_sorted if test_map[d][key] is not None]
            cps = detect_change_points(dates_used, vals, test_dates_sorted, test_vals)
            for cp in cps:
                cp["matched_infra_event"] = nearest_infra_event(cp["date"], infra_events)
            change_point_report[f"{series_name}.{key}"] = cps

    n_change_points = sum(len(v) for v in change_point_report.values())
    n_matched = sum(1 for v in change_point_report.values() for cp in v if cp["matched_infra_event"])

    # missingness: days with zero human-typed entries, by weekday and month
    all_days_sorted = sorted(all_days)

    # Base rate: given how dense the infra-event candidate list is, what share of ALL
    # calendar days in the observed range would find SOME matching event within 3 days,
    # regardless of whether anything happened that day? If this is high, an "N/M change
    # points matched" headline is not informative on its own.
    base_rate = None
    if all_days_sorted:
        d0 = datetime.fromisoformat(all_days_sorted[0]).date()
        d1 = datetime.fromisoformat(all_days_sorted[-1]).date()
        total_days = (d1 - d0).days + 1
        if 0 < total_days <= 3660:
            hits = 0
            cur = d0
            for _ in range(total_days):
                if nearest_infra_event(cur.isoformat(), infra_events):
                    hits += 1
                cur += timedelta(days=1)
            base_rate = hits / total_days

    weekday_totals = defaultdict(int)
    weekday_zero_human = defaultdict(int)
    month_totals = defaultdict(int)
    month_zero_human = defaultdict(int)
    for d in all_days_sorted:
        dt = datetime.fromisoformat(d)
        wd = dt.strftime("%A")
        mo = d[:7]
        weekday_totals[wd] += 1
        month_totals[mo] += 1
        if d not in human_days:
            weekday_zero_human[wd] += 1
            month_zero_human[mo] += 1

    # session-level: how much of each naive indicator's mass comes from autonomous sessions
    autonomous_sessions = sessions_by_kind.get("autonomous", set())
    naive_entries_total = sum(1 for r in rows if r["date_local"] and r["hour_local"] is not None)
    naive_entries_autonomous = sum(
        1 for r in rows if r["date_local"] and r["hour_local"] is not None
        and r["session_id"] in autonomous_sessions
    )
    late_entries_total = sum(1 for r in rows if r.get("hour_local") is not None and r["hour_local"] < 5)
    late_entries_autonomous = sum(
        1 for r in rows if r.get("hour_local") is not None and r["hour_local"] < 5
        and r["session_id"] in autonomous_sessions
    )
    frag_pairs_total = set()
    frag_pairs_autonomous = set()
    for r in rows:
        if r["date_local"] and r["hour_local"] is not None and r["session_id"]:
            key = (r["session_id"], r["date_local"], r["hour_local"])
            frag_pairs_total.add(key)
            if r["session_id"] in autonomous_sessions:
                frag_pairs_autonomous.add(key)

    result = {
        "total_user_role_entries": total,
        "by_class": {k: dict(v) for k, v in by_class.items()},
        "by_class_by_month": {m: {k: dict(v) for k, v in cm.items()} for m, cm in sorted(by_class_month.items())},
        "shares": shares,
        "density": {
            "days_with_any_user_role_activity": len(all_days),
            "days_with_any_human_typed_entry": len(human_days),
            "rows_with_unparseable_timestamp": unparsed_ts_rows,
        },
        "sessions": {
            "total_sessions": len(sessions_all),
            "by_kind": {k: len(v) for k, v in sessions_by_kind.items()},
            "share_sessions_fully_autonomous": (
                len(sessions_by_kind.get("autonomous", set())) / len(sessions_all)
            ) if sessions_all else None,
        },
        "indicators_naive_vs_filtered_overall": {
            "report": indicator_report_all,
            "share_days_naive_only": share_naive_only_all,
            "n_naive_days": naive_days_all,
            "n_filtered_days": filtered_days_all,
        },
        "train_test_split": {
            "cutoff_date_local": cutoff_date,
            "n_human_typed_days_total": n_human_days,
            "report": split_report,
        },
        "change_points": {
            "cutoff_date_local": cutoff_date,
            "by_series": change_point_report,
            "total_change_points": n_change_points,
            "matched_to_infra_event": n_matched,
            "base_rate_any_day_matches_within_3_days": base_rate,
        },
        "infra_events": {
            "distinct_versions": len(infra["versions"]),
            "distinct_models": len(infra["models"]),
            "versions": infra["versions"],
            "models": infra["models"],
            "events_considered": len(infra_events),
        },
        "missingness": {
            "by_weekday": {wd: {"total_days": weekday_totals[wd], "zero_human_typed_days": weekday_zero_human[wd]}
                           for wd in weekday_totals},
            "by_month": {mo: {"total_days": month_totals[mo], "zero_human_typed_days": month_zero_human[mo]}
                         for mo in sorted(month_totals)},
        },
        "third_party": {
            "entries_with_paste_marker": has_paste_marker_count,
            "share_entries_with_paste_marker": (has_paste_marker_count / total) if total else None,
            "tool_result_entries_third_party": third_party_tool_result_count,
            "share_tool_result_entries_third_party": (
                third_party_tool_result_count / by_class.get("tool-result", {}).get("entries", 1)
            ) if by_class.get("tool-result", {}).get("entries", 0) else None,
        },
        "pasted_agent_draft": {
            "human_typed_entries_checked": pasted_agent_draft_eligible,
            "flagged": pasted_agent_draft_count,
            "share": (pasted_agent_draft_count / pasted_agent_draft_eligible) if pasted_agent_draft_eligible else None,
        },
        "autonomous_session_contamination": {
            "share_of_naive_entries": (naive_entries_autonomous / naive_entries_total) if naive_entries_total else None,
            "share_of_late_entries": (late_entries_autonomous / late_entries_total) if late_entries_total else None,
            "share_of_fragmentation_session_hours": (
                len(frag_pairs_autonomous) / len(frag_pairs_total)
            ) if frag_pairs_total else None,
        },
        "provenance_field_coverage": None,  # filled in by caller with stats
    }
    return result


# --------------------------------------------------------------------------
# Indicator-4 pilot parameters (spec section 3 / D3): pi_bar, kappa_a, mu_M4 for message length
# (log chars of user-role text), the real, non-inferential authorship metadata sim/drift_sim.py's
# generator reads (constitution II). Lengths only, never text.
# --------------------------------------------------------------------------

def compute_indicator4_params(rows):
    """Over text-bearing (chars > 0) user-role entries, excluding tool-result: 'main_thread'
    excludes sidechain/subagent traffic (class == 'sidechain'); 'with_sidechain' includes it.
    n_human/n_machine split on class == 'human-typed' vs everything else (injected, lane-prompt,
    human+paste, sidechain). pi_bar_entry is the entry-level machine share; pi_bar_daymean/
    pi_day_sd are the mean/population-SD of the per-day machine share, over days with >=1
    text-bearing entry. mu_M4_humanSD is the machine-vs-human mean log-chars gap in units of the
    human series' own population SD; kappa_a is the machine/human population-variance ratio of log
    chars -- both computed only from integer char counts, never from text content.

    day_level_main_thread reports the same two contamination quantities at day granularity;
    see day_level_stats() below for what it computes and how."""
    def scope_stats(scoped_rows):
        text_rows = [r for r in scoped_rows if r["class"] != "tool-result" and r.get("chars", 0) > 0]
        n_text = len(text_rows)
        human_rows = [r for r in text_rows if r["class"] == "human-typed"]
        machine_rows = [r for r in text_rows if r["class"] != "human-typed"]
        n_human, n_machine = len(human_rows), len(machine_rows)
        pi_bar_entry = (n_machine / n_text) if n_text else None

        by_day = defaultdict(lambda: {"total": 0, "machine": 0})
        for r in text_rows:
            d = r.get("date_local")
            if d is None:
                continue
            by_day[d]["total"] += 1
            if r["class"] != "human-typed":
                by_day[d]["machine"] += 1
        day_pis = [v["machine"] / v["total"] for v in by_day.values() if v["total"] > 0]
        n_days = len(day_pis)
        pi_bar_daymean = statistics.fmean(day_pis) if day_pis else None
        pi_day_sd = statistics.pstdev(day_pis) if len(day_pis) > 1 else None

        human_logs = [math.log(r["chars"]) for r in human_rows]
        machine_logs = [math.log(r["chars"]) for r in machine_rows]
        mu_m4_humansd = kappa_a = None
        if len(human_logs) > 1 and len(machine_logs) > 1:
            human_pvar = statistics.pvariance(human_logs)
            machine_pvar = statistics.pvariance(machine_logs)
            human_pstdev = math.sqrt(human_pvar)
            if human_pstdev > 0:
                mu_m4_humansd = (statistics.fmean(machine_logs) - statistics.fmean(human_logs)) / human_pstdev
            if human_pvar > 0:
                kappa_a = machine_pvar / human_pvar
        return {
            "n_text": n_text, "n_human": n_human, "n_machine": n_machine,
            "pi_bar_entry": pi_bar_entry, "pi_bar_daymean": pi_bar_daymean,
            "pi_day_sd": pi_day_sd, "n_days": n_days,
            "mu_M4_humanSD": mu_m4_humansd, "kappa_a": kappa_a,
        }

    def day_level_stats(scoped_rows):
        """Day-granularity contamination summary over the same text-bearing,
        non-tool-result entries as scope_stats, restricted to days that have
        >=1 human-typed AND >=1 non-human entry (n_days_both). h_d/m_d (per-day
        mean log chars of each class) are intermediate only and are never
        written out -- only the cross-day/pooled summary numbers below are."""
        text_rows = [r for r in scoped_rows if r["class"] != "tool-result" and r.get("chars", 0) > 0]
        by_day = defaultdict(lambda: {"human": [], "machine": []})
        for r in text_rows:
            d = r.get("date_local")
            if d is None:
                continue
            bucket = by_day[d]["human"] if r["class"] == "human-typed" else by_day[d]["machine"]
            bucket.append(math.log(r["chars"]))

        days_both = {d: v for d, v in by_day.items() if v["human"] and v["machine"]}
        n_days_both = len(days_both)

        h_d_list, m_d_list, day_pis = [], [], []
        pooled_ss, pooled_n = 0.0, 0
        for v in days_both.values():
            h_logs, m_logs = v["human"], v["machine"]
            h_d_list.append(statistics.fmean(h_logs))
            m_d_list.append(statistics.fmean(m_logs))
            day_pis.append(len(m_logs) / (len(h_logs) + len(m_logs)))
            if len(h_logs) > 1:
                pooled_ss += len(h_logs) * statistics.pvariance(h_logs)
                pooled_n += len(h_logs)

        pi_bar_daymean = statistics.fmean(day_pis) if day_pis else None

        # Mean gap (per-day mean log chars, machine minus human) computed once and shared by
        # both mu_M4_day (normalized by the across-day human SD) and
        # mu_M4_entry_withinday_pooledHumanSD (normalized by the pooled within-day human SD).
        mean_gap = statistics.fmean(m_d_list) - statistics.fmean(h_d_list) if h_d_list else None

        mu_m4_day = kappa_a_day = None
        if n_days_both > 1:
            h_pstdev = statistics.pstdev(h_d_list)
            if h_pstdev > 0:
                mu_m4_day = mean_gap / h_pstdev
            h_pvar_days = statistics.pvariance(h_d_list)
            if h_pvar_days > 0:
                kappa_a_day = statistics.pvariance(m_d_list) / h_pvar_days

        mu_m4_entry_withinday = None
        if pooled_n > 0 and h_d_list:
            pooled_sd = math.sqrt(pooled_ss / pooled_n)
            if pooled_sd > 0:
                mu_m4_entry_withinday = mean_gap / pooled_sd

        return {
            "n_days_both": n_days_both,
            "pi_bar_daymean": pi_bar_daymean,
            "mu_M4_day": mu_m4_day,
            "kappa_a_day": kappa_a_day,
            "mu_M4_entry_withinday_pooledHumanSD": mu_m4_entry_withinday,
        }

    main_rows = [r for r in rows if r["class"] != "sidechain"]
    return {
        "main_thread": scope_stats(main_rows),
        "with_sidechain": scope_stats(rows),
        "day_level_main_thread": day_level_stats(main_rows),
    }


def write_indicator4_params(rows, path=INDICATOR4_PATH):
    params = compute_indicator4_params(rows)
    with open(path, "w") as fh:
        json.dump(params, fh, indent=2)
    return params


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def write_csv(rows, path=CSV_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _fmt(x, pct=False):
    if x is None:
        return "n/a"
    if pct:
        return f"{x:.4f}"
    return f"{x:.4f}"


RULES_TEXT = """\
## Classification rules (exactly as implemented, in priority order)

Only entries with top-level `"type"` in `("user", "assistant")` are read at all; other
entry types (attachments, mode/permission records, etc.) never reach the classifier.
Assistant entries are read ONLY to extract their `text`-type content blocks (for the
pasted-agent-draft check), their `message.model` (an infra identifier), and their
`tool_use` block ids/names (also infra identifiers, not content) -- never anything from
`toolUseResult` or an `origin.body` field, which this script never opens.

For each user-role entry, exactly one class is assigned, checked in this order:

1. **sidechain** -- `isSidechain` is `true`, or the file lives under `subagents/`.
2. **tool-result** -- content contains a `tool_result` block.
3. **provenance override** -- `promptSource == "sdk"` or `turnOrigin == "sdk"` -> `injected`.
   This is the PRIMARY signal where present (Opus review item a); marker rules below are
   the fallback for the entries where these fields are null. Field coverage is reported
   below -- both fields are sparse (`promptSource` non-null on well under 5% of entries
   in this corpus), so this override only ever reclassifies a small slice.
4. **injected** -- `isMeta` is `true`, OR the text contains one of: `<system-reminder>`,
   `<command-name>`, `<command-message>`, `<local-command-stdout>`, `hook success`,
   `<task-notification>`, `Caveat: The messages below were generated`, `[Request interrupted`.
5. **human+paste / injected** -- text contains `<pasted_content`. If well-formed tags can
   be excised and non-paste text remains, class is `human+paste` (`typed_chars`/`pasted_chars`
   recorded, `paste_split_clean = true`). If the tag is malformed but text remains outside
   it, still `human+paste`, split left blank (`paste_split_clean = false`). If nothing
   remains outside the paste, class is `injected` (the whole message is the paste).
6. **lane-prompt** -- the chronologically FIRST pending entry of a session is checked
   against every file under `~/.instinct/lanes/prompts/` by sha256 hash or by `startswith`
   the first 200 stripped characters. In-memory comparison only; nothing from those files
   is ever written out.
7. **human-typed** -- everything else.

### Additional per-row signals (not part of the class, reported as separate shares)
- `has_paste_marker`: whether `<pasted_content` appears anywhere, independent of class.
- `third_party_tool_result`: for `tool-result` rows only, whether the tool_use this result
  answers has a name matching a messaging/calendar/email keyword list (tool NAME only,
  never the result content).
- `pasted_agent_draft`: for `human-typed` rows only, a boolean set if a >=200-char span of
  the entry's text also appears in one of the session's last 5 assistant text turns.
  Computed with an in-memory shingle set (window 200, stride 40); the actual strings are
  discarded immediately after the check. Bounded to the last 5 assistant turns, so an
  overlap with an older turn is missed by construction (documented limitation).
- `session_kind`: `autonomous` (session has no `human-typed`/`human+paste` entry),
  `mixed` (session's first resolved entry was `lane-prompt` but a human later typed into
  it), or `interactive` (session started with a human-typed/paste entry).

### Known failure modes
- Wispr-dictated text is indistinguishable from typed text at this metadata level; both
  land in `human-typed`.
- Messages relayed through a phone bridge or another client are indistinguishable from
  desktop typing here.
- An autonomous lane whose prompt text was never written to `~/.instinct/lanes/prompts/`
  is misclassified as `human-typed`, not `lane-prompt`.
- `"hook success"` is a short, generic phrase; a real human message containing that
  substring would be misclassified as `injected`. No such case was individually checked.
- The lane-prompt check only ever looks at a session's first pending entry.
- Provenance fields (`promptSource`, `turnOrigin`) are null on the large majority of
  entries in this corpus, so the classifier still relies mostly on markers.
- `chars` for `tool-result`/`sidechain` rows includes nested tool_result text; image and
  tool_reference blocks contribute 0 chars regardless of actual payload size.
- **Indicator 5 (negative self-reference, spec section 3 item 5) was not computed.** It
  requires language content analysis, which this metadata-only audit does not do and will
  not do; only indicators 1 (late-activity share), 2 (fragmentation) and 4 (message length)
  are in scope for the corpus pilot (spec section 7).
"""


def render_results_md(agg, stats):
    lines = []
    lines.append("# Corpus pilot: metadata-only trace audit\n")
    lines.append(
        "What was measured: how much of Abhay's own \"user\"-role stream in "
        "`~/.claude/projects/**/*.jsonl` is machine-authored (tool results, injected "
        "system/hook text, lane-launched prompts, subagent traffic) versus typed by him, "
        "how that contamination distorts three naive usage indicators (late-activity "
        "share, session fragmentation, message length) relative to a human-typed-only "
        "filtered version, and whether descriptive change points in those indicators line "
        "up with independently dated agent-infrastructure events (CLI version changes, "
        "model changes, dated config backups, hook file changes). This is spec.md section "
        "7 (D3) plus the section 9 / Stage 2 diligence items: rights/provenance inventory "
        "(see `pilot/INVENTORY.md`), missingness, train/test split, and change-point "
        "attribution. Stage 3 (a real-trace replay demo) is out of scope here and stays "
        "gated on `DECISIONS.md` consent per spec.md section 9.\n"
    )
    lines.append("**No state of any person was estimated.**\n")

    lines.append("## Run stats\n")
    lines.append(f"- Files found under `~/.claude/projects`: {stats['files_found']}")
    lines.append(f"- Files opened: {stats['files_opened']} (failed to open: {stats['files_failed_to_open']})")
    lines.append(f"- Lines read: {stats['lines_read']}")
    lines.append(f"- `user`-role entries parsed: {stats['user_entries']}")
    lines.append(f"- `assistant`-role entries parsed (text/model/tool-name only): {stats['assistant_entries']}")
    lines.append(f"- JSON parse errors (line skipped): {stats['parse_errors']}")
    lines.append(f"- User entries with unparseable/missing timestamp: {stats['unparseable_timestamps']}")
    lines.append(f"- Lane-prompt files loaded: {stats['lane_prompt_files']}")
    cov = stats["provenance_coverage"]
    ue = stats["user_entries"] or 1
    lines.append(
        "- Provenance field coverage (share of user entries non-null): "
        + ", ".join(f"{k}={v}/{stats['user_entries']} ({v/ue:.4f})" for k, v in cov.items())
    )
    lines.append(f"- Elapsed: {stats['elapsed_seconds']:.2f}s\n")

    lines.append(RULES_TEXT)

    lines.append("## Overall class breakdown\n")
    lines.append("| class | entries | share of entries | chars | share of chars |")
    lines.append("|---|---:|---:|---:|---:|")
    total = agg["total_user_role_entries"]
    total_chars = sum(v["chars"] for v in agg["by_class"].values())
    for cls in CLASSES:
        v = agg["by_class"].get(cls, {"entries": 0, "chars": 0})
        e_share = v["entries"] / total if total else 0
        c_share = v["chars"] / total_chars if total_chars else 0
        lines.append(f"| {cls} | {v['entries']} | {e_share:.4f} | {v['chars']} | {c_share:.4f} |")
    lines.append("")

    s = agg["shares"]
    lines.append("### Human-authored share (two definitions, both reported)\n")
    lines.append(f"- Entries, strict (`class == human-typed` only): {_fmt(s['entries_human_typed_strict'])}")
    lines.append(f"- Entries, incl. mixed (`human-typed` + `human+paste`, whole entry): {_fmt(s['entries_human_typed_or_mixed'])}")
    lines.append(f"- Chars, strict: {_fmt(s['chars_human_typed_strict'])}")
    lines.append(f"- Chars, incl. mixed (typed-portion of `human+paste` counted): {_fmt(s['chars_human_typed_or_mixed'])}\n")

    d = agg["density"]
    lines.append("## Data density\n")
    lines.append(f"- Days with any user-role activity: {d['days_with_any_user_role_activity']}")
    lines.append(f"- Days with >=1 human-typed entry: {d['days_with_any_human_typed_entry']}")
    lines.append(f"- Rows with unparseable timestamp (excluded from day-level stats): {d['rows_with_unparseable_timestamp']}\n")

    sess = agg["sessions"]
    lines.append("## Sessions\n")
    lines.append(f"- Total sessions (main, non-subagent-file): {sess['total_sessions']}")
    lines.append(f"- By kind: {sess['by_kind']}")
    lines.append(f"- Share fully autonomous: {_fmt(sess['share_sessions_fully_autonomous'])}\n")

    ac = agg["autonomous_session_contamination"]
    lines.append("### Autonomous-session contribution to the NAIVE indicators\n")
    lines.append(f"- Share of naive (all user-role) entries belonging to autonomous sessions: {_fmt(ac['share_of_naive_entries'])}")
    lines.append(f"- Share of late-activity (00:00-05:00) entries from autonomous sessions: {_fmt(ac['share_of_late_entries'])}")
    lines.append(f"- Share of (session, active-hour) fragmentation units from autonomous sessions: {_fmt(ac['share_of_fragmentation_session_hours'])}\n")

    lines.append("## Per-month class breakdown\n")
    lines.append("| month | class | entries | chars |")
    lines.append("|---|---|---:|---:|")
    for month, classes in agg["by_class_by_month"].items():
        for cls in CLASSES:
            v = classes.get(cls)
            if v:
                lines.append(f"| {month} | {cls} | {v['entries']} | {v['chars']} |")
    lines.append("")

    lines.append("## Third-party content indicators (structural, estimate only)\n")
    tp = agg["third_party"]
    lines.append(f"- Share of user-role entries carrying a `<pasted_content` marker: {_fmt(tp['share_entries_with_paste_marker'])}")
    lines.append(f"- Share of tool-result entries whose tool name matches a messaging/calendar/email keyword: {_fmt(tp['share_tool_result_entries_third_party'])}")
    lines.append("  (tool-name keyword match only; result content was never read; this is a coarse estimate, not a count of actual third-party persons.)\n")

    pad = agg["pasted_agent_draft"]
    lines.append("## Pasted-agent-draft overlap (human-typed entries only)\n")
    lines.append(f"- human-typed entries checked: {pad['human_typed_entries_checked']}")
    lines.append(f"- flagged (>=200-char span shared with one of the session's last 5 assistant turns): {pad['flagged']}")
    lines.append(f"- share: {_fmt(pad['share'])}\n")

    lines.append(
        "## Naive vs filtered indicators -- CONTAMINATION only (overall, all data)\n\n"
        "Per Opus review item (f): only naive distributions, naive-vs-filtered "
        "correlation and mean absolute difference are reported here. Filtered-series "
        "level statistics (e.g. mean late-activity share of human-typed entries alone) "
        "are deliberately omitted because a level of the human-typed-only series is the "
        "closest thing in this pipeline to a behavioral signal, and reporting it monthly "
        "or per-split would work as a state proxy, which the constitution forbids without "
        "recorded consent. Naive = ALL user-role entries that day. Filtered = "
        "`human-typed` entries only that day. late_share = share of entries with local "
        f"hour in [0,5). fragmentation = mean over active local hours of distinct "
        "sessions active in that hour. mean_log_len = mean of ln(1+chars). Local time "
        f"zone: {LOCAL_TZ_NAME}.\n"
    )
    rep = agg["indicators_naive_vs_filtered_overall"]["report"]
    for key, r in rep.items():
        nd = r["naive_distribution"]
        lines.append(f"### {key}")
        lines.append(f"- naive distribution: n={nd['n']}, mean={_fmt(nd['mean'])}, median={_fmt(nd['median'])}, IQR={_fmt(nd['iqr'])}")
        lines.append(f"- filtered series length (days with data, no levels reported): {r['filtered_distribution_n_only']}")
        lines.append(f"- paired days: {r['n_paired_days']}")
        lines.append(f"- correlation(naive, filtered): {_fmt(r['correlation_naive_vs_filtered'])}")
        lines.append(f"- mean absolute difference (naive - filtered): {_fmt(r['mean_abs_difference'])}\n")
    ov = agg["indicators_naive_vs_filtered_overall"]
    lines.append(
        f"- Days where naive has data but filtered has none: {_fmt(ov['share_days_naive_only'])} "
        f"of {ov['n_naive_days']} naive-active days ({ov['n_filtered_days']} days have >=1 human-typed entry).\n"
    )

    tt = agg["train_test_split"]
    lines.append("## Train / test split\n")
    lines.append(
        f"Cutoff: first 70% of days-with->=1-human-typed-entry (chronological), "
        f"{tt['n_human_typed_days_total']} such days total, cutoff date "
        f"{tt['cutoff_date_local']}. All days <= cutoff are train, all days after are test.\n"
    )
    for split_name in ("train", "test"):
        srep = tt["report"].get(split_name, {})
        lines.append(f"### {split_name}")
        lines.append(f"- naive-active days: {srep.get('n_naive_days')}, human-typed days: {srep.get('n_filtered_days')}")
        lines.append(f"- days where naive has data but filtered has none: {_fmt(srep.get('share_days_naive_only'))}")
        for key, r in srep.get("indicators", {}).items():
            lines.append(
                f"  - {key}: correlation(naive,filtered)={_fmt(r['correlation_naive_vs_filtered'])}, "
                f"mean_abs_diff={_fmt(r['mean_abs_difference'])}, paired_days={r['n_paired_days']}"
            )
        lines.append("")

    cps = agg["change_points"]
    lines.append("## Descriptive change points vs. dated agent-infrastructure events\n")
    lines.append(
        "Change points are detected on TRAIN only (penalized binary segmentation on the "
        "mean, BIC penalty, stdlib only) for each of the 3 indicators x {naive, filtered}. "
        "Per item (f), only DATES and infra-match are reported -- never the pre/post "
        "segment means or levels. Persistence in test is reported as a boolean derived "
        "internally from a comparison of the test-period mean to the pre/post train means; "
        "the means themselves are not surfaced. **A change point with no matched infra "
        "event is a usage-pattern finding only -- it is not, and must not be read as, "
        "evidence of any change in Abhay's mental or physical state.**\n"
    )
    lines.append(f"- Total change points detected (train, all series): {cps['total_change_points']}")
    lines.append(f"- Matched to a dated infra event within 3 days: {cps['matched_to_infra_event']}")
    br = cps.get("base_rate_any_day_matches_within_3_days")
    lines.append(
        f"- **Base rate**: over every calendar day in the observed range (not just change-point "
        f"days), {_fmt(br)} of days already have SOME infra-event candidate within 3 days, purely "
        "because the candidate list (CLI versions, model ids, dated backups, POLICY.md dates, hook "
        "mtimes) is dense relative to the ~1-month observation window. **A match rate at or near "
        "this base rate is not informative** -- it does not show that a specific change point was "
        "caused by a specific infra event, only that infra events are common enough that most dates "
        "land near one. Read the table below as a candidate-event lookup, not as confirmed "
        "attribution.\n"
    )
    lines.append("| series | date | matched infra event | gap (days) | persists in test |")
    lines.append("|---|---|---|---:|---|")
    for series_key, cp_list in cps["by_series"].items():
        for cp in cp_list:
            m = cp["matched_infra_event"]
            if m:
                lines.append(f"| {series_key} | {cp['date']} | {m['category']} ({m['event_date']}) | {m['gap_days']} | {cp['persists_in_test']} |")
            else:
                lines.append(f"| {series_key} | {cp['date']} | none within 3 days | n/a | {cp['persists_in_test']} |")
    lines.append("")

    ie = agg["infra_events"]
    lines.append("## Agent-infrastructure events considered\n")
    lines.append(f"- Distinct CLI `version` values seen: {ie['distinct_versions']}")
    lines.append(f"- Distinct `message.model` values seen: {ie['distinct_models']}")
    lines.append(f"- Total dated infra-event candidates (versions + models + dated backups + POLICY.md dates + hook mtimes): {ie['events_considered']}\n")

    miss = agg["missingness"]
    lines.append("## Missingness (days with zero human-typed entries)\n")
    lines.append("### By weekday\n")
    lines.append("| weekday | total days | zero-human-typed days | share |")
    lines.append("|---|---:|---:|---:|")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for wd in weekday_order:
        v = miss["by_weekday"].get(wd)
        if v:
            share = v["zero_human_typed_days"] / v["total_days"] if v["total_days"] else None
            lines.append(f"| {wd} | {v['total_days']} | {v['zero_human_typed_days']} | {_fmt(share)} |")
    lines.append("\n### By month\n")
    lines.append("| month | total days | zero-human-typed days | share |")
    lines.append("|---|---:|---:|---:|")
    for mo, v in miss["by_month"].items():
        share = v["zero_human_typed_days"] / v["total_days"] if v["total_days"] else None
        lines.append(f"| {mo} | {v['total_days']} | {v['zero_human_typed_days']} | {_fmt(share)} |")
    lines.append("")

    lines.append(
        "## Scope note\n\n"
        "This pilot reads `user`-role entries fully, and `assistant`-role entries only for "
        "text overlap / model-id / tool-name metadata. It makes no claim about assistant "
        "prose content, and it does not estimate mood, wellbeing, or any "
        "other state of any person. Dictated text (Wispr) is indistinguishable from typed "
        "text at this metadata level -- see known failure modes above. Indicator 5 "
        "(negative self-reference) was not computed; it requires language content analysis "
        "that this metadata-only audit does not perform. **No state of any person was "
        "estimated.**\n"
    )
    return "\n".join(lines)


# --------------------------------------------------------------------------
# --check mode: classifier self-test on synthetic, in-memory data only.
# --------------------------------------------------------------------------

def run_check():
    failures = []

    def expect(label, cond):
        if not cond:
            failures.append(label)

    t, *_ = classify_terminal(False, True, False, False, "hello there")
    expect("sidechain via isSidechain", t == "sidechain")

    t, *_ = classify_terminal(True, False, False, True, "irrelevant")
    expect("sidechain via subagent file overrides tool-result", t == "sidechain")

    text, chars, has_tr = extract_text_and_chars([{"type": "tool_result", "content": "some output"}])
    expect("tool_result block detected", has_tr is True)
    t, *_ = classify_terminal(False, False, False, has_tr, text)
    expect("tool-result classification", t == "tool-result")

    t, *_ = classify_terminal(False, False, False, False, "typed by hand", prompt_source="sdk")
    expect("provenance sdk override -> injected", t == "injected")
    t, *_ = classify_terminal(False, False, False, False, "typed by hand", turn_origin="sdk")
    expect("provenance turnOrigin sdk override -> injected", t == "injected")

    t, *_ = classify_terminal(False, False, True, False, "anything")
    expect("injected via isMeta", t == "injected")

    t, *_ = classify_terminal(False, False, False, False, "prelude <system-reminder>stuff</system-reminder>")
    expect("injected via marker", t == "injected")

    pure_paste = "<pasted_content>some long block of pasted text</pasted_content>"
    t, *_ = classify_terminal(False, False, False, False, pure_paste)
    expect("pure paste -> injected", t == "injected")

    mixed = "please look at this: <pasted_content>PASTED BLOB HERE</pasted_content> what do you think?"
    t, typed_chars, pasted_chars, clean, reason = classify_terminal(False, False, False, False, mixed)
    expect("mixed paste -> human+paste", t == "human+paste")
    expect("mixed paste clean split flag", clean is True)
    expect("mixed paste typed_chars > 0", typed_chars is not None and typed_chars > 0)
    expect("mixed paste pasted_chars > 0", pasted_chars is not None and pasted_chars > 0)

    malformed = "some real typed text <pasted_content>never closed"
    t, typed_chars, pasted_chars, clean, reason = classify_terminal(False, False, False, False, malformed)
    expect("malformed paste with prefix -> human+paste", t == "human+paste")
    expect("malformed paste split flag is False", clean is False)
    expect("malformed paste leaves typed_chars blank", typed_chars is None)

    fake_hashes, fake_prefixes = set(), set()
    lane_text = "Run the nightly sweep and report back."
    fake_hashes.add(hashlib.sha256(lane_text.strip().encode("utf-8")).hexdigest())
    pending = [
        {"session_id": "S1", "timestamp_utc": "2026-01-01T00:00:00+00:00", "_line_idx": 1,
         "_text_stripped": lane_text, "chars": len(lane_text)},
        {"session_id": "S1", "timestamp_utc": "2026-01-01T00:05:00+00:00", "_line_idx": 2,
         "_text_stripped": lane_text, "chars": len(lane_text)},
        {"session_id": "S2", "timestamp_utc": "2026-01-01T00:00:00+00:00", "_line_idx": 3,
         "_text_stripped": "hey can you help me debug this thing", "chars": 37},
    ]
    resolve_pending(pending, fake_hashes, fake_prefixes)
    by_idx = {r["_line_idx"]: r for r in pending}
    expect("session S1 first msg -> lane-prompt", by_idx[1]["class"] == "lane-prompt")
    expect("session S1 second msg (same text) -> human-typed, not lane-prompt", by_idx[2]["class"] == "human-typed")
    expect("session S2 first msg, no match -> human-typed", by_idx[3]["class"] == "human-typed")

    prefix_hashes, prefix_prefixes = set(), set()
    long_prompt = "AUTONOMOUS LANE PREAMBLE " + ("x" * 300)
    prefix_prefixes.add(long_prompt.strip()[:LANE_PREFIX_LEN])
    expect("prefix match works", matches_lane_prompt(long_prompt + " and then some extra local text", prefix_hashes, prefix_prefixes))
    expect("prefix match rejects unrelated text", not matches_lane_prompt("totally unrelated text", prefix_hashes, prefix_prefixes))

    text, chars, has_tr = extract_text_and_chars("plain string content")
    expect("string content chars", chars == len("plain string content"))
    expect("string content no tool_result", has_tr is False)

    text, chars, has_tr = extract_text_and_chars([{"type": "text", "text": "hello"}, {"type": "image", "source": "ignored"}])
    expect("text+image: only text counted", chars == len("hello"))

    text, chars, has_tr = extract_text_and_chars([
        {"type": "tool_result", "content": [{"type": "text", "text": "abc"}, {"type": "image", "source": "x"}]}
    ])
    expect("nested tool_result content walked", chars == len("abc"))
    expect("nested tool_result flag set", has_tr is True)

    # pasted-agent-draft overlap (shingle stride is 40, so align the shared span on a
    # stride boundary in both the assistant buffer and the user text to guarantee a hit)
    assistant_texts = ["The quick brown fox jumps over the lazy dog. " * 10]
    shared_span = assistant_texts[0][0:200]
    prefix = "X" * 40
    expect("pasted-draft overlap detected", compute_pasted_overlap(prefix + shared_span, assistant_texts))
    expect("pasted-draft overlap absent for unrelated text", not compute_pasted_overlap("nothing at all like it, just typing along here" * 5, assistant_texts))

    # binary segmentation sanity: obvious mean shift should be detected
    series = [1.0] * 15 + [10.0] * 15
    cps = binary_segmentation(series, min_len=5)
    expect("change point detected near true break", any(13 <= c <= 17 for c in cps))

    if failures:
        print("CHECK FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("CHECK PASSED (18 scenario groups, 0 failures)")
    return 0


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run classifier self-test on synthetic data and exit")
    parser.add_argument("--until", help="keep entries with timestamp_utc <= this ISO time (reproduces a frozen snapshot)")
    args = parser.parse_args()

    if args.check:
        sys.exit(run_check())

    rows, stats, infra = run_audit()
    if args.until:
        rows = [r for r in rows if r["timestamp_utc"] and r["timestamp_utc"] <= args.until]
        stats["until"] = args.until
    write_csv(rows)
    agg = aggregate(rows, infra)
    agg["provenance_field_coverage"] = stats["provenance_coverage"]

    os.makedirs(PILOT_DIR, exist_ok=True)
    with open(JSON_PATH, "w") as fh:
        json.dump({"stats": stats, "aggregates": agg}, fh, indent=2)

    md = render_results_md(agg, stats)
    with open(MD_PATH, "w") as fh:
        fh.write(md)

    ind4 = write_indicator4_params(rows)

    print(f"files_found={stats['files_found']} files_opened={stats['files_opened']} "
          f"lines_read={stats['lines_read']} user_entries={stats['user_entries']} "
          f"assistant_entries={stats['assistant_entries']} parse_errors={stats['parse_errors']} "
          f"elapsed={stats['elapsed_seconds']:.2f}s")
    print(f"wrote {CSV_PATH} ({len(rows)} rows)")
    print(f"wrote {JSON_PATH}")
    print(f"wrote {INDICATOR4_PATH}: {ind4}")
    print(f"wrote {MD_PATH}")


if __name__ == "__main__":
    main()
