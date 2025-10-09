# Transactions Endpoint

**OANDA Reference**: [Transaction Endpoints](https://developer.oanda.com/rest-live-v20/transaction-ep/)

Transaction history and monitoring.

---

## get_transactions

Get transaction history for account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

<!-- code-block: transactions__get_transactions -->
```python
import asyncio
from datetime import datetime, timezone

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get transaction history with time range and filters
        result: TransactionsResponse = await client.transactions.get_transactions(
            client.account_id,
            from_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
            to_time=datetime(2024, 12, 31, tzinfo=timezone.utc),
            page_size=50,
            transaction_type=["ORDER_FILL", "MARKET_ORDER"],
        )
        print(f"Last Transaction ID: {result['lastTransactionID']}")
        print(f"Page count: {len(result.get('pages', []))}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

🔗 **Source**: [transactions.get_transactions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `*` | | | **Keyword-only parameters below** |
| `from_time` | datetime \| None | ➖ | Start time for transaction range |
| `to_time` | datetime \| None | ➖ | End time for transaction range |
| `page_size` | int | ➖ | Number of transactions per page (default: 100, max: 1000) |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types |

**Returns:** `TransactionsResponse` - TypedDict containing transaction history with pagination info (from_, to, pageSize, type, count, pages, lastTransactionID)

**Raises:**

`FiveTwentyError` - API errors:

  - 400: Invalid request parameters (check `e.is_bad_request`)
  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - If page_size exceeds 1000

---

## get_transaction

Get specific transaction details.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/{transactionID}`

<!-- code-block: transactions__get_transaction -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get details for a specific transaction
        result: TransactionResponse = await client.transactions.get_transaction(
            client.account_id,
            transaction_id="12345",  # Change to your transaction ID
        )
        transaction = result["transaction"]
        print(f"Transaction type: {transaction.type}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Transaction](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction)

🔗 **Source**: [transactions.get_transaction](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Transaction identifier |

**Returns:** `TransactionResponse` - TypedDict containing transaction details (transaction: TransactionUnion, lastTransactionID: str)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Transaction not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_transactions_since_id

Get transactions since specific transaction ID.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/sinceid`

<!-- code-block: transactions__get_transactions_since_id -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsSinceIdResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get all transactions since a specific ID
        result: TransactionsSinceIdResponse = (
            await client.transactions.get_transactions_since_id(
                client.account_id,
                transaction_id="100",  # Change to your starting transaction ID
                transaction_type=["ORDER_FILL"],
            )
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Transactions Since ID](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions-since-id)

🔗 **Source**: [transactions.get_transactions_since_id](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `transaction_id` | str | ✅ | Starting transaction ID |
| `*` | | | **Keyword-only parameters below** |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types |

**Returns:** `TransactionsSinceIdResponse` - TypedDict containing transactions since ID (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account or transaction not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_transactions_stream

Stream real-time transactions.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/stream`

<!-- code-block: transactions__get_transactions_stream -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import TransactionHeartbeat

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Stream real-time transaction updates
        count = 0
        async for item in client.transactions.get_transactions_stream(
            client.account_id, stall_timeout=60.0
        ):
            if isinstance(item, TransactionHeartbeat):
                print(f"Heartbeat at {item.time}")
            else:
                print(f"Transaction: {item.type} - {item.id}")
                count += 1
                if count >= 5:  # Stop after 5 transactions for testing
                    break


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Stream Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#stream-transactions)

🔗 **Source**: [transactions.get_transactions_stream](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `*` | | | **Keyword-only parameters below** |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls in seconds (default: 30.0) |

**Returns:** `AsyncIterator[TransactionUnion | TransactionHeartbeat]` - Yields transaction objects or heartbeat messages

**Raises:**

`FiveTwentyError` - API errors:

  - 400: Invalid request parameters (check `e.is_bad_request`)
  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`)

`StreamStall` - On stream timeout or connection issues

---

## get_transactions_range

Get transactions in ID range.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions/idrange`

<!-- code-block: transactions__get_transactions_range -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsRangeResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get transactions within a specific ID range
        result: TransactionsRangeResponse = (
            await client.transactions.get_transactions_range(
                client.account_id,
                from_transaction_id="100",  # Change to your range
                to_transaction_id="200",
            )
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Transaction Range](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transaction-range)

🔗 **Source**: [transactions.get_transactions_range](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `from_transaction_id` | str | ✅ | Starting transaction ID (inclusive) |
| `to_transaction_id` | str | ✅ | Ending transaction ID (inclusive) |
| `*` | | | **Keyword-only parameters below** |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types |

**Returns:** `TransactionsRangeResponse` - TypedDict containing transactions in range (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

`FiveTwentyError` - API errors:

  - 400: Invalid request parameters (check `e.is_bad_request`)
  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - If from_transaction_id > to_transaction_id or if transaction IDs are not numeric

---

## get_recent_transactions

Get recent transactions for account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/transactions`

<!-- code-block: transactions__get_recent_transactions -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionsRangeResponse

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get the most recent transactions
        result: TransactionsRangeResponse = (
            await client.transactions.get_recent_transactions(
                client.account_id,
                count=100,
                transaction_type=["ORDER_FILL", "MARKET_ORDER"],
            )
        )
        transactions = result["transactions"]
        print(f"Found {len(transactions)} recent transactions")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Recent Transactions](https://developer.oanda.com/rest-live-v20/transaction-ep/#get-transactions)

🔗 **Source**: [transactions.get_recent_transactions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/transactions.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account identifier |
| `*` | | | **Keyword-only parameters below** |
| `count` | int | ➖ | Number of recent transactions (default: 50, max: 500) |
| `transaction_type` | list[str] \| None | ➖ | Filter by transaction types |

**Returns:** `TransactionsRangeResponse` - TypedDict containing recent transactions (transactions: list[TransactionUnion], lastTransactionID: str)

**Raises:**

`FiveTwentyError` - API errors:

  - 400: Invalid request parameters (check `e.is_bad_request`)
  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Account not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - If count exceeds 500
