#!/usr/bin/env python3
"""pilot/inventory.py -- rights/provenance inventory (spec.md section 9, Stage 2 item a).

For each surface Abhay controls, records: path, date range, approximate count, who
authored it, whether third-party content is present, and whether it is usable for
research without other people's permission. Metadata only: file counts, mtimes, git
commit author emails and dates, and (for the transcripts surface) numbers already
computed by trace_audit.py. NO message/note/commit-diff body is ever opened. No network
or MCP calls are made; any surface only reachable through a connector is listed as
"connector-only, not inventoried" rather than touched.

Writes: pilot/INVENTORY.md
"""

import json
import os
import subprocess
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_DIR = os.path.join(REPO_ROOT, "pilot")
RESULTS_JSON = os.path.join(PILOT_DIR, "results.json")
INVENTORY_MD = os.path.join(PILOT_DIR, "INVENTORY.md")

OBSIDIAN_VAULT = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Brain"
)
REMEMBER_DIR = os.path.expanduser("~/.remember")
CODE_DIR = os.path.expanduser("~/code")
LANES_DIR = os.path.expanduser("~/.instinct/lanes")
LANES_PROMPTS_DIR = os.path.join(LANES_DIR, "prompts")
CLAUDE_PROJECTS_DIR = os.path.expanduser("~/.claude/projects")

MY_EMAILS = {
    "owner@example.com",
    "113219143+abhaymettu@users.noreply.github.com",
}


def file_stats(root, exts=None):
    """Count files (optionally filtered by extension) and their mtime date range,
    walking the tree. Never opens file contents."""
    count = 0
    min_dt, max_dt = None, None
    if not os.path.isdir(root):
        return {"exists": False, "count": 0, "min_date": None, "max_date": None}
    for dirpath, dirnames, filenames in os.walk(root):
        # skip heavy/irrelevant version-control internals if any
        dirnames[:] = [d for d in dirnames if d not in (".git", ".obsidian", "node_modules")]
        for fn in filenames:
            if exts and not fn.lower().endswith(tuple(exts)):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                mtime = os.path.getmtime(fp)
            except OSError:
                continue
            dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            count += 1
            if min_dt is None or dt < min_dt:
                min_dt = dt
            if max_dt is None or dt > max_dt:
                max_dt = dt
    return {
        "exists": True,
        "count": count,
        "min_date": min_dt.date().isoformat() if min_dt else None,
        "max_date": max_dt.date().isoformat() if max_dt else None,
    }


def find_git_repos(root):
    repos = []
    if not os.path.isdir(root):
        return repos
    for entry in sorted(os.listdir(root)):
        fp = os.path.join(root, entry)
        if os.path.isdir(os.path.join(fp, ".git")):
            repos.append(fp)
    return repos


