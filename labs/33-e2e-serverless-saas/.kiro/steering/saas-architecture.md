---
inclusion: always
---
# SaaS architecture rules

- **Tenancy:** pooled model. Every DynamoDB item key starts with `TENANT#<tenantId>`. Every Lambda reads `tenantId` from the authorizer context — never from the request body.
- **Isolation:** tenant-scoped IAM via session tags (`aws:PrincipalTag/tenantId`) and DynamoDB `dynamodb:LeadingKeys` conditions.
- **Identity:** Cognito user pool with a `custom:tenantId` attribute; API Gateway JWT authorizer.
- **Tiers:** `basic` (shared throughput), `premium` (higher usage-plan limits). Tier read from the tenant record.
- **Metering:** emit `TenantUsage` EMF metrics with dimensions `tenantId`, `feature`.
- **IaC:** CDK v2 TypeScript; one stack per bounded context; cdk-nag AwsSolutions must pass.
- **Every endpoint** has an EARS acceptance criterion and an integration test that proves tenant A cannot read tenant B's data.
