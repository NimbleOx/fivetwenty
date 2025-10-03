# Transactions Endpoint

**OANDA Reference**: [Transaction Endpoints](https://developer.oanda.com/rest-live-v20/transaction-ep/)

Transaction history and monitoring.

---

## get_transactions
<!-- fragment: Demo get_transactions with unused imports and assignment before return patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsResponse


async def main() -> None:
    async with AsyncClient() as client:
        # transactions.get_transactions(account_id: AccountID, from_time: datetime | None = None,
        #                   to_time: datetime | None = None, page_size: int = 100,
        #                   transaction_type: list[str] | None = None) -> TransactionsResponse
        # Returns: {"from": str, "to": str, "pageSize": int, "type": str, "count": int,
        #           "pages": list[str], "lastTransactionID": str} (some fields may be optional)

        # Example usage:
        result: TransactionsResponse = await client.transactions.get_transactions(
            account_id="123-456-789",
            page_size=50,
            transaction_type=["ORDER_FILL", "MARKET_ORDER"],
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

**OANDA Documentation**: [Get Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

Get transaction history for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_time` | str | ➖ | Start time for transaction range |
| `to_time` | str | ➖ | End time for transaction range |
| `page_size` | int | ➖ | Number of transactions per page (default: 100) |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transaction history and pagination info

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transaction
<!-- fragment: Demo get_transaction with missing return type annotation and call argument issues -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionResponse


async def get_transaction_example() -> None:
    async with AsyncClient() as client:
        # transactions.get_transaction(account_id: AccountID, transaction_id: str) -> TransactionResponse
        # Returns: {"transaction": Any, "lastTransactionID": str}

        # Example usage:
        result: TransactionResponse = await client.transactions.get_transaction(
            account_id="123-456-789",
            transaction_id="12345"
        )
        transaction = result["transaction"]
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(get_transaction_example())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/{transactionID}`

**OANDA Documentation**: [Get Transaction](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction)

Get specific transaction details.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Transaction identifier |

**Returns:** Dictionary containing transaction details and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transactions_since_id
<!-- fragment: Demo get_transactions_since_id with missing return type annotation and call argument patterns -->
```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsSinceIdResponse


async def get_transactions_since_id_example() -> None:
    async with AsyncClient() as client:
        # transactions.get_transactions_since_id(account_id: AccountID, transaction_id: str,
        #                        transaction_type: list[str] | None = None) -> TransactionsSinceIdResponse
        # Returns: {"transactions": list[Any], "lastTransactionID": str}

        # Example usage:
        result: TransactionsSinceIdResponse = await client.transactions.get_transactions_since_id(
            account_id="123-456-789",
            transaction_id="100",
            transaction_type=["ORDER_FILL"]
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(get_transactions_since_id_example())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/sinceid`

**OANDA Documentation**: [Get Transactions Since ID](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions-since-id)

Get transactions since specific transaction ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Starting transaction ID |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transactions (`list[Any]`) since ID and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_transactions_stream
<!-- fragment: Demo get_transactions_stream with missing return type annotation patterns -->
```python
# transactions.get_transactions_stream(account_id: AccountID, stall_timeout: float = 30.0) -> AsyncIterator[dict[str, Any]]

# Example usage:
async def stream_transactions_example(client):
    async for transaction in client.transactions.get_transactions_stream(
        account_id="123-456-789",
        stall_timeout=60.0
    ):
        print(f"Transaction: {transaction}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/stream`

**OANDA Documentation**: [Stream Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#stream-transactions)

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

## get_transactions_range
<!-- fragment: Demo get_transactions_range with unused imports and assignment before return issues -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration
from fivetwenty.endpoints.transactions import TransactionsRangeResponse


async def main() -> None:
    # transactions.get_transactions_range(account_id: AccountID, from_transaction_id: str,
    #                       to_transaction_id: str, transaction_type: list[str] | None = None) -> TransactionsRangeResponse
    # Returns: {"transactions": list[Any], "lastTransactionID": str}

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        result: TransactionsRangeResponse = await client.transactions.get_transactions_range(
            account_id="123-456-789",
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
| `from_transaction_id` | str | ✅ | Starting transaction ID |
| `to_transaction_id` | str | ✅ | Ending transaction ID |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing transactions (`list[Any]`) in range and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_recent_transactions
<!-- fragment: Demo get_recent_transactions with unused imports and assignment patterns -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration
from fivetwenty.endpoints.transactions import TransactionsRangeResponse


async def main() -> None:
    # transactions.get_recent_transactions(account_id: AccountID, count: int = 50,
    #                     transaction_type: list[str] | None = None) -> TransactionsRangeResponse
    # Returns: {"transactions": list[Any], "lastTransactionID": str}

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        result: TransactionsRangeResponse = await client.transactions.get_recent_transactions(
            account_id="123-456-789",
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
| `count` | int | ➖ | Number of recent transactions (default: 500, max: 500) |
| `transaction_type` | list[str] | ➖ | Filter by transaction types |

**Returns:** Dictionary containing recent transactions (`list[Any]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors