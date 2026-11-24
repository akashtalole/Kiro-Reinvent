"""Create an AgentCore Gateway (MCP) with Cognito M2M auth and a Lambda target exposing three tools.

    python create_gateway.py --lambda-arn arn:aws:lambda:us-east-1:<acct>:function:acme-tools --region us-east-1

Writes gateway.json (gatewayUrl, token endpoint, client id/secret) for agent_via_gateway.py.
Everything created here is listed in gateway.json so cleanup.py can delete it.
"""
import argparse
import json
import time
import uuid

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--lambda-arn", required=True)
ap.add_argument("--region", default="us-east-1")
ap.add_argument("--name", default="acme-tools-gw")
args = ap.parse_args()

session = boto3.session.Session(region_name=args.region)
iam, cognito, ctl = session.client("iam"), session.client("cognito-idp"), session.client("bedrock-agentcore-control")
account = session.client("sts").get_caller_identity()["Account"]
suffix = uuid.uuid4().hex[:6]

# 1) Cognito user pool for machine-to-machine (client credentials) tokens
pool = cognito.create_user_pool(PoolName=f"{args.name}-{suffix}")["UserPool"]
domain = f"{args.name}-{suffix}"
cognito.create_user_pool_domain(Domain=domain, UserPoolId=pool["Id"])
cognito.create_resource_server(UserPoolId=pool["Id"], Identifier="acme-tools", Name="acme-tools",
                               Scopes=[{"ScopeName": "invoke", "ScopeDescription": "Invoke gateway tools"}])
client = cognito.create_user_pool_client(
    UserPoolId=pool["Id"], ClientName="support-agent", GenerateSecret=True,
    AllowedOAuthFlows=["client_credentials"], AllowedOAuthScopes=["acme-tools/invoke"],
    AllowedOAuthFlowsUserPoolClient=True, SupportedIdentityProviders=["COGNITO"],
)["UserPoolClient"]

# 2) Gateway execution role: lets the gateway invoke the tools Lambda
role_name = f"{args.name}-role-{suffix}"
role = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                   "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"aws:SourceAccount": account}}}],
}))["Role"]
iam.put_role_policy(RoleName=role_name, PolicyName="invoke-tools", PolicyDocument=json.dumps({
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": args.lambda_arn}],
}))
time.sleep(10)  # IAM propagation

# 3) Gateway with a JWT authorizer pointing at the Cognito pool
gw = ctl.create_gateway(
    name=f"{args.name}-{suffix}", roleArn=role["Arn"], protocolType="MCP",
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC", "instructions": "Acme order and inventory tools."}},
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration={"customJWTAuthorizer": {
        "discoveryUrl": f"https://cognito-idp.{args.region}.amazonaws.com/{pool['Id']}/.well-known/openid-configuration",
        "allowedClients": [client["ClientId"]],
    }},
)
while ctl.get_gateway(gatewayIdentifier=gw["gatewayId"])["status"] not in ("READY", "FAILED"):
    time.sleep(5)

# 4) Lambda target with an inline tool schema (the schema is what agents see)
ctl.create_gateway_target(
    gatewayIdentifier=gw["gatewayId"], name="orders",
    targetConfiguration={"mcp": {"lambda": {"lambdaArn": args.lambda_arn, "toolSchema": {"inlinePayload": [
        {"name": "get_order", "description": "Get status and carrier for an order id like A-1001.",
         "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
        {"name": "check_stock", "description": "Units available for a SKU like SKU-1.",
         "inputSchema": {"type": "object", "properties": {"sku": {"type": "string"}}, "required": ["sku"]}},
        {"name": "issue_refund", "description": "Refund an order. Amount in USD.",
         "inputSchema": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
                         "required": ["order_id", "amount"]}},
    ]}}}},
    credentialProviderConfigurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}],
)

out = {
    "gatewayId": gw["gatewayId"], "gatewayUrl": gw["gatewayUrl"], "region": args.region,
    "tokenUrl": f"https://{domain}.auth.{args.region}.amazoncognito.com/oauth2/token",
    "clientId": client["ClientId"], "clientSecret": client["ClientSecret"], "scope": "acme-tools/invoke",
    "cleanup": {"userPoolId": pool["Id"], "domain": domain, "roleName": role_name},
}
json.dump(out, open("gateway.json", "w"), indent=2)
print("Gateway ready:", gw["gatewayUrl"], "\nSaved gateway.json (contains a client secret — do not commit it).")
