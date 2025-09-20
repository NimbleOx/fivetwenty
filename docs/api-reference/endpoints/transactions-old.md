# Transactions Endpoint

📖 **OANDA Reference**: [Transactions API Documentation](https://developer.oanda.com/rest-live-v20/transaction-ep/)

Transaction history and streaming for account activity tracking.

---

## list
```python
transactions.list(account_id: AccountID, **kwargs) -> list[Transaction]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

📖 **OANDA Documentation**: [Get Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get transaction history.

**Parameters:**

- `account_id` (AccountID) - Target account

**Optional Parameters:**

- `from_time` (DateTime) - Start time
- `to_time` (DateTime) - End time
- `page_size` (int) - Results per page
- `type` (list[TransactionType]) - Transaction types to include

**Returns:** List of transactions

**Raises:**

- `FiveTwentyError` - API errors

---

## get
```python
transactions.get(account_id: AccountID, transaction_id: TransactionID) -> Transaction
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/{transactionID}`

📖 **OANDA Documentation**: [Get Transaction Details](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction-details)

Get specific transaction.

**Parameters:**

- `account_id` (AccountID) - Target account
- `transaction_id` (TransactionID) - Transaction identifier

**Returns:** Transaction details

**Raises:**

- `FiveTwentyError` - API errors or invalid transaction ID

---

## get_range
```python
transactions.get_range(account_id: AccountID, from_id: TransactionID, to_id: TransactionID) -> list[Transaction]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/idrange`

📖 **OANDA Documentation**: [Get Transaction Range](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction-range)

Get transaction range.

**Parameters:**

- `account_id` (AccountID) - Target account
- `from_id` (TransactionID) - Start transaction ID
- `to_id` (TransactionID) - End transaction ID

**Returns:** Transactions in ID range

**Raises:**

- `FiveTwentyError` - API errors or invalid range

---

## stream
```python
transactions.stream(account_id: AccountID) -> AsyncIterator[Transaction | TransactionHeartbeat]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/stream`

📖 **OANDA Documentation**: [Stream Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#stream-transactions)

Stream real-time transactions (async only).

**Parameters:**

- `account_id` (AccountID) - Target account

**Yields:** Transaction updates and heartbeats

**Raises:**

- `FiveTwentyError` - API errors

---

## list_since
```python
transactions.list_since(account_id: AccountID, since_id: TransactionID, **kwargs) -> list[Transaction]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/sinceid`

📖 **OANDA Documentation**: [Get Transactions Since ID](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions-since-id)

Get transactions since specified transaction ID.

**Parameters:**

- `account_id` (AccountID) - Target account
- `since_id` (TransactionID) - Get transactions newer than this ID

**Optional Parameters:**

- `type` (list[TransactionFilter]) - Filter by transaction types

**Returns:** Transactions since specified ID

**Raises:**

- `FiveTwentyError` - API errors or invalid transaction ID

---