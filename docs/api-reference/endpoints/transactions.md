# Transactions Endpoint

**OANDA Reference**: [Transaction Endpoints](https://developer.oanda.com/rest-live-v20/transaction-ep/)

Transaction history and monitoring.

---

## get_transactions

```python
import asyncio
from datetime import datetime
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        # get_transactions(account_id: AccountID, *, from_time: datetime | None = None,
        #                  to_time: datetime | None = None, page_size: int = 100,
        #                  transaction_type: list[str] | None = None) -> TransactionsResponse
        # Returns: TransactionsResponse (TypedDict with from_, to, pageSize, type, count, pages, lastTransactionID)

        result: TransactionsResponse = await client.transactions.get_transactions(
            client.account_id,
            from_time=datetime(2024, 1, 1),
            to_time=datetime(2024, 12, 31),
            page_size=50,
            transaction_type=["ORDER_FILL", "MARKET_ORDER"],
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")
        print(f"Page count: {len(result.get('pages', []))}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

**OANDA Documentation**: [Get Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get transaction history for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_time` | datetime \| None | ➖ | Start time for transaction range (keyword-only) |
| `to_time` | datetime \| None | ➖ | End time for transaction range (keyword-only) |
| `page_size` | int | ➖ | Number of transactions per page (default: 100, max: 1000, keyword-only) |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types (keyword-only) |

**Returns:** `TransactionsResponse` - TypedDict containing transaction history with pagination info (from_, to, pageSize, type, count, pages, lastTransactionID)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transaction

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionResponse


async def main() -> None:
    async with AsyncClient() as client:
        # get_transaction(account_id: AccountID, transaction_id: str) -> TransactionResponse
        # Returns: TransactionResponse (TypedDict with transaction: TransactionUnion, lastTransactionID: str)

        result: TransactionResponse = await client.transactions.get_transaction(
            client.account_id,
            transaction_id="12345"
        )
        transaction = result["transaction"]
        print(f"Transaction type: {transaction.type}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/{transactionID}`

**OANDA Documentation**: [Get Transaction](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction)

Get specific transaction details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Transaction identifier |

**Returns:** `TransactionResponse` - TypedDict containing transaction details (transaction: TransactionUnion, lastTransactionID: str)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transactions_since_id

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsSinceIdResponse


async def main() -> None:
    async with AsyncClient() as client:
        # get_transactions_since_id(account_id: AccountID, transaction_id: str, *,
        #                           transaction_type: list[str] | None = None) -> TransactionsSinceIdResponse
        # Returns: TransactionsSinceIdResponse (TypedDict with transactions: list[TransactionUnion], lastTransactionID: str)

        result: TransactionsSinceIdResponse = await client.transactions.get_transactions_since_id(
            client.account_id,
            transaction_id="100",
            transaction_type=["ORDER_FILL"]
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/sinceid`

**OANDA Documentation**: [Get Transactions Since ID](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions-since-id)

Get transactions since specific transaction ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Starting transaction ID |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types (keyword-only) |

**Returns:** `TransactionsSinceIdResponse` - TypedDict containing transactions since ID (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transactions_stream

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    async with AsyncClient() as client:
        # get_transactions_stream(account_id: AccountID, *, stall_timeout: float = 30.0)
        #                         -> AsyncIterator[TransactionUnion | TransactionHeartbeat]
        # Yields: Transaction objects or TransactionHeartbeat messages

        async for item in client.transactions.get_transactions_stream(
            client.account_id,
            stall_timeout=60.0
        ):
            if hasattr(item, 'type') and item.type == "HEARTBEAT":
                print(f"Heartbeat at {item.time}")
            else:
                print(f"Transaction: {item.type} - {item.id}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/stream`

**OANDA Documentation**: [Stream Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#stream-transactions)

Stream real-time transactions.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls (default: 30.0, keyword-only) |

**Returns:** `AsyncIterator[TransactionUnion | TransactionHeartbeat]` - Yields transaction objects or heartbeat messages

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - On stream timeout or connection issues

---

## get_transactions_range

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsRangeResponse


async def main() -> None:
    async with AsyncClient() as client:
        # get_transactions_range(account_id: AccountID, from_transaction_id: str,
        #                        to_transaction_id: str, *, transaction_type: list[str] | None = None)
        #                        -> TransactionsRangeResponse
        # Returns: TransactionsRangeResponse (TypedDict with transactions: list[TransactionUnion], lastTransactionID: str)

        result: TransactionsRangeResponse = await client.transactions.get_transactions_range(
            client.account_id,
            from_transaction_id="100",
            to_transaction_id="200"
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/idrange`

**OANDA Documentation**: [Get Transaction Range](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction-range)

Get transactions in ID range.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_transaction_id` | str | ✅ | Starting transaction ID (inclusive) |
| `to_transaction_id` | str | ✅ | Ending transaction ID (inclusive) |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types (keyword-only) |

**Returns:** `TransactionsRangeResponse` - TypedDict containing transactions in range (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_recent_transactions

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsRangeResponse


async def main() -> None:
    async with AsyncClient() as client:
        # get_recent_transactions(account_id: AccountID, *, count: int = 50,
        #                         transaction_type: list[str] | None = None) -> TransactionsRangeResponse
        # Returns: TransactionsRangeResponse (TypedDict with transactions: list[TransactionUnion], lastTransactionID: str)

        result: TransactionsRangeResponse = await client.transactions.get_recent_transactions(
            client.account_id,
            count=100,
            transaction_type=["ORDER_FILL", "MARKET_ORDER"]
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} recent transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

**OANDA Documentation**: [Get Recent Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get recent transactions for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `count` | int | ➖ | Number of recent transactions (default: 50, max: 500, keyword-only) |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types (keyword-only) |

**Returns:** `TransactionsRangeResponse` - TypedDict containing recent transactions (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

- `FiveTwentyError` - API errors