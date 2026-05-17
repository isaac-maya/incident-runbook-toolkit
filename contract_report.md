# API / Service Contract Report

This companion report captures the boundary failures that should become automated checks, so the next incident is less likely to escape into downstream systems.

| Incident | Service | Boundary failure | Recommended test |
| --- | --- | --- | --- |
| INC-2401 | auth-api | token refresh response missing expires_at for 2.4% of calls | contract test asserting required auth response fields are always present |
| INC-2402 | billing-events | amount field changed from number to string in one producer | schema registry compatibility check blocking incompatible producer deploys |

## Takeaway

The recurring reliability risk is not only service health; it is weak contract confidence at system boundaries. The fix is to pair incident runbooks with automated contract checks that fail before downstream teams discover drift.
