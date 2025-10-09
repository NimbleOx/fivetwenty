# Accounts Endpoint

**OANDA Reference**: [Account Endpoints](https://developer.oanda.com/rest-live-v20/account-ep/)

Account management and information retrieval.

---

## get_accounts

Get list of all accounts for the authenticated user.

**OANDA Endpoint**: `GET /v3/accounts`

<!-- code-block: get_accounts_basic -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Retrieve all accounts associated with the API token
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Accounts](https://developer.oanda.com/rest-live-v20/account-ep/#get-accounts)

🔗 **Source**: [accounts.get_accounts](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

*No parameters required*

**Returns:** List of account properties (basic info)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_account

Get detailed information for specific account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}`

<!-- code-block: get_account_details -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get full account details including all open trades and positions
        result = await client.accounts.get_account(account_id=client.account_id)
        account = result["account"]
        print(f"Account balance: {account.balance}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Account Details](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-details)

🔗 **Source**: [accounts.get_account](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing complete account details (`Account`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_account_summary

Get condensed account information.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/summary`

<!-- code-block: get_account_summary_basic -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get condensed account summary (NAV, balance, P/L, margin) without trade details
        result = await client.accounts.get_account_summary(account_id=client.account_id)
        summary = result["account"]
        print(f"Account NAV: {summary.nav}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Account Summary](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-summary)

🔗 **Source**: [accounts.get_account_summary](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing account summary (`AccountSummary`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_account_instruments

Get all tradeable instruments for account.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments`

<!-- code-block: get_account_instruments_filtered -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get instrument specifications (pip value, margin rate, etc.) filtered to specific pairs
        result = await client.accounts.get_account_instruments(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"]
        )
        instruments = result["instruments"]
        print(f"Found {len(instruments)} instruments")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Account Instruments](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-instruments)

🔗 **Source**: [accounts.get_account_instruments](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `instruments` | list[str] | ➖ | Filter to specific instruments (optional) |

**Returns:** Dictionary containing list of instrument specifications (`list[Instrument]`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## patch_account_configuration

Update account configuration settings.

**OANDA Endpoint**: `PATCH /v3/accounts/{accountID}/configuration`

<!-- code-block: update_account_alias -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Update the account display name (alias)
        result = await client.accounts.patch_account_configuration(
            account_id=client.account_id,
            alias="My Trading Account"
        )
        print("Configuration updated")
        print(f"Transaction ID: {result['clientConfigureTransaction'].id}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Configure Account](https://developer.oanda.com/rest-live-v20/account-ep/#configure-account)

🔗 **Source**: [accounts.patch_account_configuration](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `alias` | str | ➖ | Client-assigned account alias (display name) |
| `margin_rate` | str | ➖ | Account margin rate as decimal string (e.g., "0.05" for 5%) |

**Returns:** Dictionary containing configuration transaction (`ClientConfigureTransaction`) and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 400: Invalid parameters (check `e.is_validation_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_account_changes

Get account state changes since specified transaction ID.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/changes`

<!-- code-block: get_account_changes_since -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get all account state changes (orders, trades, positions) since transaction ID 100
        result = await client.accounts.get_account_changes(
            account_id=client.account_id,
            since_transaction_id="100"
        )
        print(f"Changes: {len(result['changes'].orders_created)} orders created")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Account Changes](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-changes)

🔗 **Source**: [accounts.get_account_changes](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `since_transaction_id` | str | ✅ | Transaction ID to get changes since |

**Returns:** Dictionary containing changes (`AccountChanges`), state (`AccountChangesState`), and last transaction ID (`str`)

**Raises:**

`FiveTwentyError` - API errors:

- 401/403: Authentication failed (check `e.is_authentication_error`)
- 400: Invalid transaction ID (check `e.is_validation_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)