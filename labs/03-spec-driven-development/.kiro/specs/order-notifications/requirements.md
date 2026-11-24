# Requirements Document — Order notifications

## Introduction
Customers want to know when their order changes state. The system sends email and push notifications on key transitions and lets customers control their preferences.

## Requirements

### Requirement 1 — Notify on state change
**User story:** As a customer, I want a notification when my order ships, so that I know when to expect it.

#### Acceptance criteria
1. WHEN an order transitions to `SHIPPED` THE SYSTEM SHALL publish an `OrderShipped` event within 5 seconds.
2. WHEN an `OrderShipped` event is received THE SYSTEM SHALL send a notification on every channel the customer has enabled.
3. IF a channel delivery fails THEN THE SYSTEM SHALL retry with exponential backoff up to 3 times and then route the message to a dead-letter queue.
4. THE SYSTEM SHALL deliver each notification at most once per channel per event (idempotency key = eventId + channel).

### Requirement 2 — Preferences
**User story:** As a customer, I want to choose channels, so that I'm not spammed.

#### Acceptance criteria
1. WHEN a customer updates preferences THE SYSTEM SHALL apply them to events received after the update.
2. WHILE a customer has opted out of all channels THE SYSTEM SHALL NOT send notifications and SHALL record the suppression.

### Requirement 3 — Observability
1. THE SYSTEM SHALL emit metrics `NotificationsSent`, `NotificationsFailed`, `DLQDepth` per channel.
2. WHEN `DLQDepth` > 0 for 5 minutes THE SYSTEM SHALL raise a CloudWatch alarm.
