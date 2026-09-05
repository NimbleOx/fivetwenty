# Guides

Use these guides to understand SDK behavior or solve a specific integration problem.
For a first connection, start with the [tutorials](../tutorials/index.md).

## Understand the library

- [SDK architecture](understanding/sdk-architecture.md): how requests, response models and streams fit together.
- [Async and sync clients](understanding/async-vs-sync.md): choose an execution model and manage its lifetime.
- [Configuration](understanding/configuration.md): supply credentials and understand precedence.
- [Practice and live environments](understanding/environments.md): select and verify the target account.
- [Application patterns](understanding/best-practices.md): connection reuse, decimal arithmetic and error handling.

## Understand OANDA data

- [Forex concepts](trading-concepts/forex-trading-concepts.md): instruments, units, prices, margin and currency conversion.
- [Market data and streaming](trading-concepts/streaming.md): snapshots, sampled pricing updates and transaction records.
- [Order types](trading-concepts/order-types.md): pending orders, position effects and dependent orders.

## Complete an API task

- [Configure live access](practical-solutions/setup-live-trading.md).
- [Handle connection failures](practical-solutions/handle-connection-failures.md).
- [Close a trade or position](practical-solutions/close-positions.md).
- [Create, replace and cancel orders](practical-solutions/manage-orders-effectively.md).
- [Manage stop-loss orders](practical-solutions/implement-stop-loss-strategies.md).
- [Configure multiple accounts](practical-solutions/multi-account-configuration.md).

## Measure and improve performance

The [performance guides](optimization/index.md) cover connection reuse, bounded
stream processing, memory usage and latency measurement. They do not promise an
execution speed or fill rate; measure those in your application and environment.

Use the [API reference](../api-reference/index.md) alongside these guides when you
need a full parameter table or return type.
