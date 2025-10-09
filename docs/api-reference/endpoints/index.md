# API Endpoints Reference

**OANDA Reference**: [OANDA v20 REST API](https://developer.oanda.com/rest-live-v20/introduction/)

Complete reference for all FiveTwenty endpoint implementations.

---

## Quick Reference

### Endpoint Groups
| Endpoint | Purpose | Key Methods |
|----------|---------|-------------|
| [accounts](accounts.md) | Account management | `list()`, `get()`, `summary()`, `instruments()`, `configure()`, `changes()` |
| [orders](orders.md) | Order operations | `post_market_order()`, `post_limit_order()`, `cancel()`, `list_pending()`, `list()`, `replace()` |
| [trades](trades.md) | Trade management | `list_open()`, `get()`, `close()`, `modify()`, `list()` |
| [positions](positions.md) | Position tracking | `list_open()`, `get()`, `close()`, `list()` |
| [pricing](pricing.md) | Market data | `get()`, `stream()`, `candles()`, `latest_candles()` |
| [instruments](instruments.md) | Instrument data | `get_all()`, `candles()`, `order_book()` |
| [transactions](transactions.md) | Transaction history | `list()`, `get()`, `get_range()`, `stream()`, `list_since()` |

---

## Endpoint Organization

### **Account Management**
- **[Accounts Endpoint](accounts.md)** - Account information, configuration, and instruments

### **Trading Operations**
- **[Orders Endpoint](orders.md)** - Order placement, modification, and cancellation
- **[Trades Endpoint](trades.md)** - Trade management and monitoring
- **[Positions Endpoint](positions.md)** - Position tracking and management

### **Market Data**
- **[Pricing Endpoint](pricing.md)** - Real-time prices and account-specific candlesticks
- **[Instruments Endpoint](instruments.md)** - Instrument specifications and historical data

### **History & Monitoring**
- **[Transactions Endpoint](transactions.md)** - Transaction history and real-time streaming

---

## Need More Context?

- **Learn with [Tutorials](../../tutorials/index.md)** for hands-on guidance
- **Get comprehensive guidance with [Guides](../../guides/index.md)** for both solutions and understanding

**Ready to explore?** Choose an endpoint above or browse the complete [Client API Reference](../client.md) for setup and configuration details.
