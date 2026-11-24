---
id: 44
title: "Field pattern: agent-guided model fine-tuning with Kiro in SageMaker AI"
category: End-to-end solutions
level: Advanced
duration: 3 h
summary: Use Kiro (pre-configured over ACP in SageMaker AI Studio JupyterLab) plus SageMaker AI's model-customization skills to go from a use-case description to a fine-tuned, evaluated and deployed model — SFT, DPO or RLVR — with editable notebooks at each step.
services: [Kiro, Amazon SageMaker AI, SageMaker Studio JupyterLab, ACP, Agent Skills, Amazon Bedrock]
tags: [fine-tuning, SFT, DPO, RLVR, LLM-as-judge, skills, ACP, field pattern]
---

# Lab 44 · Field pattern: agent-guided model fine-tuning with Kiro in SageMaker AI

> **Outcome:** A small language model fine-tuned for step-by-step clinical-style reasoning, evaluated with LLM-as-a-judge, and deployed to a SageMaker AI endpoint or Bedrock. Kiro drives each step and leaves editable notebooks behind.

> **From the field:** [Agent-guided workflows to accelerate model customization in Amazon SageMaker AI](https://aws.amazon.com/blogs/machine-learning/agent-guided-workflows-to-accelerate-model-customization-in-amazon-sagemaker-ai/) (AWS ML Blog, May 2026). JupyterLab in SageMaker AI Studio supports coding agents over **ACP**, and **Kiro is pre-configured** in its chat panel. The space automatically loads nine model-customization **Agent Skills**. Other ACP agents can be added and get the same skills: Claude Code (`@zed-industries/claude-agent-acp`), Codex, Gemini and OpenCode.

## The workflow

```mermaid
flowchart LR
  P["'I want to customize a model'"] --> UC[Use-case spec skill]
  UC --> PL[Planning skill<br/>multi-step plan]
  PL --> FS[Fine-tuning setup<br/>base model + technique]
  FS --> DE[Dataset evaluation] --> DT[Dataset transformation]
  DT --> FT[Fine-tuning<br/>serverless training notebook]
  FT --> EV[Model evaluation<br/>LLM-as-judge]
  EV --> DP[Deployment<br/>SageMaker endpoint or Bedrock]
```

| Skill | Phase |
| --- | --- |
| Use Case Specification · Planning | Discovery and configuration |
| Fine-tuning Setup | Picks a base model from SageMaker AI Hub and recommends SFT, DPO or RLVR |
| Dataset Evaluation · Dataset Transformation | Validates the schema and converts between OpenAI chat, SageMaker, Hugging Face and Nova formats |
| Fine-tuning | Generates serverless training notebooks |
| Model Evaluation | LLM-as-judge with built-in and custom metrics |
| Model Deployment | Picks the SageMaker endpoint or Bedrock route and generates the code |

| Technique | Trains on | Best for |
| --- | --- | --- |
| SFT | Input/output pairs | Task behavior, format compliance, domain answers |
| DPO | Preferred vs rejected outputs | Tone, style, preferences |
| RLVR | Code-based reward functions | Tasks where correctness can be checked programmatically |

## Step 1 — Space and sign-in

1. Open a SageMaker AI Studio **JupyterLab** space on SageMaker AI Distribution 4.1 or later. The post states no minimum instance type.
2. Set up the execution role as the post describes:
   - attach `AmazonSageMakerFullAccess`;
   - add an inline policy for Lambda, S3 and Bedrock;
   - make sure the trust policy covers `sagemaker`, `lambda` and `bedrock`.
3. Open the chat panel, type `@` and pick **@Kiro**. On first use, sign in from a terminal:

```bash
kiro-cli login --use-device-flow
```

## Step 2 — Describe the use case

```text
@Kiro I want to customize a model: a small model that reasons step by step through
medical cases before giving a diagnosis, trained on FreedomIntelligence/medical-o1-reasoning-SFT.
```

The agent **plans before it acts**. It activates the specification and planning skills and proposes a plan that names the technique (SFT here), the base model, data checks and evaluation metrics. Review the plan before you approve it.

## Step 3 — Run the plan

Approve each phase. Each one produces a notebook you can edit and re-run in your own ML pipeline: data validation and transformation, serverless fine-tuning, evaluation against the base model, then deployment.

## Step 4 — Make the skills yours

The skills follow the Agent Skills format and are fully editable. Encode your team's governance in them, for example:

- approved base models;
- a mandatory evaluation set;
- PII checks before training;
- deployment only to private endpoints.

Version the skills in git like code (see [Lab 07](../07-agent-skills/README.md) and [Lab 41](../41-domain-skills-at-scale/README.md)).

## Guardrails

- This is a demonstration domain. Fine-tuned medical-reasoning models aren't clinical tools.
- Delete endpoints after evaluation, because they bill hourly.
- Keep training data in your account's S3 bucket, with encryption and least-privilege roles.

## Learn more

- [SageMaker AI model customization](https://docs.aws.amazon.com/sagemaker/) · [Agent Client Protocol](https://agentclientprotocol.com/) · [Lab 11 — ACP](../11-acp-editor-integration/README.md)
