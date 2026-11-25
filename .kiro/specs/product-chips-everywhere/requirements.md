# Requirements — Product chips everywhere

## Introduction
The Product filter exists on list pages, but a reader on a lab page or in the ⌘K search can't see or jump to a product. This spec is **not implemented yet**: run it in Kiro (IDE spec mode, or `kiro-cli` with `/spec`) to build it.

## Requirement 1 — Product chips on lab pages
**User story:** As a learner on a lab page, I want to see which products the lab covers and jump to every lab for that product.

#### Acceptance criteria
1. WHEN a lab page renders THE SYSTEM SHALL show one chip per product from `labs.json`, in canonical order.
2. WHEN a user clicks a product chip THE SYSTEM SHALL open `labs.html?product=<name>`.
3. THE SYSTEM SHALL render chips with no horizontal scroll at 390 px width.

## Requirement 2 — Product search in ⌘K
**User story:** As a reader, I want typing a product name in the search dialog to find its labs.

#### Acceptance criteria
1. WHEN the query matches a product name THE SYSTEM SHALL include that product's labs in the results.
2. THE SYSTEM SHALL show a "All <product> labs →" result first that opens the filtered labs page.

## Requirement 3 — Product counts on the home page
**User story:** As a first-time visitor, I want to see how many labs each product has.

#### Acceptance criteria
1. THE SYSTEM SHALL show a row of product chips with counts computed from `labs.json` at page load.
2. IF a product has zero labs THEN THE SYSTEM SHALL hide its chip.
