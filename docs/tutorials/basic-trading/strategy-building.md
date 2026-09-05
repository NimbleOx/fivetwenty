# Build a testable signal calculation

A signal is an input to a decision, not an instruction that must place an order.
Keep the calculation independent of networking so you can test it with known data
and decide separately how it affects an account.

## Compare two moving averages

The following function classifies the latest window. It does not detect a crossover:
a crossover requires comparing the previous and current relationship as well.

```python
from decimal import Decimal
from collections.abc import Sequence
from typing import Literal


def moving_average_signal(
    closes: Sequence[Decimal], short_window: int = 5, long_window: int = 20
) -> Literal["above", "below", "equal"]:
    if not 0 < short_window < long_window:
        message = "Require 0 < short_window < long_window"
        raise ValueError(message)
    if len(closes) < long_window:
        message = "Not enough completed candles"
        raise ValueError(message)
    short_average = sum(closes[-short_window:], Decimal("0")) / short_window
    long_average = sum(closes[-long_window:], Decimal("0")) / long_window
    if short_average > long_average:
        return "above"
    if short_average < long_average:
        return "below"
    return "equal"


print(moving_average_signal([Decimal("1.10")] * 20))  # equal
```

Supply completed candles in chronological order, as in the
[market-data lesson](market-data.md). Keep the instrument, granularity and final
candle timestamp with the result. Reprocessing the same candle should not silently
create another order.

## Test the meaning of the signal

Useful cases include a constant series, rising and falling series, insufficient
history, invalid window lengths, and exact equality. Test the expected relationship
with small inputs you can calculate by hand. A test that only checks that the
function returns a string adds little confidence.

An application's next decision also depends on its existing trades, pending
orders, data freshness and configured limits. Evaluate those inputs before deciding
whether to submit, hold, reduce or cancel anything.

## Evaluate a strategy separately

This example makes no claim that the signal predicts future prices. A backtest must
define when data becomes available, when an order could execute, and which bid/ask
prices, costs and execution assumptions apply. Using a candle's final close before
that candle ends introduces look-ahead bias.

Keep data used to choose parameters separate from data used to evaluate them.
Report assumptions and sensitivity to costs rather than presenting one optimized
historical result as expected performance. The [notebooks](../../examples.md)
include analysis exercises, not a broker execution simulator.

Continue with [assembling a workflow](complete-system.md).
