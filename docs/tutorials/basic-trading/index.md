# Basic trading with FiveTwenty

These lessons explain how to read OANDA data, distinguish trades from positions,
and keep decision logic separate from account operations. They build on
[authentication](../getting-started/authentication.md) and the
[practice trade lifecycle](../getting-started/first-trade.md).

| Lesson | What you will do |
| --- | --- |
| [Model and numeric basics](foundation.md) | Use typed response values and instrument metadata |
| [Market data](market-data.md) | Read quotes and completed candles |
| [Position management](position-management.md) | Inspect exposure and close a specific trade |
| [Strategy building](strategy-building.md) | Write and test a signal calculation without submitting orders |
| [Assembling a workflow](complete-system.md) | Connect reads, calculations and a decision preview |

The examples assume Python 3.10 or later and a configured practice account. A
helper function is intended to be called inside an existing client context; blocks
with `asyncio.run(main())` are complete scripts. Each lesson states whether its
example changes account state.

These are SDK lessons, not validated trading strategies. A successful API call or a
working signal calculation does not establish profitability. For order behavior,
continue with [advanced orders](../advanced-orders/index.md); for limits of sizing
calculations and protective orders, read [risk management](../risk-management.md).
