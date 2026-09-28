# Corpus pilot: metadata-only trace audit

What was measured: how much of Abhay's own "user"-role stream in `~/.claude/projects/**/*.jsonl` is machine-authored (tool results, injected system/hook text, lane-launched prompts, subagent traffic) versus typed by him, how that contamination distorts three naive usage indicators (late-activity share, session fragmentation, message length) relative to a human-typed-only filtered version, and whether descriptive change points in those indicators line up with independently dated agent-infrastructure events (CLI version changes, model changes, dated config backups, hook file changes). This is spec.md section 7 (D3) plus the section 9 / Stage 2 diligence items: rights/provenance inventory (see `pilot/INVENTORY.md`), missingness, train/test split, and change-point attribution. Stage 3 (a real-trace replay demo) is out of scope here and stays gated on `DECISIONS.md` consent per spec.md section 9.

**No state of any person was estimated.**

## Run stats

- Files found under `~/.claude/projects`: 2315
- Files opened: 2314 (failed to open: 1)
- Lines read: 582899
- `user`-role entries parsed: 76359
- `assistant`-role entries parsed (text/model/tool-name only): 127967
- JSON parse errors (line skipped): 0
- User entries with unparseable/missing timestamp: 0
- Lane-prompt files loaded: 326
- Provenance field coverage (share of user entries non-null): promptSource=3433/76359 (0.0450), turnOrigin=1644/76359 (0.0215), entrypoint=76359/76359 (1.0000), userType=76359/76359 (1.0000)
- Elapsed: 9.10s

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

## Overall class breakdown

| class | entries | share of entries | chars | share of chars |
|---|---:|---:|---:|---:|
| tool-result | 48432 | 0.6549 | 95562804 | 0.5504 |
| injected | 5249 | 0.0710 | 15772484 | 0.0908 |
| lane-prompt | 217 | 0.0029 | 624173 | 0.0036 |
| sidechain | 19369 | 0.2619 | 59164952 | 0.3408 |
| human-typed | 688 | 0.0093 | 2501542 | 0.0144 |
| human+paste | 0 | 0.0000 | 0 | 0.0000 |

### Human-authored share (two definitions, both reported)

- Entries, strict (`class == human-typed` only): 0.0093
- Entries, incl. mixed (`human-typed` + `human+paste`, whole entry): 0.0093
- Chars, strict: 0.0144
- Chars, incl. mixed (typed-portion of `human+paste` counted): 0.0144

## Data density

- Days with any user-role activity: 24
- Days with >=1 human-typed entry: 21
- Rows with unparseable timestamp (excluded from day-level stats): 0

## Sessions

- Total sessions (main, non-subagent-file): 1544
- By kind: {'autonomous': 1303, 'mixed': 20, 'interactive': 221}
- Share fully autonomous: 0.8439

### Autonomous-session contribution to the NAIVE indicators

- Share of naive (all user-role) entries belonging to autonomous sessions: 0.5701
- Share of late-activity (00:00-05:00) entries from autonomous sessions: 0.7497
- Share of (session, active-hour) fragmentation units from autonomous sessions: 0.7462

## Per-month class breakdown

| month | class | entries | chars |
|---|---|---:|---:|
| 2026-08 | tool-result | 61 | 93426 |
| 2026-08 | injected | 20 | 337525 |
| 2026-08 | human-typed | 1 | 16714 |
| 2026-09 | tool-result | 48371 | 95469378 |
| 2026-09 | injected | 5229 | 15434959 |
| 2026-09 | lane-prompt | 217 | 624173 |
| 2026-09 | sidechain | 19369 | 59164952 |
| 2026-09 | human-typed | 687 | 2484828 |

## Third-party content indicators (structural, estimate only)

- Share of user-role entries carrying a `<pasted_content` marker: 0.0030
- Share of tool-result entries whose tool name matches a messaging/calendar/email keyword: 0.0077
  (tool-name keyword match only; result content was never read; this is a coarse estimate, not a count of actual third-party persons.)

## Pasted-agent-draft overlap (human-typed entries only)

