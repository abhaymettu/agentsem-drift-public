# Rights / provenance inventory

Per spec.md section 9, Stage 2 item (a): for every surface Abhay controls, what exists, its date range, who authored it, whether third-party content is present, and whether it is usable for research without other people's permission. Metadata only -- no note, message, or commit body was opened to produce this document. No network or MCP call was made; connector-only surfaces are listed as such, not inventoried.

## Claude Code transcripts

- Path: `~/.claude/projects`
- Approx. count: 75145 user-role + 125875 assistant-role entries, across 1544 sessions
- Date range: 24 distinct local calendar days of activity (see pilot/RESULTS.md for the full breakdown)
- Authored by: him (typed turns), the agent (assistant turns, tool results), and automated lanes/subagents (a large majority of 'user'-role entries in this corpus are tool-results or subagent/sidechain traffic, not typed text -- see pilot/RESULTS.md).
- Third-party content: present, low-share estimate. 0.0030 of user-role entries carry a pasted-content marker (mostly full-message pastes, not mixed with typed prose -- see pilot/RESULTS.md), and 0.0077 of tool-result entries come from a tool whose name matches a messaging/calendar/email keyword (tool name only; result content was never read). This is a coarse structural estimate, not a count of actual other people.
- Usable for research on his own usage metadata without others' permission: yes, at the metadata level this audit operates on. Any content-level use (e.g. reading the text of a pasted email) would need those spans excluded or separately cleared.

## Obsidian vault

- Path: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Brain`
- Exists: True
- Approx. count (`.md` files): 2148
- Date range (file mtimes): 2023-01-05 to 2026-09-28
- Authored by: him (personal notes, second-brain captures via the `brain-capture` skill).
- Third-party content: unknown from metadata alone -- not inspected here. Likely present in some notes (e.g. quoting a meeting or a message) but not counted; a content-level pass would be needed before any release.
- Usable for research on file counts/dates/structure without others' permission: yes. Usable at the content level: not established by this inventory.

## ~/.remember

- Path: `~/.remember`
- Exists: True
- Approx. count (all files): 241
- Date range (file mtimes): 2026-07-23 to 2026-09-28
- Authored by: him and the agent (a Claude memory-plugin store).
- Third-party content: unknown from metadata alone -- not inspected.
- Usable for research on counts/dates without others' permission: yes.

## git repos under ~/code

- Repos found (have a `.git` dir): 69
- Repos with commit history read: 66
- Total commits (all branches, all repos): 11365
- Date range (author dates): 2025-06-05 to 2026-09-27
- Distinct author emails across all repos: 408
- Repos with a small number (<=5) of non-owner commit author emails -- plausible personal collaborators, worth a manual look before any use beyond his own metadata: abhaymettu-site (4 non-owner author(s), emails not listed); abhaymettu.github.io (4 non-owner author(s), emails not listed); agentsem-trap-world (1 non-owner author(s), emails not listed); atlas (2 non-owner author(s), emails not listed); fastbrowse (2 non-owner author(s), emails not listed); mirofish-quant-psych (1 non-owner author(s), emails not listed); osf-mcp-server (1 non-owner author(s), emails not listed); patchbay (1 non-owner author(s), emails not listed); perch (1 non-owner author(s), emails not listed); strafe (1 non-owner author(s), emails not listed); tradingagents-scout (1 non-owner author(s), emails not listed)
- Repos with a large number of distinct non-owner author emails (almost certainly a cloned/forked external project's own upstream history, not personal collaboration data -- author counts only, no emails listed): Search (44 distinct authors); career-ops (199 distinct authors); firstmate (93 distinct authors); job-pipeline (64 distinct authors)
- Authored by: him, for the repos with no or few non-owner authors (commit metadata only was read, never diffs or commit message bodies). The 'large number of authors' repos above are external/forked projects, authored by their upstream contributors, not personal data about people he knows.
- Usable for research on commit counts/dates/authorship without others' permission: yes, for the repos where he is the sole or near-sole author, and for the external-project repos (public upstream OSS history). The small-collaborator repos should get a manual look before any use beyond his own metadata.

## ~/.instinct/lanes

- Manifest: `~/.instinct/lanes/manifest.json`, top-level entries: 1
- Prompts dir: `~/.instinct/lanes/prompts`, `.txt` file count: 334, date range (mtimes): 2026-09-11 to 2026-09-20
- Authored by: him (lane configuration) and agents (persisted lane prompts, written verbatim, never reconstructed from memory, per lane policy).
- Third-party content: none expected (infrastructure/tooling config, not personal correspondence).
- Usable for research (as infra metadata) without others' permission: yes.

## Connector-only surfaces (not inventoried)

Per instruction, no MCP or network call was made to produce this inventory. The following surfaces are only reachable through a connector and are listed here as **connector-only, not inventoried**, not as "absent":

- Google Calendar (via the Google Calendar MCP connector)
- Gmail (via the Gmail MCP connector)
- Wispr Flow dictation/meeting notes (via the wisprflow / wispr-flow-write MCP connectors)
- Any messaging relay (iMessage/SMS/Slack/etc.) reachable only through an MCP tool, not a local file

## Summary judgment

The Claude Code transcripts are the surface with the most directly relevant third-party-content risk for this project, quantified here via structural markers only (not content review); the estimated share is small (well under 1% of entries by either marker). The Obsidian vault and `~/.remember` were not content-inspected and should not be treated as cleared for anything beyond count/date-level use until a content-level pass is done. Git history under `~/code` does show many non-owner commit authors, but essentially all of them sit in repos with more than 5 distinct outside authors -- i.e. cloned/forked external projects' own public upstream history, not personal collaboration data; any repo with <= 5 outside authors is called out by name above for a manual look. No calendar, email, or messaging-relay data was read. **No state of any person was estimated in producing this inventory.**
