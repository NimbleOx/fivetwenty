# Model and numeric basics

FiveTwenty keeps OANDA's response structure while parsing nested objects into
Pydantic models. Most endpoint results are dictionaries: select the response key,
then use model attributes. This distinction makes the code easier to read and
preserves native numeric and datetime types.

## Read a model from a response

This read-only helper accepts a client that is already open:

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def show_balance(client: AsyncClient) -> Decimal:
    response = await client.accounts.get_account_summary(client.account_id)
    account = response["account"]
    print(f"Balance: {account.balance} {account.currency}")
    print(f"NAV: {account.nav} {account.currency}")
    return account.balance
```

`balance` and `nav` are `Decimal` values. Balance and net asset value describe
separate account metrics; unrealized profit or loss affects NAV. The response also
contains `lastTransactionID`, which is an account transaction cursor, not a balance.

`get_accounts()` is an exception to the usual envelope pattern: it returns a list
of account property models directly. Check each endpoint's documented return type.

## Construct decimal values deliberately

```python
from decimal import Decimal

bid = Decimal("1.10000")
ask = Decimal("1.10012")
spread = ask - bid
print(spread)  # 0.00012, in quote-currency price units
```

Strings avoid introducing a binary floating-point approximation before the decimal
is constructed. `Decimal` arithmetic still has a precision context and rounding
rules; it is not unlimited-precision arithmetic. Financial models use `Decimal`,
but elapsed seconds and retry delays use ordinary numeric timing values.

For FX, price is expressed in quote currency per base-currency unit. Do not treat a
price difference as account-currency profit. Conversion and costs may be needed.

## Read instrument constraints

Instrument metadata includes `pip_location`, `display_precision`,
`trade_units_precision` and `minimum_trade_size`. A pip's price size is
`Decimal("10") ** instrument.pip_location`; display precision is a separate concept.
Fetch metadata for the account and instrument you will use rather than assuming
all products accept integer units or five decimal places.

Request models validate supported local constraints and serialize field names for
the wire. OANDA still decides whether a request is valid for the current account,
price, margin and instrument conditions.

## Keep datetime objects until serialization

Time-bearing response attributes are Python `datetime` objects. Use timezone-aware
values for request boundaries. The client's `datetime_format` controls wire values
and the `Accept-Datetime-Format` header; it does not turn model attributes into
strings. Python datetime precision is microseconds, so sub-microsecond source
precision is not retained.

Use attributes for calculations. Compatibility access such as `model["openTime"]`
returns serialized values and can differ in type from `model.open_time`.

Continue with [market data](market-data.md), or consult the
[model reference](../../api-reference/models/index.md).
