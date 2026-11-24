"""A data-analyst agent that runs model-written code in an isolated AgentCore Code Interpreter sandbox
— never on your host — and browses the web in an isolated AgentCore Browser.

    python analyst_agent.py "Download the CSV at <url>, compute weekly sends per channel, and chart it"
"""
import json
import sys

from bedrock_agentcore.tools.browser_client import browser_session
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
from playwright.sync_api import sync_playwright
from strands import Agent, tool

REGION = "us-east-1"
_ci = CodeInterpreter(REGION)          # one sandbox session for the agent's lifetime (state persists between calls)


def _collect(response: dict) -> dict:
    """Flatten the streamed executeCode response into {stdout, stderr, exit_code}."""
    out: dict = {}
    for event in response.get("stream", []):
        result = event.get("result", {})
        out.update(result.get("structuredContent", {}) or {})
        if result.get("isError"):
            out["error"] = result.get("content")
    return out


@tool
def run_python(code: str) -> dict:
    """Execute Python in an isolated sandbox (pandas, numpy, matplotlib available). Variables persist
    between calls. Print results you need; save charts to files and say their names.

    Args:
        code: Python source to execute.
    """
    if not _ci.session_id:
        _ci.start()
    return _collect(_ci.execute_code(code))


@tool
def read_web_page(url: str) -> dict:
    """Open a URL in an isolated cloud browser and return the page title and visible text (first 6k chars).

    Args:
        url: http(s) URL to open.
    """
    if not url.startswith(("https://", "http://")):
        return {"error": "only http(s) URLs are allowed"}
    with browser_session(REGION) as client:
        ws_url, headers = client.generate_ws_headers()
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            text = page.inner_text("body")[:6000]
            title = page.title()
            browser.close()
    return {"title": title, "text": text}


agent = Agent(
    system_prompt=("You are a careful data analyst. Use run_python for every computation (never do math in your head) "
                   "and read_web_page to gather sources. Show the key numbers, then a 3-bullet interpretation."),
    tools=[run_python, read_web_page],
)

if __name__ == "__main__":
    try:
        agent(" ".join(sys.argv[1:]) or
              "Generate 90 days of synthetic daily notification sends for email and push with weekly seasonality, "
              "then report the week-over-week trend per channel and any anomalies.")
    finally:
        if _ci.session_id:
            _ci.stop()
