# Design — Site catalog and product filter

## Overview
`scripts/build_site.py` stays dependency-free (Python 3.9+). Products are derived at build time so the browser only filters precomputed arrays.

## Components
| Component | Responsibility |
| --- | --- |
| `split_list` / `parse_scalar` / `parse_front_matter` | Minimal YAML-subset parser: ints, quoted strings, flow lists with quote-aware splitting |
| `PRODUCTS` + `products_for(services, explicit)` | Ordered `(name, regex)` table; explicit `products:` overrides |
| `add_scenario_products` | Writes `products` into `_site/data/scenarios.json` from labs + services |
| `write_stub` / `write_pretty_urls` | Redirect stubs with a relative target `"../" * depth + target` |
| `labs.html`, `use-cases.html`, `scenarios.html` | A `Product` chip row; state in `URLSearchParams`; `aria-pressed` on chips |

## Data
- `_site/data/labs.json` → `{categories, levels, products, labs[{…, products}]}`
- `_site/data/scenarios.json` → each scenario gains `products`; top level gains `products`

## Correctness properties (checked with Hypothesis in `tests/test_build_site_properties.py`)
| # | Property | Requirement |
| --- | --- | --- |
| P1 | Serialising any front-matter dict (ints, strings with `:`, `,`, `#`, `[]`, lists) and parsing it returns the same dict | 1.1–1.4 |
| P2 | `products_for` returns a duplicate-free subsequence of `PRODUCT_NAMES` | 2.1 |
| P3 | Explicit products round-trip in canonical order | 2.2 |
| P4 | AgentCore-only services never yield Amazon Bedrock | 2.3 |
| P5 | `products_for(a) ⊆ products_for(a + b)` (monotonic) | 2.4 |
| P6 | For any directory depth, the stub's target resolves to the intended page | 3.1 |
| E1 | Every path and use-case lab id exists; every lab has ≥ 1 product (example-based over real data) | 4.1–4.2 |

## Error handling
Front-matter and scenario errors print every problem, then exit 1, so CI shows all of them at once.
