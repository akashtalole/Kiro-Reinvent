#!/usr/bin/env python3
"""Count resource types in a CloudFormation template: inventory.py template.json"""
import collections
import json
import sys

res = json.load(open(sys.argv[1])).get("Resources", {})
for t, n in collections.Counter(r["Type"] for r in res.values()).most_common():
    print(f"{n:4d}  {t}")
