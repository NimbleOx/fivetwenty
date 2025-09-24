# Transactions Endpoint

📖 **OANDA Reference**: [Transaction Endpoints](https://developer.oanda.com/rest-live-v20/transaction-ep/)

Transaction history and monitoring.

---

## list
```python
# transactions.list(account_id: AccountID, from_time: str | None = None,
#                   to_time: str | None = None, page_size: int = 100,
#                   transaction_type: list[str] | None = None) -> dict[str, Any]

# Example usage:
transactions = await client.transactions.list(
    account_id="123-456-789",
    page_size=50,
    transaction_type=["ORDER_FILL", "MARKET_ORDER"]
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

📖 **OANDA Documentation**: [Get Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get transaction history for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_time` | str | ➖ | Start time for transaction range |
| `to_time` | str | ➖ | End time for transaction range |
| `page_size` | int | ➖ | Number of transactions per page (default: 100) |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transaction history

**Raises:**

- `FiveTwentyError` - API errors

---

## get
```python
# transactions.get(account_id: AccountID, transaction_id: str) -> dict[str, Any]

# Example usage:
transaction = await client.transactions.get(
    account_id="123-456-789",
    transaction_id="12345"
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/{transactionID}`

📖 **OANDA Documentation**: [Get Transaction](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction)

Get specific transaction details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Transaction identifier |

**Returns:** Dictionary containing transaction details

**Raises:**

- `FiveTwentyError` - API errors

---

## list_since
```python
# transactions.list_since(account_id: AccountID, transaction_id: str,
#                        transaction_type: list[str] | None = None) -> dict[str, Any]

# Example usage:
transactions = await client.transactions.list_since(
    account_id="123-456-789",
    transaction_id="100",
    transaction_type=["ORDER_FILL"]
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/sinceid`

📖 **OANDA Documentation**: [Get Transactions Since ID](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions-since-id)

Get transactions since specific transaction ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Starting transaction ID |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transactions since ID

**Raises:**

- `FiveTwentyError` - API errors

---

## stream
```python
# transactions.stream(account_id: AccountID, stall_timeout: float = 30.0) -> AsyncIterator[dict[str, Any]]

# Example usage:
async for transaction in client.transactions.stream(
    account_id="123-456-789",
    stall_timeout=60.0
):
    print(f"Transaction: {transaction}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/stream`

📖 **OANDA Documentation**: [Stream Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#stream-transactions)

Stream real-time transactions.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls (default: 30.0) |

**Returns:** AsyncIterator yielding transaction data

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - On stream timeout or connection issues

---

## get_range
```python
# transactions.get_range(account_id: AccountID, from_transaction_id: str,
#                       to_transaction_id: str, transaction_type: list[str] | None = None) -> dict[str, Any]

# Example usage:
transactions = await client.transactions.get_range(
    account_id="123-456-789",
    from_transaction_id="100",
    to_transaction_id="200"
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/idrange`

📖 **OANDA Documentation**: [Get Transaction Range](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction-range)

Get transactions in ID range.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_transaction_id` | str | ✅ | Starting transaction ID |
| `to_transaction_id` | str | ✅ | Ending transaction ID |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transactions in range

**Raises:**

- `FiveTwentyError` - API errors

---

## get_all
```python
# transactions.get_all(account_id: AccountID, count: int = 500,
#                     transaction_type: list[str] | None = None) -> dict[str, Any]

# Example usage:
all_transactions = await client.transactions.get_all(
    account_id="123-456-789",
    count=100,
    transaction_type=["ORDER_FILL", "MARKET_ORDER"]
)
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

📖 **OANDA Documentation**: [Get Recent Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get recent transactions for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `count` | int | ➖ | Number of recent transactions (default: 500, max: 500) |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing recent transactions

**Raises:**

- `FiveTwentyError` - API errors