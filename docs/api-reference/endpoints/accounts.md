# Accounts Endpoint

**OANDA Reference**: [Account Endpoints](https://developer.oanda.com/rest-live-v20/account-ep/)

Account management and information retrieval.

---

## get_accounts
<!-- code-block: get_accounts_basic -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.get_accounts() -> list[AccountProperties]

        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")


asyncio.run(main())
```
**OANDA Endpoint**: `GET /v3/accounts`

🔗 **OANDA Documentation**: [Get Accounts](https://developer.oanda.com/rest-live-v20/account-ep/#get-accounts)

🔗 **FiveTwenty SDK**: [accounts.get_accounts](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Get list of all accounts for the authenticated user.

**Parameters:**

*No parameters required*

**Returns:** List of account properties (basic info)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_account
<!-- code-block: get_account_details -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.get_account(account_id: AccountID) -> AccountResponse
        # Returns: {"account": Account, "lastTransactionID": str}

        result = await client.accounts.get_account(account_id=client.account_id)
        account = result["account"]
        print(f"Account balance: {account.balance}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
**OANDA Endpoint**: `GET /v3/accounts/{accountID}`

🔗 **OANDA Documentation**: [Get Account Details](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-details)

🔗 **FiveTwenty SDK**: [accounts.get_account](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Get detailed information for specific account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing complete account details (`Account`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## get_account_summary
<!-- code-block: get_account_summary_basic -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.get_account_summary(account_id: AccountID) -> AccountSummaryResponse
        # Returns: {"account": AccountSummary, "lastTransactionID": str}

        result = await client.accounts.get_account_summary(account_id=client.account_id)
        summary = result["account"]
        print(f"Account NAV: {summary.nav}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")

asyncio.run(main())
```
**OANDA Endpoint**: `GET /v3/accounts/{accountID}/summary`

🔗 **OANDA Documentation**: [Get Account Summary](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-summary)

🔗 **FiveTwenty SDK**: [accounts.get_account_summary](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Get condensed account information.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |

**Returns:** Dictionary containing account summary (`AccountSummary`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## get_account_instruments
<!-- code-block: get_account_instruments_filtered -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.get_account_instruments(account_id: AccountID, *, instruments: list[str] | None = None) -> AccountInstrumentsResponse
        # Returns: {"instruments": list[Instrument], "lastTransactionID": str}

        result = await client.accounts.get_account_instruments(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"]
        )
        instruments = result["instruments"]
        print(f"Found {len(instruments)} instruments")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
**OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments`

🔗 **OANDA Documentation**: [Get Account Instruments](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-instruments)

🔗 **FiveTwenty SDK**: [accounts.get_account_instruments](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Get all tradeable instruments for account.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `instruments` | list[str] | ➖ | Filter to specific instruments (optional) |

**Returns:** Dictionary containing list of instrument specifications (`list[Instrument]`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---

## patch_account_configuration
<!-- code-block: update_account_alias -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.patch_account_configuration(account_id: AccountID, *, alias: str | None = None,
        #                   margin_rate: str | None = None) -> AccountConfigurationResponse

        result = await client.accounts.patch_account_configuration(
            account_id=client.account_id,
            alias="My Trading Account"
        )
        print("Configuration updated")
        print(f"Transaction ID: {result['clientConfigureTransaction'].id}")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
**OANDA Endpoint**: `PATCH /v3/accounts/{accountID}/configuration`

🔗 **OANDA Documentation**: [Configure Account](https://developer.oanda.com/rest-live-v20/account-ep/#configure-account)

🔗 **FiveTwenty SDK**: [accounts.patch_account_configuration](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Update account configuration settings.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `alias` | str | ➖ | Client-assigned account alias (display name) |
| `margin_rate` | str | ➖ | Account margin rate as decimal string (e.g., "0.05" for 5%) |

**Returns:** Dictionary containing configuration transaction (`ClientConfigureTransaction`) and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, invalid parameters, or insufficient permissions

---

## get_account_changes
<!-- code-block: get_account_changes_since -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # accounts.get_account_changes(account_id: AccountID, *, since_transaction_id: str) -> AccountChangesResponse

        result = await client.accounts.get_account_changes(
            account_id=client.account_id,
            since_transaction_id="100"
        )
        print(f"Changes: {len(result['changes'].orders_created)} orders created")
        print(f"Last Transaction ID: {result['lastTransactionID']}")


asyncio.run(main())
```
**OANDA Endpoint**: `GET /v3/accounts/{accountID}/changes`

🔗 **OANDA Documentation**: [Get Account Changes](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-changes)

🔗 **FiveTwenty SDK**: [accounts.get_account_changes](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/accounts.py)

Get account state changes since specified transaction ID.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Target account identifier |
| `since_transaction_id` | str | ✅ | Transaction ID to get changes since |

**Returns:** Dictionary containing changes (`AccountChanges`), state (`AccountChangesState`), and last transaction ID (`str`)

**Raises:**

- `FiveTwentyError` - API errors, invalid transaction ID, or account not found