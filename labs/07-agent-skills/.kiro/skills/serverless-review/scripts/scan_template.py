#!/usr/bin/env python3
"""Static scan of a synthesized CloudFormation template for common serverless misconfigurations.

usage: scan_template.py template.json
Prints one finding per line: SEVERITY<TAB>LogicalId<TAB>message
"""
import json
import sys


def main(path: str) -> int:
    tpl = json.load(open(path))
    res = tpl.get("Resources", {})
    findings = []
    fn_timeouts = {}
    for lid, r in res.items():
        t, p = r.get("Type"), r.get("Properties", {}) or {}
        if t == "AWS::Lambda::Function":
            fn_timeouts[lid] = p.get("Timeout", 3)
            if "Timeout" not in p:
                findings.append(("major", lid, "Timeout not set (defaults to 3 s)"))
            if p.get("MemorySize", 128) == 128:
                findings.append(("minor", lid, "MemorySize left at 128 MB — tune it"))
            if "arm64" not in (p.get("Architectures") or []):
                findings.append(("minor", lid, "x86_64 — consider arm64 (Graviton)"))
            if not p.get("TracingConfig"):
                findings.append(("minor", lid, "Tracing not enabled"))
        if t == "AWS::SQS::Queue" and "RedrivePolicy" not in p and not lid.lower().startswith("dlq") and "dlq" not in lid.lower():
            findings.append(("major", lid, "Queue has no RedrivePolicy (DLQ)"))
        if t == "AWS::Lambda::EventSourceMapping":
            if "ReportBatchItemFailures" not in (p.get("FunctionResponseTypes") or []):
                findings.append(("major", lid, "Event source mapping without ReportBatchItemFailures"))
        if t == "AWS::Logs::LogGroup" and "RetentionInDays" not in p:
            findings.append(("minor", lid, "Log group never expires"))
        if t == "AWS::IAM::Policy":
            for st in (p.get("PolicyDocument", {}).get("Statement") or []):
                acts = st.get("Action")
                acts = acts if isinstance(acts, list) else [acts]
                if st.get("Effect") == "Allow" and any(a == "*" or (isinstance(a, str) and a.endswith(":*")) for a in acts):
                    findings.append(("blocker", lid, f"Wildcard action {acts}"))
    for sev, lid, msg in findings:
        print(f"{sev}\t{lid}\t{msg}")
    print(f"# {len(findings)} findings across {len(res)} resources; functions: {', '.join(fn_timeouts) or 'none'}")
    return 1 if any(f[0] == "blocker" for f in findings) else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
