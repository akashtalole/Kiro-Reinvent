# Requirements — Tenant onboarding

## Requirement 1 — Self-service sign-up
**User story:** As a prospective customer, I want to sign up my company, so that my team can start using the product.
1. WHEN a sign-up request with company name, admin email and tier is received THE SYSTEM SHALL create a tenant record, a Cognito admin user with `custom:tenantId`, and return 201 within 3 seconds.
2. IF the company name is already registered THEN THE SYSTEM SHALL return 409 without creating any resources.
3. WHEN onboarding fails after partial creation THE SYSTEM SHALL roll back created resources (Step Functions saga).

## Requirement 2 — Tenant isolation
1. THE SYSTEM SHALL reject any data-plane request whose JWT `custom:tenantId` does not match the resource's tenant with 403.
2. WHILE a tenant is `SUSPENDED` THE SYSTEM SHALL reject all data-plane requests with 423.

## Requirement 3 — Tiering and metering
1. WHEN a `basic` tenant exceeds 100 requests/minute THE SYSTEM SHALL return 429.
2. THE SYSTEM SHALL emit per-tenant usage metrics for every billable operation.
