"""Kiro Crew script job: watch GitHub Actions and wake someone only when a run fails.

Install:  cp ci_watch.py ~/.kiro/crew/crons/
Schedule: kirocrew cron add "ci-watch" "watch CI" \
            --script ~/.kiro/crew/crons/ci_watch.py:run --every 900 \
            --no-persistent-session --minimal-context

Needs the GitHub CLI (`gh`) signed in on the gateway host. No model call is made
unless a run has failed, and even then only a notification is sent.
"""
from __future__ import annotations

import json
import os
import subprocess

try:  # provided by the Kiro Crew runtime
    from kiro_crew.cron_script import Skip
except ImportError:  # lets you run the file locally for a dry run
    class Skip(Exception):
        """Stand-in for kiro_crew.cron_script.Skip outside Crew."""

REPO = os.environ.get("CI_WATCH_REPO", "owner/repo")
LIMIT = 5


def latest_runs(repo: str = REPO, limit: int = LIMIT) -> list[dict]:
    out = subprocess.run(
        ["gh", "run", "list", "--repo", repo, "--limit", str(limit),
         "--json", "name,conclusion,status,url,headBranch"],
        capture_output=True, text=True, timeout=60, check=True,
    ).stdout
    return json.loads(out or "[]")


def failures(runs: list[dict]) -> list[dict]:
    return [r for r in runs if r.get("status") == "completed" and r.get("conclusion") == "failure"]


def run(ctx) -> None:
    bad = failures(latest_runs())
    if not bad:
        raise Skip()  # green: stay silent, check again next tick
    lines = [f"- {r['name']} on {r['headBranch']}: {r['url']}" for r in bad]
    ctx.notify(f"CI is red in {REPO}:\n" + "\n".join(lines))


if __name__ == "__main__":  # local dry run: python ci_watch.py
    print(json.dumps(failures(latest_runs()), indent=2))
