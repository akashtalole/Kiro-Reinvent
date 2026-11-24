# Setup guide

## Accounts

- **Kiro account.** The free tier is enough for most labs. Headless CI (Lab 10) and the autonomous agent (Lab 14) need a paid plan.
- **AWS account.** Use a sandbox or dev account. Never run labs against production.
- **Bedrock model access.** Labs 21–37 need access to an Anthropic Claude model (or another tool-capable model) in your region.

## Tools

| Tool | Install | Used by |
| --- | --- | --- |
| Kiro CLI | `curl -fsSL https://cli.kiro.dev/install \| bash` | most labs |
| Kiro IDE | [kiro.dev/downloads](https://kiro.dev/downloads/) | 03, 04, 08 |
| Kiro Crew | `curl -fsSL https://download.crew.kiro.dev/cli.sh \| sh` | 12, 13, 35 |
| AWS CLI v2 | [docs](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | AWS labs |
| uv / uvx | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | MCP servers |
| Node.js 20+ | [nodejs.org](https://nodejs.org) | CDK, AgentCore CLI |
| Python 3.12+ | [python.org](https://www.python.org) | Strands / AgentCore labs |
| AgentCore CLI | `npm install -g @aws/agentcore` | 26–34 |
| AWS CDK | `npm install -g aws-cdk` | 16, 33 |

## AWS credentials

```bash
aws configure sso --profile dev
export AWS_PROFILE=dev AWS_REGION=us-east-1
aws sts get-caller-identity
```

Lab 15 sets up a separate read-only role for agents. Use it.

## Python environment (per lab)

```bash
cd labs/<lab>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Preview the site locally

```bash
python scripts/build_site.py --serve     # http://localhost:8000
```

## Costs

Most labs cost cents. Several resources keep billing until you delete them: Gateways, Memory resources, Knowledge Bases (vector stores), and Runtime agents with traffic. Every lab ends with a **Clean up** section.
