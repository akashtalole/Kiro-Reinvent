"""Delete everything create_gateway.py created (reads gateway.json)."""
import json
import time

import boto3

cfg = json.load(open("gateway.json"))
s = boto3.session.Session(region_name=cfg["region"])
ctl, iam, cognito = s.client("bedrock-agentcore-control"), s.client("iam"), s.client("cognito-idp")
for t in ctl.list_gateway_targets(gatewayIdentifier=cfg["gatewayId"]).get("items", []):
    ctl.delete_gateway_target(gatewayIdentifier=cfg["gatewayId"], targetId=t["targetId"])
time.sleep(5)
ctl.delete_gateway(gatewayIdentifier=cfg["gatewayId"])
c = cfg["cleanup"]
iam.delete_role_policy(RoleName=c["roleName"], PolicyName="invoke-tools")
iam.delete_role(RoleName=c["roleName"])
cognito.delete_user_pool_domain(Domain=c["domain"], UserPoolId=c["userPoolId"])
cognito.delete_user_pool(UserPoolId=c["userPoolId"])
print("deleted")
