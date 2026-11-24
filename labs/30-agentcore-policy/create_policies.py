"""Create a policy engine, generate policies from natural language, create them, and attach the
engine to a gateway in LOG_ONLY mode. Flip to ENFORCE with --enforce after reviewing decisions.

    python create_policies.py --gateway-id <id>               # generate + create + attach (LOG_ONLY)
    python create_policies.py --gateway-id <id> --enforce     # switch the gateway to ENFORCE
"""
import argparse
import json
import pathlib
import time

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--gateway-id", required=True)
ap.add_argument("--region", default="us-east-1")
ap.add_argument("--enforce", action="store_true")
args = ap.parse_args()
ctl = boto3.client("bedrock-agentcore-control", region_name=args.region)
gw = ctl.get_gateway(gatewayIdentifier=args.gateway_id)
state_file = pathlib.Path("policy-state.json")


def attach(engine_arn: str, mode: str) -> None:
    ctl.update_gateway(
        gatewayIdentifier=gw["gatewayId"], name=gw["name"], roleArn=gw["roleArn"],
        protocolType=gw["protocolType"], authorizerType=gw["authorizerType"],
        authorizerConfiguration=gw.get("authorizerConfiguration", {}),
        protocolConfiguration=gw.get("protocolConfiguration", {}),
        policyEngineConfiguration={"arn": engine_arn, "mode": mode},
    )
    print(f"gateway {gw['gatewayId']} → policy engine in {mode} mode")


if args.enforce:
    attach(json.loads(state_file.read_text())["engineArn"], "ENFORCE")
    raise SystemExit

engine = ctl.create_policy_engine(name="acme_support_policies", description="Refund and order tool policies")
while ctl.get_policy_engine(policyEngineId=engine["policyEngineId"])["status"] not in ("ACTIVE", "CREATE_FAILED"):
    time.sleep(3)

gen = ctl.start_policy_generation(
    policyEngineId=engine["policyEngineId"], name="refund_rules",
    resource={"arn": gw["gatewayArn"]},
    content={"rawText": pathlib.Path("policies/requirements.txt").read_text()},
)
gen_id = gen["policyGenerationId"]
while (status := ctl.get_policy_generation(policyEngineId=engine["policyEngineId"], policyGenerationId=gen_id)["status"]) \
        not in ("GENERATED", "GENERATE_FAILED"):
    time.sleep(5)
print("generation:", status)

assets = ctl.list_policy_generation_assets(policyEngineId=engine["policyEngineId"], policyGenerationId=gen_id)["policyGenerationAssets"]
created = []
for i, asset in enumerate(assets):
    print(f"\n--- asset {i}: {asset.get('rawTextFragment', '')[:100]}")
    print(json.dumps(asset.get("definition"), indent=2)[:1200])
    if asset.get("findings"):
        print("findings:", asset["findings"])
    if input("Create this policy? [y/N] ").strip().lower() == "y":
        p = ctl.create_policy(
            policyEngineId=engine["policyEngineId"], name=f"refund_rule_{i}",
            definition={"policyGeneration": {"policyGenerationId": gen_id, "policyGenerationAssetId": asset["policyGenerationAssetId"]}},
            validationMode="FAIL_ON_ANY_FINDINGS",
        )
        created.append(p["policyId"])

state_file.write_text(json.dumps({"engineId": engine["policyEngineId"], "engineArn": engine["policyEngineArn"], "policies": created}, indent=2))
attach(engine["policyEngineArn"], "LOG_ONLY")
print("\nReview decisions in CloudWatch, then run with --enforce.")
