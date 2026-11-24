# AWS MCP servers catalog

A working map of AWS MCP servers, grouped by job. Source: [awslabs.github.io/mcp](https://awslabs.github.io/mcp/), which listed 63 servers as of November 2026, plus the AWS-managed servers. Package names follow `awslabs.<name>@latest` for `uvx`. Check each server's page for current flags.

## Managed (remote)

| Server | Endpoint / install | Notes | Lab |
| --- | --- | --- | --- |
| **AWS MCP Server** (preview) | `uvx mcp-proxy-for-aws@latest https://aws-mcp.us-east-1.api.aws/mcp` | APIs + docs + agent SOPs; SigV4; supersedes local aws-api + aws-knowledge | 15 |
| **AWS Knowledge** | `https://knowledge-mcp.global.api.aws` | Docs search/read, regional availability, skills; no auth | 09, 22 |
| **Amazon EKS / ECS / SageMaker** (preview) | Managed endpoints | Cluster and service troubleshooting | — |

## Infrastructure & deployment

| Server | Use for | Lab |
| --- | --- | --- |
| `aws-iac-mcp-server` | CDK / CloudFormation guidance, schemas, validation, compliance checks | 16 |
| `ccapi-mcp-server` | Cloud Control API resource CRUD | — |
| `aws-serverless-mcp-server` | SAM init/build/deploy, logs, metrics, web apps | 17 |
| `lambda-tool-mcp-server` | Expose selected Lambda functions as tools | 17 |
| `eks-mcp-server`, `ecs-mcp-server`, `finch-mcp-server` | Containers | — |
| Terraform MCP (AWS / HashiCorp) | Provider/module docs, checks | 16 |
| `aws-api-mcp-server` | AWS CLI-equivalent calls (local) | — |

## Data & analytics

| Server | Use for | Lab |
| --- | --- | --- |
| `dynamodb-mcp-server` | Data modeling guidance, table ops | 20 |
| `postgres-mcp-server`, `mysql-mcp-server`, Aurora DSQL | Aurora queries (use read-only) | 20 |
| `s3-tables-mcp-server` | Iceberg tables in S3 Tables | 20 |
| DocumentDB, Neptune, Keyspaces, ElastiCache/Valkey/Memcached, Timestream for InfluxDB, Redshift, Data Processing (Glue/EMR/Athena) | Specialised stores & processing | — |

## Cost & operations

| Server | Use for | Lab |
| --- | --- | --- |
| `aws-pricing-mcp-server` | List prices, estimates | 08, 18 |
| `billing-cost-management-mcp-server` | Cost Explorer, anomalies, Compute Optimizer, Savings Plans | 08, 18 |
| `cloudwatch-mcp-server` | Alarms, metrics, Logs Insights | 19 |
| `cloudwatch-appsignals-mcp-server` | Services, SLOs, traces | 19 |
| `cloudtrail-mcp-server` | Change history ("who did what") | 19 |
| Managed Prometheus, Well-Architected Security Assessment | Ops & posture | — |

## AI / ML

| Server | Use for | Lab |
| --- | --- | --- |
| `bedrock-kb-retrieval-mcp-server` | Query Bedrock Knowledge Bases | 37 |
| Bedrock AgentCore MCP server | AgentCore docs and guidance for building agents | 26 |
| Kendra, Q Business, Q index, SageMaker AI, Document Loader, Translate, Bedrock Custom Model Import | AI services | — |

## Integration, security & more

SNS/SQS, Amazon MQ, Step Functions tool, AppSync, OpenAPI, Location, IAM, AWS Security Agent, Support, HealthOmics/HealthImaging/HealthLake, IoT SiteWise, Registry of Open Data.

## Choosing where to connect them

| Consumer | How |
| --- | --- |
| Kiro (developer) | `.kiro/settings/mcp.json`, or bundled as a **power** for on-demand loading (Labs 08–09) |
| Kiro custom agent | `mcpServers` inside the agent file (Lab 05) |
| Your Strands agent (dev) | `MCPClient` stdio/HTTP (Lab 22) |
| Your agent (production) | Behind **AgentCore Gateway** as an MCP-server target (Lab 27) |
