# Accounts Endpoint

📖 **OANDA Reference**: [Account Endpoints](https://developer.oanda.com/rest-live-v20/account-ep/)

Account management and information retrieval.

---

## get_accounts
```python
import asyncio
from fivetwenty import AsyncClient, Configuration


async def main() -> None:
    config = Configuration(token="demo-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # accounts.get_accounts() -> list[AccountProperties]

        # Example usage:
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts`

📖 **OANDA Documentation**: [Get Accounts](https://developer.oanda.com/rest-live-v20/account-ep/#get-accounts)

Get list of all accounts for the authenticated user.

**Parameters:**

*No parameters required*

**Returns:** List of account properties (basic info)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_account
```python
import asyncio
from fivetwenty import AsyncClient, Configuration


async def get_account_example() -> None:
    config = Configuration(token="demo-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # accounts.get_account(account_id: AccountID) -> Account

        # Example usage:
        account = await client.accounts.get_account(account_id="123-456-789")
        print(f"Account balance: {account.balance}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}`

📖 **OANDA Documentation**: [Get Account Details](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-details)

Get detailed information for specific account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Complete account details with balances, margin, and statistics

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## get_account_summary
```python
async def get_account_summary_example() -> None:
    async with AsyncClient(token="demo-token") as client:
        # accounts.get_account_summary(account_id: AccountID) -> AccountSummary

        # Example usage:
        summary = await client.accounts.get_account_summary(account_id="123-456-789")
        print(f"Account NAV: {summary.nav}")
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/summary`

📖 **OANDA Documentation**: [Get Account Summary](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-summary)

Get condensed account information.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Account summary with key metrics

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## get_account_instruments
```python
import asyncio
from fivetwenty import AsyncClient, Configuration


async def main() -> None:
    # accounts.get_account_instruments(account_id: AccountID, instruments: list[str] | None = None) -> list[Instrument]

    config = Configuration(token="demo-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        instruments = await client.accounts.get_account_instruments(
            account_id="123-456-789",
            instruments=["EUR_USD", "GBP_USD"]
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments`

📖 **OANDA Documentation**: [Get Account Instruments](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-instruments)

Get all tradeable instruments for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `instruments` | list[str] | ➖ | Filter to specific instruments (optional) |

**Returns:** List of instrument specifications

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## patch_account_configuration
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Configuration


async def main() -> None:
    # accounts.patch_account_configuration(account_id: AccountID, alias: str | None = None,
    #                   margin_rate: str | None = None) -> dict[str, Any]

    config = Configuration(token="demo-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        result = await client.accounts.patch_account_configuration(
            account_id="123-456-789",
            alias="My Trading Account"
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `PATCH /v3/accounts/{accountID}/configuration`

📖 **OANDA Documentation**: [Configure Account](https://developer.oanda.com/rest-live-v20/account-ep/#configure-account)

Update account configuration settings.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `alias` | str | ➖ | Client-assigned account alias (display name) |
| `margin_rate` | str | ➖ | Account margin rate as decimal string (e.g., "0.05" for 5%) |

**Returns:** Updated account configuration

**Raises:**

- `FiveTwentyError` - API errors, invalid parameters, or insufficient permissions

---

## get_account_changes
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Configuration


async def main() -> None:
    # accounts.get_account_changes(account_id: AccountID, since_transaction_id: str) -> dict[str, Any]

    config = Configuration(token="demo-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        changes = await client.accounts.get_account_changes(
            account_id="123-456-789",
            since_transaction_id="100"
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/changes`

📖 **OANDA Documentation**: [Get Account Changes](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-changes)

Get account state changes since specified transaction ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `since_transaction_id` | str | ✅ | Transaction ID to get changes since |

**Returns:** Account changes and current state

**Raises:**

- `FiveTwentyError` - API errors, invalid transaction ID, or account not found