- human-typed entries checked: 688
- flagged (>=200-char span shared with one of the session's last 5 assistant turns): 0
- share: 0.0000

## Naive vs filtered indicators -- CONTAMINATION only (overall, all data)

Per Opus review item (f): only naive distributions, naive-vs-filtered correlation and mean absolute difference are reported here. Filtered-series level statistics (e.g. mean late-activity share of human-typed entries alone) are deliberately omitted because a level of the human-typed-only series is the closest thing in this pipeline to a behavioral signal, and reporting it monthly or per-split would work as a state proxy, which the constitution forbids without recorded consent. Naive = ALL user-role entries that day. Filtered = `human-typed` entries only that day. late_share = share of entries with local hour in [0,5). fragmentation = mean over active local hours of distinct sessions active in that hour. mean_log_len = mean of ln(1+chars). Local time zone: America/Chicago.

### late_share
- naive distribution: n=24, mean=0.1435, median=0.1012, IQR=0.2006
- filtered series length (days with data, no levels reported): 21
- paired days: 21
- correlation(naive, filtered): 0.9025
- mean absolute difference (naive - filtered): 0.0813

### fragmentation
- naive distribution: n=24, mean=4.3584, median=3.5446, IQR=1.9941
- filtered series length (days with data, no levels reported): 21
- paired days: 21
- correlation(naive, filtered): 0.1169
- mean absolute difference (naive - filtered): 2.6224

### mean_log_len
- naive distribution: n=24, mean=6.1649, median=6.1971, IQR=0.3852
- filtered series length (days with data, no levels reported): 21
- paired days: 21
- correlation(naive, filtered): 0.2836
- mean absolute difference (naive - filtered): 1.2098

- Days where naive has data but filtered has none: 0.1250 of 24 naive-active days (21 days have >=1 human-typed entry).

## Middle-series indicators -- CONTAMINATION only (overall, all data)

Referee round 2: a third series between naive and filtered. middle = user-role entries MINUS tool-result and sidechain entries (injected and lane-prompt entries are kept, unlike in the filtered series). Reported as contamination quantities only -- correlation and mean absolute difference -- no levels, no per-day series. Days with middle-series data: 24.

### late_share
- naive vs middle: correlation=0.9365, mean_abs_diff=0.0445, paired_days=24
- middle vs filtered: correlation=0.9007, mean_abs_diff=0.0778, paired_days=21

### fragmentation
- naive vs middle: correlation=0.9995, mean_abs_diff=0.0756, paired_days=24
- middle vs filtered: correlation=0.1100, mean_abs_diff=2.5853, paired_days=21

### mean_log_len
- naive vs middle: correlation=-0.0173, mean_abs_diff=0.7740, paired_days=24
- middle vs filtered: correlation=0.2436, mean_abs_diff=1.2677, paired_days=21

## Train / test split

Cutoff: first 70% of days-with->=1-human-typed-entry (chronological), 21 such days total, cutoff date 2026-09-21. All days <= cutoff are train, all days after are test.

### train
- naive-active days: 18, human-typed days: 15
- days where naive has data but filtered has none: 0.1667
  - late_share: correlation(naive,filtered)=0.9368, mean_abs_diff=0.0740, paired_days=15
  - fragmentation: correlation(naive,filtered)=0.1533, mean_abs_diff=2.7290, paired_days=15
  - mean_log_len: correlation(naive,filtered)=0.3775, mean_abs_diff=1.3357, paired_days=15

### test
- naive-active days: 6, human-typed days: 6
- days where naive has data but filtered has none: 0.0000
  - late_share: correlation(naive,filtered)=0.9045, mean_abs_diff=0.0996, paired_days=6
  - fragmentation: correlation(naive,filtered)=-0.3025, mean_abs_diff=2.3557, paired_days=6
  - mean_log_len: correlation(naive,filtered)=0.7770, mean_abs_diff=0.8952, paired_days=6

## Descriptive change points vs. dated agent-infrastructure events

Change points are detected on TRAIN only (penalized binary segmentation on the mean, BIC penalty, stdlib only) for each of the 3 indicators x {naive, filtered}. Per item (f), only DATES and infra-match are reported -- never the pre/post segment means or levels. Persistence in test is reported as a boolean derived internally from a comparison of the test-period mean to the pre/post train means; the means themselves are not surfaced. **A change point with no matched infra event is a usage-pattern finding only -- it is not, and must not be read as, evidence of any change in Abhay's mental or physical state.**

- Total change points detected (train, all series): 8
- Matched to a dated infra event within 3 days: 8
- **Base rate**: over every calendar day in the observed range (not just change-point days), 1.0000 of days already have SOME infra-event candidate within 3 days, purely because the candidate list (CLI versions, model ids, dated backups, POLICY.md dates, hook mtimes) is dense relative to the ~1-month observation window. **A match rate at or near this base rate is not informative** -- it does not show that a specific change point was caused by a specific infra event, only that infra events are common enough that most dates land near one. Read the table below as a candidate-event lookup, not as confirmed attribution.

| series | date | matched infra event | gap (days) | persists in test |
|---|---|---|---:|---|
| naive.late_share | 2026-09-10 | policy-dated-section (2026-09-10) | 0 | True |
| naive.fragmentation | 2026-09-10 | policy-dated-section (2026-09-10) | 0 | True |
| naive.fragmentation | 2026-09-15 | dated-backup (2026-09-16) | 1 | False |
| naive.mean_log_len | 2026-09-09 | model-change (2026-09-09) | 0 | False |
| filtered.late_share | 2026-09-10 | policy-dated-section (2026-09-10) | 0 | False |
| filtered.fragmentation | 2026-09-11 | dated-backup (2026-09-11) | 0 | True |
| filtered.mean_log_len | 2026-09-09 | model-change (2026-09-09) | 0 | True |
| filtered.mean_log_len | 2026-09-17 | dated-backup (2026-09-16) | 1 | True |

## Agent-infrastructure events considered

- Distinct CLI `version` values seen: 7
- Distinct `message.model` values seen: 10
- Total dated infra-event candidates (versions + models + dated backups + POLICY.md dates + hook mtimes): 27

## Missingness (days with zero human-typed entries)

### By weekday

| weekday | total days | zero-human-typed days | share |
|---|---:|---:|---:|
| Monday | 3 | 1 | 0.3333 |
| Tuesday | 4 | 1 | 0.2500 |
| Wednesday | 4 | 1 | 0.2500 |
| Thursday | 3 | 0 | 0.0000 |
| Friday | 3 | 0 | 0.0000 |
| Saturday | 3 | 0 | 0.0000 |
| Sunday | 4 | 0 | 0.0000 |

### By month

| month | total days | zero-human-typed days | share |
|---|---:|---:|---:|
| 2026-08 | 1 | 0 | 0.0000 |
| 2026-09 | 23 | 3 | 0.1304 |

## Scope note

This pilot reads `user`-role entries fully, and `assistant`-role entries only for text overlap / model-id / tool-name metadata. It makes no claim about assistant prose content, and it does not estimate mood, wellbeing, or any other state of any person. Dictated text (Wispr) is indistinguishable from typed text at this metadata level -- see known failure modes above. Indicator 5 (negative self-reference) was not computed; it requires language content analysis that this metadata-only audit does not perform. **No state of any person was estimated.**
