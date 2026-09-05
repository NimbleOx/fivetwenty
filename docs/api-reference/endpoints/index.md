# API Endpoints Reference

**OANDA Reference**: [OANDA v20 REST API](https://developer.oanda.com/rest-live-v20/introduction/)

Endpoint methods are grouped by resource. Access each group through a client
attribute, such as `client.accounts` or `client.orders`. Some convenience methods
combine multiple HTTP requests; each method's page explains what it does.

---

## Quick Reference

### Endpoint Groups
| Endpoint | Purpose | Key Methods |
|----------|---------|-------------|
| [accounts](accounts.md) | Account management | `get_accounts()`, `get_account()`, `get_account_summary()`, `get_account_instruments()`, `patch_account_configuration()`, `get_account_changes()` |
| [instruments](instruments.md) | Instrument candles and books (`client.instruments`) | `get_instrument_candles()`, `get_instrument_order_book()`, `get_instrument_position_book()` |
| [orders](orders.md) | Order operations | `post_order()`, `post_market_order()`, `post_limit_order()`, `post_stop_order()`, `post_market_if_touched_order()`, `get_orders()`, `get_order()`, `cancel_order()`, `get_pending_orders()`, `put_order()`, `put_order_client_extensions()` |
| [trades](trades.md) | Trade management | `get_trades()`, `get_open_trades()`, `get_trade()`, `close_trade()`, `put_trade_client_extensions()`, `put_trade_orders()` |
| [positions](positions.md) | Position tracking | `get_positions()`, `get_open_positions()`, `get_position()`, `close_position()` |
| [pricing](pricing.md) | Market data | `get_pricing()`, `get_pricing_stream()`, `get_account_instrument_candles()`, `get_latest_candles()`, `stream_pricing_with_retries()` |
| [transactions](transactions.md) | Transaction history | `get_transactions()`, `get_transaction()`, `get_transactions_since_id()`, `get_transactions_stream()`, `get_transactions_range()`, `get_recent_transactions()` |

---

## Read the return type

Collection methods usually return dictionaries with lists of parsed models and
metadata. For example, `get_orders()` returns models in `response["orders"]` and a
transaction cursor in `response["lastTransactionID"]`. `get_accounts()` returns its
list directly.

Order responses vary with the outcome. Check the returned transaction fields to
determine whether an order was created, filled or cancelled.

Use the [client reference](../client.md) for setup and connection management, or the
[tutorials](../../tutorials/index.md) for complete workflows.
