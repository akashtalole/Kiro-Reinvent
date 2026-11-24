"""Backfill per-tenant Bedrock application inference profiles for existing tenants.

    python create_tenant_profiles.py --base-model-arn arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0 \
        --tenants t-acme01:premium t-globex2:basic
Activate the `tenantId` cost-allocation tag in Billing so spend shows per tenant in Cost Explorer.
Default quota is 1,000 application profiles per Region per account (adjustable).
"""
import argparse

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--base-model-arn", required=True)
ap.add_argument("--tenants", nargs="+", required=True, help="tenantId:tier pairs")
ap.add_argument("--region", default="us-east-1")
a = ap.parse_args()
bedrock = boto3.client("bedrock", region_name=a.region)
existing = {p["inferenceProfileName"] for p in bedrock.list_inference_profiles(typeEquals="APPLICATION")["inferenceProfileSummaries"]}
for pair in a.tenants:
    tenant, tier = pair.split(":")
    name = f"{tenant}-default"
    if name in existing:
        print("exists ", name)
        continue
    r = bedrock.create_inference_profile(
        inferenceProfileName=name, description=f"Default model for {tenant} ({tier})",
        modelSource={"copyFrom": a.base_model_arn},
        tags=[{"key": "tenantId", "value": tenant}, {"key": "tier", "value": tier}],
    )
    print("created", name, r["inferenceProfileArn"])
