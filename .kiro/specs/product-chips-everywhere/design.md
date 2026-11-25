# Design — Product chips everywhere

- **Lab page (`site/lab.html`):** after the existing service chips, render `lab.products` as `<a class="chip accent" href="labs.html?product=…">`. Escape with `K.esc` and encode with `encodeURIComponent`.
- **Search (`site/assets/site.js`, `render(q)`):** add `l.products` to the haystack. If `q` case-insensitively equals or prefixes a product name, prepend a synthetic result linking to `labs.html?product=…`.
- **Home (`site/index.html`):** new chip row under the hero stats, counts from `labs.json`, zero counts hidden.

## Correctness properties
- **P1:** for any product name, the generated href decodes back to the same name (round-trip through `encodeURIComponent` + `URLSearchParams`).
- **P2:** the sum of home-page counts ≥ the number of labs (labs can have several products), and each count equals the labs page's filtered count for that product.
- **P3:** search results for a product query ⊇ the labs page's filtered list for that product.

Write P1 and P2 as Playwright checks; P2's count equality can be a property over every product in `labs.json`.
