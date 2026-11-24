"""Register a GitHub OAuth app with AgentCore Identity's token vault.

1. Create a GitHub OAuth App (Settings → Developer settings → OAuth Apps).
2. Run this script; copy the printed callbackUrl into the GitHub app's "Authorization callback URL".

    GITHUB_CLIENT_ID=... GITHUB_CLIENT_SECRET=... python create_github_provider.py
"""
import os

import boto3

ctl = boto3.client("bedrock-agentcore-control", region_name=os.environ.get("AWS_REGION", "us-east-1"))
resp = ctl.create_oauth2_credential_provider(
    name="github-provider",
    credentialProviderVendor="GithubOauth2",
    oauth2ProviderConfigInput={"githubOauth2ProviderConfig": {
        "clientId": os.environ["GITHUB_CLIENT_ID"],
        "clientSecret": os.environ["GITHUB_CLIENT_SECRET"],   # stored in Secrets Manager by the service
    }},
)
print("provider ARN:", resp["credentialProviderArn"])
print("callbackUrl  :", resp["callbackUrl"])
