# Practice and live environments

OANDA exposes separate practice and live hosts. Practice accounts use virtual
funds; live accounts can create financial obligations. The SDK selects hosts from
the resolved account configuration.

| Service | Practice | Live |
|---|---|---|
| REST | `https://api-fxpractice.oanda.com/v3` | `https://api-fxtrade.oanda.com/v3` |
| Streaming | `https://stream-fxpractice.oanda.com/v3` | `https://stream-fxtrade.oanda.com/v3` |

These addresses are listed in OANDA's [development guide](https://developer.oanda.com/rest-live-v20/development-guide/).
Account availability, instruments and order features depend on the OANDA division
and account; a practice account is not a promise of identical live execution.

## Verify the resolved environment

For scripts using environment-variable configuration, check the client after it
has resolved those variables:

```python
from fivetwenty import Client, Environment

with Client() as client:
    if client.config.environment != Environment.PRACTICE:
        message = "This script requires a practice account"
        raise ValueError(message)
    print(client.config.summary())
```

This check makes no request. The next account read can establish whether the token
has access to the configured account. Token text cannot reliably identify the
environment or prove account permissions.

## Keep configuration explicit

Use distinct aliases and secret-store entries for practice and live deployments.
Do not switch a running client's private environment fields or HTTP base URL.
Create a new client with the intended configuration and close the old one.

A constructor argument does not always override environment variables or a supplied
configuration object. Follow the [configuration precedence rules](configuration.md#configuration-priority).
In particular, `AsyncClient(environment=Environment.PRACTICE)` alone does not
force a process configured for live access into practice mode.

## What practice testing establishes

Practice testing can reveal invalid requests, response-shape errors and resource
cleanup problems. It cannot establish live liquidity, latency, slippage, costs or
strategy profitability. Historical backtesting is a separate task from making
requests against a practice account.

Use deterministic HTTP mocks for simulated timeouts, rejected requests and failure
sequences. Live integration tests should run on an isolated practice account; see
the [testing guide](../../contributing/testing-guide.md).

## Before enabling live requests

Make the target alias, account and environment visible to the application's
operator without printing the token. Verify account access with a read-only request,
keep an audit of submitted requests and outcomes, and define how the application
reconciles an order whose response is lost. The SDK does not provide a live-trading
confirmation prompt or a strategy risk engine.

See [configure live access](../practical-solutions/setup-live-trading.md) for a
read-only verification example and [connection failures](../practical-solutions/handle-connection-failures.md)
for uncertain write outcomes.
