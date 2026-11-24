---
inclusion: always
---
# Tech stack

- Runtime: Node.js 20, ES modules, no TypeScript build step.
- Tests: `node --test`. Every new module ships with tests in `test/`.
- Infra: AWS CDK v2 (TypeScript) in `infra/`. Lambda + API Gateway HTTP API + DynamoDB.
- Do not add new runtime dependencies without asking.
