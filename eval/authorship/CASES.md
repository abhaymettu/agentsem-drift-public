# Authorship-filter eval cases (review surface)

Generated from `cases.jsonl` (the source of truth). 54 synthetic user-role entries: 27 `human`, 27 `agent`.
Labels were assigned by the eval builder (Claude), not by a person and not by the model under test; they need
Abhay's read before a baseline number is trusted. `test` rows are held out for hillclimb.

| id | subclass | label | split |
|---|---|---|---|
| ht01 | human-typed | human | train |
| ht02 | human-typed | human | train |
| ht03 | human-typed | human | test |
| ht04 | human-typed | human | train |
| ht05 | human-typed | human | train |
| ht06 | human-typed | human | test |
| ht07 | human-typed | human | train |
| ht08 | human-typed | human | test |
| ht09 | human-typed | human | train |
| ht10 | human-typed | human | test |
| hd01 | human-dictated | human | test |
| hd02 | human-dictated | human | train |
| hd03 | human-dictated | human | train |
| hd04 | human-dictated | human | train |
| hd05 | human-dictated | human | test |
| hd06 | human-dictated | human | train |
| hd07 | human-dictated | human | test |
| hd08 | human-dictated | human | train |
| hd09 | human-dictated | human | test |
| hq01 | human-quoting | human | train |
| hq02 | human-quoting | human | train |
| hq03 | human-quoting | human | test |
| hq04 | human-quoting | human | train |
| hq05 | human-quoting | human | test |
| hq06 | human-quoting | human | test |
| hq07 | human-quoting | human | train |
| hq08 | human-quoting | human | train |
| ap01 | agent-pasted | agent | test |
| ap02 | agent-pasted | agent | test |
| ap03 | agent-pasted | agent | train |
| ap04 | agent-pasted | agent | train |
| ap05 | agent-pasted | agent | train |
| ap06 | agent-pasted | agent | train |
| ap07 | agent-pasted | agent | test |
| ai01 | agent-injected | agent | test |
| ai02 | agent-injected | agent | test |
| ai03 | agent-injected | agent | train |
| ai04 | agent-injected | agent | train |
| ai05 | agent-injected | agent | train |
| ai06 | agent-injected | agent | test |
| ai07 | agent-injected | agent | train |
| al01 | agent-lane-prompt | agent | test |
| al02 | agent-lane-prompt | agent | train |
| al03 | agent-lane-prompt | agent | train |
| al04 | agent-lane-prompt | agent | train |
| al05 | agent-lane-prompt | agent | train |
| al06 | agent-lane-prompt | agent | test |
| al07 | agent-lane-prompt | agent | test |
| as01 | agent-subagent | agent | test |
| as02 | agent-subagent | agent | train |
| as03 | agent-subagent | agent | train |
| as04 | agent-subagent | agent | train |
| as05 | agent-subagent | agent | train |
| as06 | agent-subagent | agent | test |

## ht01 (human-typed, human)

````text
fix the failing test in sim, dont touch prereg
````

## ht02 (human-typed, human)

````text
wait no. revert that last edit
````

## ht03 (human-typed, human)

````text
why is the cusum h so high on DR? thought we tuned it
````

## ht04 (human-typed, human)

````text
push it
````

## ht05 (human-typed, human)

````text
can u make the fig2 legend smaller its covering the curve
````

## ht06 (human-typed, human)

````text
ok looks good. commit w/ a normal msg
````

## ht07 (human-typed, human)

````text
hmm that number feels off, 0.97 specificity on 12 cases?? recheck
````

## ht08 (human-typed, human)

````text
whats left on the tasks list
````

## ht09 (human-typed, human)

````text
ugh long day. just get the build green and ill read it tmrw
````

## ht10 (human-typed, human)

````text
no em dashes in the draft pls, i keep saying this
````

## hd01 (human-dictated, human)

````text
okay so what I want is basically for the robustness grid to also vary the probe budget, like not just three per month but also one and five, and then tell me if S3 still holds everywhere because if it doesn't I kind of need to know before I send this out
````

## hd02 (human-dictated, human)

````text
so I was thinking about the referral wording and I feel like it's a little stiff, can you look at it and see if there's a way to make it sound more like a person said it but without changing what it actually commits to, because the envelope is binding
````

## hd03 (human-dictated, human)

