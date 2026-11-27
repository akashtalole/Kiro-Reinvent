#!/usr/bin/env python3
"""Verify or create the X-Signature for a Ring webhook body (HMAC-SHA256, hex).

  RING_SIGNING_KEY=... verify.py BODY_FILE "sha256=<hex>"   -> exit 0 valid, 1 invalid
  RING_SIGNING_KEY=... verify.py --sign BODY_FILE            -> prints "sha256=<hex>"
The key is read from the environment only and never printed.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import sys


def sign(body: bytes, key: bytes) -> str:
    return "sha256=" + hmac.new(key, body, hashlib.sha256).hexdigest()


def verify(body: bytes, header: str, key: bytes) -> bool:
    return hmac.compare_digest(sign(body, key), (header or "").strip())


def main(argv: list[str]) -> int:
    key = os.environ.get("RING_SIGNING_KEY", "").encode()
    if not key:
        print("set RING_SIGNING_KEY", file=sys.stderr)
        return 2
    if argv[:1] == ["--sign"] and len(argv) == 2:
        print(sign(open(argv[1], "rb").read(), key))
        return 0
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    body = open(argv[0], "rb").read()
    ok = verify(body, argv[1], key)
    print("valid" if ok else f"INVALID (expected prefix {sign(body, key)[:15]}…)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
