#!/usr/bin/env python3
"""Minimal Agent Client Protocol (ACP) client that drives `kiro-cli acp` over stdio.

ACP is JSON-RPC 2.0 over newline-delimited stdio. Flow:
  initialize -> session/new -> session/prompt (agent streams session/update notifications)
The agent may call back `session/request_permission`; this client approves only
read-only tool kinds and rejects everything else.

usage: python3 acp_client.py "Summarise this repo" [--agent reviewer] [--cwd .]
"""
import argparse
import itertools
import json
import os
import subprocess
import sys

READ_ONLY_KINDS = {"read", "search", "fetch", "think"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--agent")
    ap.add_argument("--cwd", default=os.getcwd())
    args = ap.parse_args()

    cmd = ["kiro-cli", "acp"] + (["--agent", args.agent] if args.agent else [])
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    ids = itertools.count(1)

    def send(msg: dict) -> None:
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()

    def request(method: str, params: dict) -> dict:
        rid = next(ids)
        send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        for line in proc.stdout:
            msg = json.loads(line)
            if msg.get("id") == rid and "method" not in msg:
                if "error" in msg:
                    sys.exit(f"{method} failed: {msg['error']}")
                return msg["result"]
            handle(msg)
        sys.exit("agent exited")

    def handle(msg: dict) -> None:
        method = msg.get("method")
        if method == "session/update":
            upd = msg["params"].get("update", {})
            kind = upd.get("sessionUpdate")
            if kind == "agent_message_chunk":
                content = upd.get("content", {})
                if content.get("type") == "text":
                    print(content.get("text", ""), end="", flush=True)
            elif kind in ("tool_call", "tool_call_update"):
                print(f"\n  ⚙ {upd.get('title') or upd.get('toolCallId')} [{upd.get('status', '')}]", file=sys.stderr)
            elif kind == "plan":
                for e in upd.get("entries", []):
                    print(f"  ☐ {e.get('content')}", file=sys.stderr)
        elif method == "session/request_permission":
            tool = msg["params"].get("toolCall", {})
            options = msg["params"].get("options", [])
            allow = tool.get("kind") in READ_ONLY_KINDS
            wanted = "allow_once" if allow else "reject_once"
            choice = next((o for o in options if o.get("kind") == wanted), None)
            outcome = {"outcome": "selected", "optionId": choice["optionId"]} if choice else {"outcome": "cancelled"}
            print(f"\n  🔐 {tool.get('title')} → {'allow' if allow else 'reject'}", file=sys.stderr)
            send({"jsonrpc": "2.0", "id": msg["id"], "result": {"outcome": outcome}})

    init = request("initialize", {
        "protocolVersion": 1,
        "clientCapabilities": {"fs": {"readTextFile": False, "writeTextFile": False}, "terminal": False},
    })
    print(f"agent: {init.get('agentInfo', {}).get('name', 'kiro')} (protocol {init.get('protocolVersion')})", file=sys.stderr)
    session = request("session/new", {"cwd": os.path.abspath(args.cwd), "mcpServers": []})
    result = request("session/prompt", {
        "sessionId": session["sessionId"],
        "prompt": [{"type": "text", "text": args.prompt}],
    })
    print(f"\n\n[stop reason: {result.get('stopReason')}]", file=sys.stderr)
    proc.terminate()


if __name__ == "__main__":
    main()
