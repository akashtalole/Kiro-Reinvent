# Requirements — Site catalog and product filter

## Introduction
The site is generated from lab folders. Each lab's front matter must parse exactly, every lab must be findable by the products it teaches, and short URLs must reach the real pages. This spec covers `scripts/build_site.py` and the filter UI on the labs, use cases and scenarios pages.

## Requirement 1 — Front matter parses exactly
**User story:** As a lab author, I want the front matter I write to appear on the site exactly as written, so that titles, services and tags are never mangled.

#### Acceptance criteria
1. WHEN a front-matter value is an integer THE SYSTEM SHALL parse it as an integer.
2. WHEN a value is a quoted string THE SYSTEM SHALL return the string without the quotes.
3. WHEN a value is a flow list `[a, "b, c"]` THE SYSTEM SHALL split it only on commas outside quotes.
4. THE SYSTEM SHALL return the first `# ` heading of the body as the lab heading.
5. IF a required field (`id`, `title`, `category`, `level`, `duration`, `summary`) is missing THEN THE SYSTEM SHALL fail the build and name the lab.

## Requirement 2 — Every lab is findable by product
**User story:** As a learner, I want to filter labs, use cases and scenarios by product (for example Kiro Crew), so that I can follow one product end to end.

#### Acceptance criteria
1. THE SYSTEM SHALL derive each lab's products from its `services` using one fixed, ordered product list.
2. WHEN a lab declares `products:` explicitly THE SYSTEM SHALL use exactly those, in canonical order, and SHALL fail the build on an unknown product.
3. THE SYSTEM SHALL NOT tag a lab as Amazon Bedrock only because it uses an AgentCore service.
4. WHEN services are added to a lab THE SYSTEM SHALL NOT remove any product it already had.
5. THE SYSTEM SHALL give each use case its lab's products and each scenario the union of its labs' and services' products.
6. WHEN a user selects a product chip THE SYSTEM SHALL show only matching items, keep the choice in the URL (`?product=`), and combine it with the other filters.

## Requirement 3 — Short URLs reach the real page
**User story:** As a reader sharing links, I want folder-style URLs such as `/crew/` or `/labs/51/`, so that links are short and stable.

#### Acceptance criteria
1. FOR every pretty URL THE SYSTEM SHALL write `<dir>/index.html` whose redirect target, resolved relative to `<dir>`, is the intended page.
2. THE SYSTEM SHALL keep the query string and fragment of the target.

## Requirement 4 — The catalog never points at nothing
**User story:** As a maintainer, I want broken references to fail CI, so that paths and use cases never link to a missing lab.

#### Acceptance criteria
1. THE SYSTEM SHALL fail the tests IF any learning path or use case references a lab id that does not exist.
2. THE SYSTEM SHALL fail the tests IF any lab has no product.
