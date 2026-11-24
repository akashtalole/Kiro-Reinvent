"""An agent that acts on GitHub *as the signed-in user* via AgentCore Identity (OAuth 3LO / user federation).

The agent never sees a long-lived secret: AgentCore Identity runs the OAuth flow, stores the user's
token in its vault keyed by the agent's workload identity + user, and hands a short-lived access
token to the decorated tool. First call prints an authorization URL; later calls reuse the token.

    python github_agent.py "List my 5 most recently updated repositories and any open PRs on them"
"""
import asyncio
import sys

import requests
from bedrock_agentcore.identity.auth import requires_access_token
from strands import Agent, tool

_token: dict = {}


def show_auth_url(url: str) -> None:
    print(f"\n🔐 Authorize GitHub access for this agent:\n{url}\n")


@requires_access_token(
    provider_name="github-provider",
    scopes=["repo", "read:user"],
    auth_flow="USER_FEDERATION",
    on_auth_url=show_auth_url,
    force_authentication=False,
)
async def _fetch_token(*, access_token: str) -> str:
    return access_token


def github_get(path: str, **params) -> list | dict:
    if "value" not in _token:
        _token["value"] = asyncio.run(_fetch_token())
    r = requests.get(f"https://api.github.com{path}", params=params, timeout=15,
                     headers={"Authorization": f"Bearer {_token['value']}", "Accept": "application/vnd.github+json"})
    r.raise_for_status()
    return r.json()


@tool
def my_recent_repos(limit: int = 5) -> list[dict]:
    """List the signed-in user's most recently updated repositories.

    Args:
        limit: How many repositories to return (max 20).
    """
    repos = github_get("/user/repos", sort="updated", per_page=min(limit, 20))
    return [{"full_name": r["full_name"], "updated_at": r["updated_at"], "open_issues": r["open_issues_count"]} for r in repos]


@tool
def open_pull_requests(full_name: str) -> list[dict]:
    """List open pull requests for a repository the user can access.

    Args:
        full_name: "owner/repo".
    """
    prs = github_get(f"/repos/{full_name}/pulls", state="open", per_page=10)
    return [{"number": p["number"], "title": p["title"], "author": p["user"]["login"]} for p in prs]


agent = Agent(system_prompt="You help developers triage their GitHub work. Be concise; use tables.",
              tools=[my_recent_repos, open_pull_requests])

if __name__ == "__main__":
    agent(" ".join(sys.argv[1:]) or "List my 5 most recently updated repositories and any open PRs on them")
