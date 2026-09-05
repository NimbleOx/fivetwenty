# Bound memory and measure CPU work

Long-running applications usually benefit more from bounded storage and clear task
lifetimes than from custom object pools. Profile a representative workload before
changing data structures or numeric types.

## Bound retained data

Use a `deque(maxlen=...)` for rolling history, and keep only the fields needed by the
calculation. Persist older observations if the application needs an audit history.
The chosen window is an application decision; the SDK does not define one.

```python
from collections import deque
from decimal import Decimal

recent_spreads: deque[Decimal] = deque(maxlen=100)
recent_spreads.append(Decimal("0.00012"))
recent_spreads.append(Decimal("0.00014"))
mean_spread = sum(recent_spreads, Decimal("0")) / Decimal(len(recent_spreads))
print(mean_spread)
```

Also bound the number of worker tasks. A queue with a fixed capacity is ineffective
if each received message launches another untracked task.

## Preserve types at the trading boundary

Keep order quantities and monetary calculations in `Decimal`. Analytics libraries
may use floating-point arrays; that is a deliberate conversion with different
precision characteristics. Do not feed an analysis array directly into order
serialization or assume that converting a float back to `Decimal` recovers its
original decimal value.

Avoid changing the garbage collector, recycling mutable Pydantic objects or caching
bound methods unless measurements show a specific problem. These techniques can
make correctness and resource lifetime harder to verify.

## Profile allocations and CPU separately

Use `tracemalloc` to compare allocations around a repeatable workload and `cProfile`
to identify CPU-heavy functions. Distinguish retained objects from a temporary peak.
Record the input size, Python version and workload alongside the measurement.

For an asyncio application, CPU-heavy work can delay every request and heartbeat on
the same event loop. Consider a process worker for substantial CPU work and a thread
for blocking I/O, with explicit limits and shutdown behavior. Account for transfer
and coordination costs in the measurement.

## Check cleanup

After repeated connect/read/close cycles, inspect open tasks, threads and connections
as well as memory. Explicitly close clients and partially consumed streams. A stable
small test does not prove that an unbounded production workload will remain stable.

See [stream processing](streaming-optimization.md) for bounded consumption and
[latency measurement](latency-optimization.md) for elapsed-time measurements.
