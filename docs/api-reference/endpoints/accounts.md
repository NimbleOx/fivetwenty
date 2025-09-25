# Accounts Endpoint

📖 **OANDA Reference**: [Account Endpoints](https://developer.oanda.com/rest-live-v20/account-ep/)

Account management and information retrieval.

---

## get_accounts
```python
import asyncio

async def main():
    # accounts.get_accounts() -> list[AccountProperties]

    # Example usage:
    accounts = await client.accounts.get_accounts()

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
# accounts.get_account(account_id: AccountID) -> Account

# Example usage:
account = await client.accounts.get_account(account_id="123-456-789")
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
# accounts.get_account_summary(account_id: AccountID) -> AccountSummary

# Example usage:
summary = await client.accounts.get_account_summary(account_id="123-456-789")
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
# accounts.get_account_instruments(account_id: AccountID, instruments: list[str] | None = None) -> list[Instrument]

# Example usage:
instruments = await client.accounts.get_account_instruments(
    account_id="123-456-789",
    instruments=["EUR_USD", "GBP_USD"]
)
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
# accounts.patch_account_configuration(account_id: AccountID, alias: str | None = None,
#                   margin_rate: str | None = None) -> dict[str, Any]

# Example usage:
result = await client.accounts.patch_account_configuration(
    account_id="123-456-789",
    alias="My Trading Account"
)
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
# accounts.get_account_changes(account_id: AccountID, since_transaction_id: str) -> dict[str, Any]

# Example usage:
changes = await client.accounts.get_account_changes(
    account_id="123-456-789",
    since_transaction_id="100"
)
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