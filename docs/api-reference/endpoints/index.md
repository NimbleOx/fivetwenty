# API Endpoints Reference

**OANDA Reference**: [OANDA v20 REST API](https://developer.oanda.com/rest-live-v20/introduction/)

Complete reference for all FiveTwenty endpoint implementations.

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

## Endpoint Organization

### **Account Management**
- **[Accounts Endpoint](accounts.md)** - Account information, configuration, and instruments

### **Trading Operations**
- **[Orders Endpoint](orders.md)** - Order placement, modification, and cancellation
- **[Trades Endpoint](trades.md)** - Trade management and monitoring
- **[Positions Endpoint](positions.md)** - Position tracking and management

### **Market Data**
- **[Pricing Endpoint](pricing.md)** - Real-time prices, account-specific candlesticks, and latest candle data
- **[Instruments Endpoint](instruments.md)** - Instrument candlestick data and order/position book snapshots (3 methods on `client.instruments`)

### **History & Monitoring**
- **[Transactions Endpoint](transactions.md)** - Transaction history and real-time streaming

---

## Need More Context?

- **Learn with [Tutorials](../../tutorials/index.md)** for hands-on guidance
- **Get guidance with [Guides](../../guides/index.md)** for both solutions and understanding

**Ready to explore?** Choose an endpoint above or browse the complete [Client API Reference](../client.md) for setup and configuration details.