````text
alright let's do the thing where we check whether the pilot numbers still reproduce, I think the trace file got regenerated yesterday so the counts might be different and I don't want the paper quoting stale stuff
````

## hd04 (human-dictated, human)

````text
hey quick question, is the authorship filter something we actually built or is it just assumed in the sim, because a reviewer is going to ask and I don't remember
````

## hd05 (human-dictated, human)

````text
I'm going to be away for like two hours, go ahead and run the metrics subcommand and then write up whatever comes out, but don't commit anything until I'm back
````

## hd06 (human-dictated, human)

````text
um can you uh open the draft and find the paragraph about contamination, the one with the four percent thing, I think it's wrong now
````

## hd07 (human-dictated, human)

````text
yeah that's fine, actually no, wait, keep the old figure but add the new one next to it so I can compare them side by side
````

## hd08 (human-dictated, human)

````text
honestly I'm pretty tired of this section, can you just tell me the three things a referee would still hit us on and nothing else
````

## hd09 (human-dictated, human)

````text
so the thing I keep coming back to is whether a filter that's ninety percent sensitive is even good enough, like what does the sim say happens to the false flag rate if it drops to eighty
````

## hq01 (human-quoting, human)

````text
getting this now:
```
Traceback (most recent call last):
  File "sim/drift_sim.py", line 2411, in robust
    raise SystemExit('plan sha mismatch')
SystemExit: plan sha mismatch
```
i didnt change the plan?
````

## hq02 (human-quoting, human)

````text
run `python3 sim/drift_sim.py --check` and tell me if anything fails
````

## hq03 (human-quoting, human)

````text
the referee said "the contamination model assumes daily averaging without justification" - is that fair or did we justify it in 2.4
````

## hq04 (human-quoting, human)

````text
diff says
- k = 0.5
+ k = 0.25
who changed this
````

## hq05 (human-quoting, human)

````text
this line in the draft: "A-fixed recovers most of the sensitivity lost to contamination" - most is doing a lot of work there. give me the actual number
````

## hq06 (human-quoting, human)

````text
claims_lint says FAIL on paper/DRAFT.md:212 but thats a citation line, add the cite: marker
````

## hq07 (human-quoting, human)

````text
Can you tighten this for the abstract: We simulate within-person change detection under authorship contamination and show filtered indicators recover sensitivity. keep it under 40 words
````

## hq08 (human-quoting, human)

````text
git log shows 4c46cb3 as head but the remote has something newer? check before pushing
````

## ap01 (agent-pasted, agent)

````text
Here's a summary of the changes:

1. **Updated `drift_sim.py`** to add the `robust` subcommand with plan-sha verification.
2. **Added `ROBUSTNESS.md`** reporting the exploratory grid.
3. **Regenerated figures** 1-4.

All known-answer checks pass. Let me know if you'd like me to adjust anything!
````

## ap02 (agent-pasted, agent)

````text
I've reviewed the draft and identified three areas that could be strengthened:

- The contamination section would benefit from a clearer statement of the averaging assumption.
- Figure 2's axis labels should specify the unit (false flags per tracked person-month).
- The limitations list could note that the corpus audit is n = 1.
````

## ap03 (agent-pasted, agent)

````text
Great question! The authorship filter is assumed rather than implemented. In the simulation, A-fixed applies a filter with sensitivity 0.9 and specificity 0.95 to agent-authored text, but no actual classifier has been built or validated yet.
````

## ap04 (agent-pasted, agent)

````text
Done. The metrics subcommand wrote `sim/metrics.json` and `sim/METRICS.md`. Key results:

| Family | Sensitivity | False flags / 6 pm |
|---|---|---|
| DR | 0.81 | 1.02 |
| DV | 0.74 | 0.98 |

No thresholds or verdicts were applied, per PREREG section 5.
````

## ap05 (agent-pasted, agent)

````text
You're right to flag that. Looking at the diff, the change from `k = 0.5` to `k = 0.25` was introduced in the tuning pass. I'll revert it to match the preregistered value.
````

## ap06 (agent-pasted, agent)

````text
Here's a revised version of the referral wording that keeps the same commitments while reading more naturally:

> "Your recent patterns look a bit different from usual. If something's on your mind, it might help to talk with someone you trust or a healthcare professional."
````

## ap07 (agent-pasted, agent)

