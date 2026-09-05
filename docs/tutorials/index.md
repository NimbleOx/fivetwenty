# Tutorials

These tutorials introduce FiveTwenty through concrete API tasks. Start with a
practice account and run each example only after reading what it changes.

## Start here

1. [Install FiveTwenty](getting-started/installation.md) and choose a Python environment.
2. [Configure authentication](getting-started/authentication.md) and verify account access.
3. [Create and close a practice trade](getting-started/first-trade.md), inspecting the response at each step.

## Build on the basics

| Topic | What you will learn |
|---|---|
| [Trading basics](basic-trading/index.md) | Read prices and candles, track positions and separate signals from execution |
| [Additional order types](advanced-orders/index.md) | Use pending and dependent orders and inspect their lifecycle |
| [Risk calculations](risk-management.md) | Work with units, price distances and account-currency values |
| [Account management](account-management.md) | Read balances, margin and account changes |
| [Streaming data](streaming-data.md) | Consume typed pricing and transaction records and close streams |

Strategy examples illustrate application code. Their parameters and results are
not recommendations or evidence that a strategy will be profitable. Practice
execution is useful for API testing but does not predict live fills or returns.

## Other ways to learn

The [examples](../examples.md) page lists runnable scripts and six notebooks.
Use [guides](../guides/index.md) for a particular integration problem and the
[API reference](../api-reference/index.md) for exact signatures and response fields.

If an example fails, record the failing method, exception type and sanitized error
code. Check [connection and authentication troubleshooting](../guides/practical-solutions/handle-connection-failures.md)
before reporting an issue. Never include an API token in a report.
