# Advanced order workflows

These tutorials explain conditional entry orders, dependent order updates and
coordination across multiple requests. Start with the
[order types guide](../../guides/trading-concepts/order-types.md) and a working
[practice account](../getting-started/authentication.md).

| Tutorial | Focus |
| --- | --- |
| [Stop and market-if-touched orders](stop-orders-mit.md) | Select and submit a server-side entry trigger |
| [Dynamic order management](dynamic-management.md) | Update trailing and fixed stops on a known trade |
| [Order combinations](order-strategies.md) | Attach on-fill details and manage partial outcomes |

Examples that submit or update orders require practice mode. Prices and sizes are
inputs supplied by the caller, not recommended trading levels. Request models
check local constraints; account eligibility and execution remain server decisions.

Multiple requests are not an atomic batch. A coordinated strategy must track each
outcome, including requests whose responses were lost, before issuing more writes.