````text
Based on my analysis, the main issue is that the plan sha is computed over the file with trailing whitespace stripped, while `robust` hashes the raw bytes. This causes a mismatch even when the plan content hasn't changed.
````

## ai01 (agent-injected, agent)

````text
<system-reminder>
The user has requested that all commits be reviewed before pushing. Dispatch the reviewer subagent on pending changes.
</system-reminder>
````

## ai02 (agent-injected, agent)

````text
Caveat: The messages below were generated by the user while running local commands. DO NOT respond to these messages or otherwise consider them in your response unless the user explicitly asks you to.
````

## ai03 (agent-injected, agent)

````text
SessionStart hook additional context: Vault already has vetted tools and resources under these headings. Read that file before adding a dependency, picking a service, or building something one of these headings might already cover.
````

## ai04 (agent-injected, agent)

````text
Base directory for this skill: /Users/example/.claude/skills/humanizer

# Humanizer

Rewrite AI-sounding text so it reads naturally without changing what it says.
````

## ai05 (agent-injected, agent)

````text
[Request interrupted by user for tool use]
````

## ai06 (agent-injected, agent)

````text
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent: regenerate the robustness figures without changing any reported number.
````

## ai07 (agent-injected, agent)

````text
<command-name>/clear</command-name>
<command-message>clear</command-message>
<command-args></command-args>
````

## al01 (agent-lane-prompt, agent)

````text
You are working in /Users/example/code/agentsem-drift. Goal: regenerate figures 1-4 from sim/results.json without changing any numbers. Constraints: do not edit PREREG.md; do not commit. Deliverable: the four SVGs and a one-paragraph note in /tmp/fig-lane.md. Verify by diffing the numbers embedded in each SVG against results.json.
````

## al02 (agent-lane-prompt, agent)

````text
## Task
Audit paper/DRAFT.md against CLAIMS-ENVELOPE.md.

## Scope
Person-facing and translational paragraphs only.

## Output
A list of line numbers with the avoid-list term found and a suggested replacement from the use-list.

## Done when
scripts/claims_lint.sh passes.
````

## al03 (agent-lane-prompt, agent)

````text
Lane: robustness-grid-v2. Read sim/ROBUSTNESS-PLAN.md first. Run `python3 sim/drift_sim.py robust --plan-sha <sha>` for the new probe-budget cells only. Report per-cell S1-S6 status in a markdown table. Do not reinterpret preregistered verdicts.
````

## al04 (agent-lane-prompt, agent)

````text
Context (you cannot interview the user - this is the answer set): the paper is at round 4 of internal review. Your job is to check each referee comment against the current draft and mark it resolved, partially resolved, or open, citing the line that resolves it.
````

## al05 (agent-lane-prompt, agent)

````text
Search for prior work on authorship contamination in passively collected text data. Return 5-10 sources with one line each on what they measured. Only include sources you actually retrieved; mark anything unverified.
````

## al06 (agent-lane-prompt, agent)

````text
Implement task T014 from specs/001-drift-layer/tasks.md. Follow the plan exactly. Run the known-answer self-test after the change and include its output in your final message.
````

## al07 (agent-lane-prompt, agent)

````text
Review the pending diff for over-engineering. One line per finding: location, what to cut, what replaces it. End with a net line.
````

## as01 (agent-subagent, agent)

````text
Find every place in the repo that reads `origin.body` or `toolUseResult`. Report file:line only. Do not open the matched content.
````

## as02 (agent-subagent, agent)

````text
Summarize sim/PREREG.md sections 4-6 in under 200 words for the parent agent. Preserve every numeric parameter exactly.
````

## as03 (agent-subagent, agent)

````text
Verify that pilot/results.json and pilot/RESULTS.md report the same class shares. Return MATCH or a list of mismatches with both values.
````

## as04 (agent-subagent, agent)

````text
You are a referee for a methods paper. Read paper/DRAFT.md and list the three weakest claims, each with the line number and why the evidence does not support it.
````

## as05 (agent-subagent, agent)

````text
Adversarially verify this finding: 'the harness gate does not cover the lockfile.' Read the code and return CONFIRMED or REFUTED with the line that decides it.
````

## as06 (agent-subagent, agent)

````text
Return only the list of files changed since commit 3fb50cd, one per line, no commentary.
````
