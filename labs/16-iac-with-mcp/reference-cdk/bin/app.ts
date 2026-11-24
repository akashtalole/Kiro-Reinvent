#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { AwsSolutionsChecks } from "cdk-nag";
import { NotificationsStack } from "../lib/notifications-stack";

const app = new cdk.App();
const env = app.node.tryGetContext("env") ?? "dev";
new NotificationsStack(app, `Notifications${env[0].toUpperCase()}${env.slice(1)}Stack`, {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
  tags: { app: "order-notifications", env, owner: "platform-team" },
});
cdk.Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true }));
