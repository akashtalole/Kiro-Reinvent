# Bot: Cost sentinel (AWS)

**Responsibility:** Catch AWS spend surprises early.

**Agent:** custom agent with the `power-aws-cost-guard` power (Lab 08), read-only AWS profile.

**Trigger:** Daily 09:00.

**Do:** Compare yesterday's spend by service with the 14-day median; for any service > +30% and > $20/day, find the usage type driving it and the resources involved (CloudTrail for who/when). Post a short report with a suggested action.

**Never:** stop, delete or resize resources; change budgets or commitments.