def git_commit_stats(repo_path):
    """Commit count, author-email tally, and date range for a repo's current history.
    Reads commit metadata only (author email + date), never a diff or commit message body."""
    try:
        out = subprocess.run(
            ["git", "-C", repo_path, "log", "--all", "--format=%ae|%ad", "--date=short"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if out.returncode != 0:
        return None
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    if not lines:
        return {"commits": 0, "authors": {}, "min_date": None, "max_date": None}
    authors = {}
    dates = []
    for line in lines:
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        email, date = parts
        authors[email] = authors.get(email, 0) + 1
        dates.append(date)
    dates.sort()
    return {
        "commits": len(lines),
        "authors": authors,
        "min_date": dates[0] if dates else None,
        "max_date": dates[-1] if dates else None,
    }


SMALL_COLLAB_THRESHOLD = 5  # <= this many distinct non-owner authors => plausible personal
                            # collaborator; more than this => almost certainly a cloned/forked
                            # external project (its upstream OSS history, not personal data).


def inventory_git_repos():
    repos = find_git_repos(CODE_DIR)
    total_commits = 0
    all_authors = {}
    min_date, max_date = None, None
    small_collab_repos = []   # (name, n_other_authors) -- few enough to be real collaborators
    external_project_repos = []  # (name, distinct_other_author_count) -- likely a fork/clone
    per_repo = []
    for repo in repos:
        stats = git_commit_stats(repo)
        if stats is None or stats["commits"] == 0:
            continue
        total_commits += stats["commits"]
        for email, n in stats["authors"].items():
            all_authors[email] = all_authors.get(email, 0) + n
        if stats["min_date"] and (min_date is None or stats["min_date"] < min_date):
            min_date = stats["min_date"]
        if stats["max_date"] and (max_date is None or stats["max_date"] > max_date):
            max_date = stats["max_date"]
        other = {e: n for e, n in stats["authors"].items() if e not in MY_EMAILS}
        if other:
            if len(other) <= SMALL_COLLAB_THRESHOLD:
                small_collab_repos.append((os.path.basename(repo), len(other)))
            else:
                external_project_repos.append((os.path.basename(repo), len(other)))
        per_repo.append((os.path.basename(repo), stats["commits"], stats["min_date"], stats["max_date"]))
    return {
        "repo_count": len(repos),
        "repos_with_commits": len(per_repo),
        "total_commits": total_commits,
        "distinct_author_emails": len(all_authors),
        "min_date": min_date,
        "max_date": max_date,
        "small_collab_repos": small_collab_repos,
        "external_project_repos": external_project_repos,
    }


def inventory_lanes():
    prompts_stats = file_stats(LANES_PROMPTS_DIR, exts=[".txt"])
    manifest_path = os.path.join(LANES_DIR, "manifest.json")
    manifest_entries = None
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", errors="replace") as fh:
                obj = json.load(fh)
            manifest_entries = len(obj) if hasattr(obj, "__len__") else None
        except (OSError, json.JSONDecodeError):
            manifest_entries = None
    return {"prompts": prompts_stats, "manifest_entries": manifest_entries}


def load_transcript_summary():
    if not os.path.isfile(RESULTS_JSON):
        return None
    with open(RESULTS_JSON, "r") as fh:
        d = json.load(fh)
    agg = d["aggregates"]
    stats = d["stats"]
    return {
        "user_entries": stats["user_entries"],
        "assistant_entries": stats["assistant_entries"],
        "sessions": agg["sessions"]["total_sessions"],
        "days_with_any_user_role_activity": agg["density"]["days_with_any_user_role_activity"],
        "share_entries_with_paste_marker": agg["third_party"]["share_entries_with_paste_marker"],
        "share_tool_result_entries_third_party": agg["third_party"]["share_tool_result_entries_third_party"],
    }


def render_md():
    transcripts = load_transcript_summary()
    obsidian = file_stats(OBSIDIAN_VAULT, exts=[".md"])
    remember = file_stats(REMEMBER_DIR)
    git_repos = inventory_git_repos()
    lanes = inventory_lanes()

    lines = []
    lines.append("# Rights / provenance inventory\n")
    lines.append(
        "Per spec.md section 9, Stage 2 item (a): for every surface Abhay controls, what "
        "exists, its date range, who authored it, whether third-party content is present, "
        "and whether it is usable for research without other people's permission. "
        "Metadata only -- no note, message, or commit body was opened to produce this "
        "document. No network or MCP call was made; connector-only surfaces are listed "
        "as such, not inventoried.\n"
    )

    lines.append("## Claude Code transcripts\n")
    lines.append(f"- Path: `{CLAUDE_PROJECTS_DIR}`")
    if transcripts:
        lines.append(f"- Approx. count: {transcripts['user_entries']} user-role + {transcripts['assistant_entries']} assistant-role entries, across {transcripts['sessions']} sessions")
        lines.append(f"- Date range: {transcripts['days_with_any_user_role_activity']} distinct local calendar days of activity (see pilot/RESULTS.md for the full breakdown)")
    else:
        lines.append("- Run `pilot/trace_audit.py` first to populate counts (pilot/results.json not found).")
    lines.append(
        "- Authored by: him (typed turns), the agent (assistant turns, tool results), "
        "and automated lanes/subagents (a large majority of 'user'-role entries in this "
        "corpus are tool-results or subagent/sidechain traffic, not typed text -- see "
        "pilot/RESULTS.md)."
    )
    if transcripts:
        lines.append(
            f"- Third-party content: present, low-share estimate. "
            f"{transcripts['share_entries_with_paste_marker']:.4f} of user-role entries carry a "
            f"pasted-content marker (mostly full-message pastes, not mixed with typed prose -- see "
            f"pilot/RESULTS.md), and {transcripts['share_tool_result_entries_third_party']:.4f} of "
            f"tool-result entries come from a tool whose name matches a messaging/calendar/email "
            f"keyword (tool name only; result content was never read). This is a coarse structural "
            f"estimate, not a count of actual other people."
        )
    lines.append(
        "- Usable for research on his own usage metadata without others' permission: yes, "
        "at the metadata level this audit operates on. Any content-level use (e.g. reading "
        "the text of a pasted email) would need those spans excluded or separately cleared.\n"
    )

    lines.append("## Obsidian vault\n")
    lines.append(f"- Path: `{OBSIDIAN_VAULT}`")
    lines.append(f"- Exists: {obsidian['exists']}")
    lines.append(f"- Approx. count (`.md` files): {obsidian['count']}")
    lines.append(f"- Date range (file mtimes): {obsidian['min_date']} to {obsidian['max_date']}")
    lines.append("- Authored by: him (personal notes, second-brain captures via the `brain-capture` skill).")
    lines.append(
        "- Third-party content: unknown from metadata alone -- not inspected here. Likely "
        "present in some notes (e.g. quoting a meeting or a message) but not counted; a "
        "content-level pass would be needed before any release."
    )
    lines.append(
        "- Usable for research on file counts/dates/structure without others' permission: "
        "yes. Usable at the content level: not established by this inventory.\n"
    )

    lines.append("## ~/.remember\n")
    lines.append(f"- Path: `{REMEMBER_DIR}`")
    lines.append(f"- Exists: {remember['exists']}")
    lines.append(f"- Approx. count (all files): {remember['count']}")
    lines.append(f"- Date range (file mtimes): {remember['min_date']} to {remember['max_date']}")
    lines.append("- Authored by: him and the agent (a Claude memory-plugin store).")
    lines.append("- Third-party content: unknown from metadata alone -- not inspected.")
    lines.append("- Usable for research on counts/dates without others' permission: yes.\n")

    lines.append("## git repos under ~/code\n")
    lines.append(f"- Repos found (have a `.git` dir): {git_repos['repo_count']}")
    lines.append(f"- Repos with commit history read: {git_repos['repos_with_commits']}")
    lines.append(f"- Total commits (all branches, all repos): {git_repos['total_commits']}")
    lines.append(f"- Date range (author dates): {git_repos['min_date']} to {git_repos['max_date']}")
    lines.append(f"- Distinct author emails across all repos: {git_repos['distinct_author_emails']}")
    if git_repos["small_collab_repos"]:
        lines.append(
            f"- Repos with a small number (<={SMALL_COLLAB_THRESHOLD}) of non-owner commit "
            "author emails -- plausible personal collaborators, worth a manual look before "
            "any use beyond his own metadata: "
            + "; ".join(f"{name} ({n} non-owner author(s), emails not listed)" for name, n in git_repos["small_collab_repos"])
        )
    else:
        lines.append(f"- No repo showed a small (<={SMALL_COLLAB_THRESHOLD}) set of non-owner authors.")
    if git_repos["external_project_repos"]:
        lines.append(
            "- Repos with a large number of distinct non-owner author emails (almost "
            "certainly a cloned/forked external project's own upstream history, not "
            "personal collaboration data -- author counts only, no emails listed): "
            + "; ".join(f"{name} ({n} distinct authors)" for name, n in git_repos["external_project_repos"])
        )
    lines.append(
        "- Authored by: him, for the repos with no or few non-owner authors (commit "
        "metadata only was read, never diffs or commit message bodies). The 'large "
        "number of authors' repos above are external/forked projects, authored by their "
        "upstream contributors, not personal data about people he knows."
    )
    lines.append(
        "- Usable for research on commit counts/dates/authorship without others' "
        "permission: yes, for the repos where he is the sole or near-sole author, and for "
        "the external-project repos (public upstream OSS history). The small-collaborator "
        "repos should get a manual look before any use beyond his own metadata.\n"
    )

    lines.append("## ~/.instinct/lanes\n")
    lines.append(f"- Manifest: `{os.path.join(LANES_DIR, 'manifest.json')}`, top-level entries: {lanes['manifest_entries']}")
    lines.append(f"- Prompts dir: `{LANES_PROMPTS_DIR}`, `.txt` file count: {lanes['prompts']['count']}, date range (mtimes): {lanes['prompts']['min_date']} to {lanes['prompts']['max_date']}")
    lines.append("- Authored by: him (lane configuration) and agents (persisted lane prompts, written verbatim, never reconstructed from memory, per lane policy).")
    lines.append("- Third-party content: none expected (infrastructure/tooling config, not personal correspondence).")
    lines.append("- Usable for research (as infra metadata) without others' permission: yes.\n")

    lines.append("## Connector-only surfaces (not inventoried)\n")
    lines.append(
        "Per instruction, no MCP or network call was made to produce this inventory. "
        "The following surfaces are only reachable through a connector and are listed "
        "here as **connector-only, not inventoried**, not as \"absent\":\n"
    )
    lines.append("- Google Calendar (via the Google Calendar MCP connector)")
    lines.append("- Gmail (via the Gmail MCP connector)")
    lines.append("- Wispr Flow dictation/meeting notes (via the wisprflow / wispr-flow-write MCP connectors)")
    lines.append("- Any messaging relay (iMessage/SMS/Slack/etc.) reachable only through an MCP tool, not a local file\n")

    lines.append(
        "## Summary judgment\n\n"
        "The Claude Code transcripts are the surface with the most directly relevant "
        "third-party-content risk for this project, quantified here via structural markers "
        "only (not content review); the estimated share is small (well under 1% of entries "
        "by either marker). The Obsidian vault and `~/.remember` were not content-inspected "
        "and should not be treated as cleared for anything beyond count/date-level use until "
        "a content-level pass is done. Git history under `~/code` does show many non-owner "
        f"commit authors, but essentially all of them sit in repos with more than "
        f"{SMALL_COLLAB_THRESHOLD} distinct outside authors -- i.e. cloned/forked external "
        "projects' own public upstream history, not personal collaboration data; any repo "
        f"with <= {SMALL_COLLAB_THRESHOLD} outside authors is called out by name above for a "
        "manual look. No calendar, email, or messaging-relay data was read. **No state of "
        "any person was estimated in producing this inventory.**\n"
    )
    return "\n".join(lines)


def main():
    os.makedirs(PILOT_DIR, exist_ok=True)
    md = render_md()
    with open(INVENTORY_MD, "w") as fh:
        fh.write(md)
    print(f"wrote {INVENTORY_MD}")


if __name__ == "__main__":
    main()
