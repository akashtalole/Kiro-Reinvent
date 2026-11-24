"""Continuously evaluate a deployed agent: sample live sessions from its CloudWatch telemetry and score
them with built-in evaluators. Results land as logs + CloudWatch metrics you can alarm on.

    python create_online_eval.py --service-name <agent service name, e.g. acme_support.DEFAULT> \
        --role-arn arn:aws:iam::<acct>:role/agentcore-eval-role
List evaluators available in your region with:  aws bedrock-agentcore-control list-evaluators
"""
import argparse

import boto3

ap = argparse.ArgumentParser()
ap.add_argument("--service-name", required=True)
ap.add_argument("--role-arn", required=True)
ap.add_argument("--region", default="us-east-1")
ap.add_argument("--sample", type=float, default=20.0, help="percent of sessions to evaluate")
args = ap.parse_args()

ctl = boto3.client("bedrock-agentcore-control", region_name=args.region)
resp = ctl.create_online_evaluation_config(
    onlineEvaluationConfigName="acme_support_online",
    description="Helpfulness, goal success and harmfulness on sampled production sessions",
    rule={
        "samplingConfig": {"samplingPercentage": args.sample},
        "sessionConfig": {"sessionTimeoutMinutes": 15},   # a session is evaluated after 15 idle minutes
    },
    dataSourceConfig={"cloudWatchLogs": {"serviceNames": [args.service_name], "logGroupNames": ["aws/spans"]}},
    evaluators=[{"evaluatorId": e} for e in ("Builtin.Helpfulness", "Builtin.GoalSuccessRate", "Builtin.Harmfulness")],
    outputConfig={"cloudWatchConfig": {"resultDestination": "DEDICATED_LOG_GROUP", "metricsNamespace": "AcmeSupport/Evals"}},
    evaluationExecutionRoleArn=args.role_arn,
    enableOnCreate=True,
)
print({k: resp.get(k) for k in ("onlineEvaluationConfigId", "status")})
