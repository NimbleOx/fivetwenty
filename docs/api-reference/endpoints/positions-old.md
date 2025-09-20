# Positions Endpoint

📖 **OANDA Reference**: [Positions API Documentation](https://developer.oanda.com/rest-live-v20/position-ep/)

Position tracking and management for your trading account.

---

## list_open
```python
positions.list_open(account_id: AccountID) -> list[Position]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/openPositions`

📖 **OANDA Documentation**: [Get Open Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-open-positions)

Get all open positions for account.

**Parameters:**

- `account_id` (AccountID) - Target account

**Returns:** List of open positions

**Raises:**

- `FiveTwentyError` - API errors

---

## get
```python
positions.get(account_id: AccountID, instrument: InstrumentName) -> Position
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions/{instrument}`

📖 **OANDA Documentation**: [Get Position](https://developer.oanda.com/rest-live-v20/position-ep/#get-position)

Get position for specific instrument.

**Parameters:**

- `account_id` (AccountID) - Target account
- `instrument` (InstrumentName) - Target instrument

**Returns:** Position details (may have zero units)

**Raises:**

- `FiveTwentyError` - API errors

---

## close
```python
positions.close(account_id: AccountID, instrument: InstrumentName, **kwargs) -> OrderResponse
```
🔗 **OANDA Endpoint**: `PUT /v3/accounts/{accountID}/positions/{instrument}/close`

📖 **OANDA Documentation**: [Close Position](https://developer.oanda.com/rest-live-v20/position-ep/#close-position)

Close position for instrument.

**Parameters:**

- `account_id` (AccountID) - Target account
- `instrument` (InstrumentName) - Instrument to close

**Optional Parameters:**

- `long_units` (str) - Long units to close ("ALL" or specific amount)
- `short_units` (str) - Short units to close ("ALL" or specific amount)

**Returns:** Close response with fill details

**Raises:**

- `FiveTwentyError` - API errors or no position found

---

## list
```python
positions.list(account_id: AccountID) -> list[Position]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/positions`

📖 **OANDA Documentation**: [Get All Positions](https://developer.oanda.com/rest-live-v20/position-ep/#get-all-positions)

Get all positions for account (including zero-unit positions).

**Parameters:**

- `account_id` (AccountID) - Target account

**Returns:** List of all positions for every instrument that has had a position during account lifetime

**Raises:**

- `FiveTwentyError` - API errors or invalid account ID

---