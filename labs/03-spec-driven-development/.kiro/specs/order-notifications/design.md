# Design Document — Order notifications

## Overview
Event-driven fan-out on AWS serverless primitives.

## Architecture
```mermaid
flowchart LR
  orders[Orders service] -- OrderShipped --> eb[(EventBridge bus)]
  eb --> rule[Rule: detail-type=OrderShipped]
  rule --> q[SQS notify-queue]
  q --> fn[Lambda notifier]
  fn --> prefs[(DynamoDB preferences)]
  fn --> ses[SES email]
  fn --> sns[SNS mobile push]
  q -. after 3 attempts .-> dlq[SQS DLQ]
  dlq --> alarm[CloudWatch alarm]
```

## Components and interfaces
| Component | Responsibility | Interface |
| --- | --- | --- |
| `notifier` Lambda | Load prefs, send per channel, idempotency | SQS batch event, partial batch failure |
| `preferences` table | PK `customerId`; attrs `email`, `push`, `updatedAt` | GetItem |
| `idempotency` table | PK `eventId#channel`, TTL 7 days | conditional PutItem |

## Data models
```ts
type OrderShipped = { eventId: string; orderId: string; customerId: string; shippedAt: string };
```

## Error handling
Retries via SQS `maxReceiveCount=3`; Lambda returns `batchItemFailures`.

## Testing strategy
Unit tests for preference filtering and idempotency; property test: for any sequence of duplicate events, sends per (eventId, channel) ≤ 1.
