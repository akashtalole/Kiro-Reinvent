# Tasks — Site catalog and product filter

- [x] 1. Derive products in the build
  - [x] 1.1 Add `PRODUCTS` and `products_for` with explicit-override validation _(R2.1–2.3)_
  - [x] 1.2 Emit `products` in `labs.json`; add `add_scenario_products` _(R2.5)_
- [x] 2. Product chip rows on labs, use cases and scenarios, kept in the URL _(R2.6)_
- [x] 3. Pretty-URL aliases `/crew/`, `/frontier/`, `/internals/` _(R3.1–3.2)_
- [x] 4. Property tests with Hypothesis for P1–P6 and integrity tests E1 _(R1–R4)_
  - [x] 4.1 **P1 found a bug:** a quoted list item containing a comma (`["a, b"]`) was split in two. Fixed with quote-aware `split_list` _(R1.3)_
- [x] 5. Run tests in CI and in the "Done means green" Stop hook
