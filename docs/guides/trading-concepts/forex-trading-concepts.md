# Trading concepts in the SDK

This page explains the terms used by FiveTwenty models and endpoints. It focuses
on interpreting API data rather than selecting a trading strategy.

## Instruments, units and prices

OANDA instrument names use values such as `EUR_USD`. For a currency pair, the first
currency is the base and the second is the quote. A EUR/USD price describes quote
currency per unit of base currency. Positive order units request a buy; negative
units request a sell.

Use `get_account_instruments()` to discover instruments available to the account.
An `InstrumentName` enum member is a convenient name, not proof of availability.
Metadata includes minimum trade size, unit precision, display precision and pip
location. These properties are not interchangeable.

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def show_precision(client: AsyncClient) -> None:
    response = await client.accounts.get_account_instruments(
        client.account_id, instruments=["EUR_USD"]
    )
    for instrument in response["instruments"]:
        pip_size = Decimal(10) ** instrument.pip_location
        print(instrument.name, pip_size, instrument.minimum_trade_size)
```

A pip's size is `10 ** pip_location`; it is not always `0.0001`. See
[OANDA's instrument definitions](https://developer.oanda.com/rest-live-v20/primitives-df/)
for metadata semantics.

## Orders, trades and positions

| Object | What it represents | Useful identifier |
|---|---|---|
| Order | A request with execution conditions | Order ID |
| Trade | Exposure opened by a fill, with its own remaining units and dependent orders | Trade ID |
| Position | Aggregate long and short sides for an instrument | Instrument name |
| Transaction | An account event such as creation, fill, cancellation or financing | Transaction ID |

An order fill can open, reduce or close trades according to its position-fill
setting and account rules. A trade's `current_units` can differ from
`initial_units` after a partial reduction.

A position can have both long and short sides. Their sum is net units, but a net
value of zero does not imply that no trades or gross exposure remain. Use explicit
trade or position-close endpoints when the intent is to remove exposure.

## Bid, ask and liquidity

Bid prices are relevant to selling and ask prices to buying. A price snapshot can
contain several liquidity buckets; top-of-book prices do not guarantee a complete
fill at that level. `closeout_bid` and `closeout_ask` are closeout prices, not a
replacement for the executable liquidity buckets when estimating an entry.

The difference between bid and ask is the spread. Total trading cost can also
include commissions, financing and other account-specific charges.

OANDA order-book and position-book snapshots describe distributions of client
orders or positions. They are not an exchange's complete executable order book.
See [market-data models](../../api-reference/models/market-data-models.md).

## Balance, NAV and margin

`balance` records the account balance, while `nav` reflects net asset value,
including unrealized profit/loss. `margin_used`, `margin_available` and
`margin_closeout_percent` describe different account conditions. Use OANDA's returned
values rather than defining a margin call as “margin used approaches balance.”

Available margin is not a safe loss budget. A proposed order can change margin and
exposure, and prices can change between a read and execution. Account and instrument
rules determine the actual requirements.

## Profit/loss and currency conversion

Unrealized P/L describes open exposure; realized P/L records completed reductions
or closures. Their model fields are decimals in Python. For a simple currency
trade, signed units multiplied by the exit-minus-entry price change gives a
quote-currency price-movement component. It excludes costs and conversion to the
account currency.

Use the API's reported P/L and conversion data for account reporting. Do not add
amounts from different currencies or reuse one conversion factor for every gain,
loss and position direction without checking its meaning.

## Market conditions and account rules

Trading hours, instruments, hedging behavior and guaranteed-stop features vary.
Check current account configuration and instrument status. A sampled price stream
and a historical backtest do not describe every execution condition.

Continue with [order types](order-types.md), [streaming](streaming.md) or the
[risk-calculation tutorial](../../tutorials/risk-management.md).
