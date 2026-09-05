# Guides

Use these guides to understand how FiveTwenty works or solve an integration problem.
For a first connection, start with the [tutorials](../tutorials/index.md).

## Understand the library

- [SDK architecture](understanding/sdk-architecture.md): how requests, response models and streams fit together.
- [Async and sync clients](understanding/async-vs-sync.md): choose a client and manage connections and streams.
- [Configuration](understanding/configuration.md): supply credentials and learn which settings take priority.
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

The [performance guides](optimization/index.md) explain how to reuse connections,
keep up with streams, control memory usage and measure latency. Start with
measurements from your application to decide which changes will help.

Use the [API reference](../api-reference/index.md) alongside these guides when you
need a full parameter table or return type.
