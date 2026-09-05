# Risk calculations and account controls

FiveTwenty exposes account metrics, instrument constraints and order operations.
Your application chooses its limits and actions. This page explains the inputs a
sizing calculation needs and the limits of protective orders; it does not prescribe
a risk percentage or trading strategy.

## Estimate loss in account currency

For an FX instrument, an entry-to-stop price difference is in quote currency per
base-currency unit. To compare it with an account-currency budget, include an
appropriate loss conversion factor. This simplified calculation excludes execution
slippage, gaps, fees and financing:

```python
from decimal import ROUND_DOWN, Decimal


def units_for_budget(
    budget: Decimal,
    entry: Decimal,
    stop: Decimal,
    loss_conversion: Decimal,
    units_precision: int,
) -> Decimal:
    if budget <= 0 or loss_conversion <= 0 or units_precision < 0:
        message = "Require positive budget/conversion and nonnegative precision"
        raise ValueError(message)
    distance = abs(entry - stop)
    if distance == 0:
        message = "Entry and stop must differ"
        raise ValueError(message)
    units = budget / (distance * loss_conversion)
    increment = Decimal("1").scaleb(-units_precision)
    return units.quantize(increment, rounding=ROUND_DOWN)
```

The result is an unsigned estimate, not an order request. The caller must select
direction, verify that the stop is on the intended side, and check minimum size,
maximum size, margin and other account constraints. If rounding leaves the size
below the minimum, do not silently increase it beyond the chosen budget.

When quote and account currency match, the conversion factor is one. Otherwise,
request home conversions from pricing and use the applicable loss conversion;
reject missing or invalid data. A gain conversion or position-value conversion
serves a different purpose. Other product types may require a different model.

## Request protective orders

On-fill stop details can be included in the entry request. Existing trade protection
can be created, replaced or cancelled through `put_trade_orders()`. Inspect the
response and resulting trade state before reporting which protection is present.

An ordinary stop loss specifies trigger behavior, not a guaranteed execution price
or maximum loss. Guaranteed-stop availability, requirements and costs depend on the
account and instrument. See [stop-loss operations](../guides/practical-solutions/implement-stop-loss-strategies.md).

## Define application limits precisely

A daily-loss rule needs a day boundary, time zone, starting value, treatment of
cash flows, and a decision about realized versus unrealized losses. A ratio needs
well-defined handling of zero or negative equity. Persist the state needed to
resume the same rule after a restart.

When a limit is reached, distinguish pausing new entries, cancelling pending
orders, and closing existing exposure. These are separate actions with separate
failure paths. The SDK has no automatic account-wide circuit breaker, and a local
flag cannot stop another process from submitting orders.

Test currency conversion, rounding boundaries, unavailable prices, stale account
data and unknown write outcomes before connecting these calculations to execution.
The [risk notebook](../examples.md) provides further exercises; its scenario values
are examples rather than recommended limits.
