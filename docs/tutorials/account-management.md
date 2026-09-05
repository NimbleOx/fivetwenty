# Read account state and build reports

Account summaries provide current account metrics. Detailed account, trade,
position and transaction endpoints provide the records needed to explain changes.
This tutorial reads those values; it does not modify account configuration.

## Read reported metrics

```python
from fivetwenty import AsyncClient


async def show_account_metrics(client: AsyncClient) -> None:
    response = await client.accounts.get_account_summary(client.account_id)
    account = response["account"]
    print(f"Currency: {account.currency}")
    print(f"Balance: {account.balance}; NAV: {account.nav}")
    print(f"Margin used: {account.margin_used}; available: {account.margin_available}")
    print(f"Margin closeout percent: {account.margin_closeout_percent}")
    print(f"Transaction cursor: {response['lastTransactionID']}")
```

Use the meanings in the [account model reference](../api-reference/models/account-models.md).
A custom `margin_used / nav` ratio is not interchangeable with OANDA's reported
margin-closeout metric. Do not label an account “safe” using a hardcoded percentage
without defining the metric and the applicable account rules.

## Maintain an account view

Read an initial account snapshot, then use account updates and transactions to
track changes. Preserve the relevant transaction cursor and apply updates in order.
A disconnected transaction stream does not supply a replay automatically; retrieve
missing records before considering a local view current.

Concurrent endpoint reads can observe different moments. If a report combines a
summary with separate trade and position reads, record when they were collected
and acknowledge that the result is not an atomic account snapshot.

## Interpret fills before calculating performance

An `ORDER_FILL` transaction can open a trade, reduce one or close one or more trades.
It is not necessarily a completed round trip. Counting profitable fill transactions
as winning trades can therefore produce a misleading win rate.

Define the reporting unit first: a trade ID, a completed strategy position, or a
period of account performance. Reconcile related transactions, partial closures,
financing, fees and cash movements as appropriate. Preserve account currency; do
not sum money from different accounts without conversion.

Transaction-list responses can return page URLs. Retrieve the referenced pages or
ID ranges to cover the intended interval instead of treating the page index as a
complete transaction history.

## Monitor multiple accounts

Use one explicitly configured client per account, and label every record with its
account ID and currency. The [multi-account guide](../guides/practical-solutions/multi-account-configuration.md)
shows environment prefixes and resource cleanup.

Separate accounts do not establish compliance with hedging or other account rules.
The SDK exposes configuration and data; it does not determine which arrangements
are permitted for an account holder.

Continue with [risk calculations](risk-management.md) and
[transaction endpoints](../api-reference/endpoints/transactions.md).
