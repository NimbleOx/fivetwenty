# API Reference Documentation Validation Plan

## Objective
Validate every single line of the `docs/api-reference/` documentation against the SDK implementation to ensure 100% accuracy, completeness, and correctness.

---

## Validation Methodology

### Phase 1: Source Code Mapping (Foundation)

Create a comprehensive mapping between documentation files and SDK source files:

```
docs/api-reference/client.md              → fivetwenty/client.py
docs/api-reference/configuration.md       → fivetwenty/configuration.py
docs/api-reference/exceptions.md          → fivetwenty/exceptions.py
docs/api-reference/error-handling.md      → fivetwenty/exceptions.py + error handling patterns
docs/api-reference/endpoints/accounts.md  → fivetwenty/endpoints/accounts.py
docs/api-reference/endpoints/orders.md    → fivetwenty/endpoints/orders.py
docs/api-reference/endpoints/trades.md    → fivetwenty/endpoints/trades.py
docs/api-reference/endpoints/positions.md → fivetwenty/endpoints/positions.py
docs/api-reference/endpoints/pricing.md   → fivetwenty/endpoints/pricing.py
docs/api-reference/endpoints/instruments.md → fivetwenty/endpoints/instruments.py
docs/api-reference/endpoints/transactions.md → fivetwenty/endpoints/transactions.py
docs/api-reference/models/account-models.md → fivetwenty/models/accounts.py
docs/api-reference/models/order-models.md → fivetwenty/models/orders.py
docs/api-reference/models/trading-models.md → fivetwenty/models/trades.py, positions.py
docs/api-reference/models/transaction-models.md → fivetwenty/models/transactions.py
docs/api-reference/models/market-data-models.md → fivetwenty/models/pricing.py
docs/api-reference/models/enum-models.md  → fivetwenty/models/enums.py
docs/api-reference/models/system-models.md → fivetwenty/models/base.py, enums.py (type aliases)
```

**Validation Checks:**
- [ ] Every SDK file has corresponding documentation
- [ ] Every documented feature exists in SDK
- [ ] No orphaned documentation (docs for removed features)

---

### Phase 2: Client & Configuration Validation

#### 2.1 Client Constructor Validation (`client.md`)

**For AsyncClient and Client classes:**

1. **Constructor Signature Validation**
   - [ ] All parameters documented
   - [ ] Parameter types match SDK type hints exactly
   - [ ] Default values match SDK defaults
   - [ ] Parameter descriptions are accurate
   - [ ] Required vs optional parameters correctly indicated

2. **Initialization Pattern Validation**
   - [ ] Direct parameters pattern documented and correct
   - [ ] Configuration object pattern documented and correct
   - [ ] Environment variable pattern documented and correct
   - [ ] Error conditions documented (ValueError when no config)

3. **Method Validation**
   ```python
   # For each client method, verify:
   - Method exists in SDK
   - Signature matches (parameters, types, defaults)
   - Return type is correct
   - Docstring description matches docs
   - Error cases documented
   ```

4. **Endpoint Property Validation**
   - [ ] `client.accounts` exists and returns `AccountEndpoints`
   - [ ] `client.orders` exists and returns `OrderEndpoints`
   - [ ] `client.trades` exists and returns `TradeEndpoints`
   - [ ] `client.positions` exists and returns `PositionEndpoints`
   - [ ] `client.pricing` exists and returns `PricingEndpoints`
   - [ ] `client.instruments` exists and returns `InstrumentEndpoints`
   - [ ] `client.transactions` exists and returns `TransactionEndpoints`

5. **Property Validation**
   - [ ] `client.account_id` property documented and exists
   - [ ] `client.config` property documented and exists
   - [ ] `client.timeout` property documented and exists
   - [ ] All properties have correct types

#### 2.2 Configuration Validation (`configuration.md`)

1. **AccountConfig Model Validation**
   - [ ] All fields documented with correct types
   - [ ] Field requirements (required/optional) match Pydantic model
   - [ ] Default values match model defaults
   - [ ] Field descriptions accurate
   - [ ] Validation rules documented

2. **AccountConfigLoader Validation**
   - [ ] All methods documented
   - [ ] Method signatures correct
   - [ ] Environment variable names correct
   - [ ] Load order documented correctly

3. **ConfigValidator Validation**
   - [ ] All validation methods documented
   - [ ] Validation rules match implementation
   - [ ] Error messages documented

---

### Phase 3: Endpoint Validation (7 Endpoint Files)

**For each endpoint file, perform these validation checks:**

#### 3.1 Method Signature Validation
For every documented method:

```python
# Validation checklist per method:
1. Method name matches SDK exactly
2. All parameters documented
3. Parameter types match SDK type hints
4. Required vs optional parameters correct
5. Default values match SDK
6. Keyword-only parameters marked with *
7. Return type matches SDK
8. Return value structure documented correctly
```

#### 3.2 Method Documentation Validation
```python
# For each method:
1. OANDA endpoint URL is correct (GET/POST/PUT/PATCH/DELETE /v3/accounts/...)
2. OANDA documentation link works and points to correct page
3. Method description accurately describes what it does
4. All parameters have descriptions
5. Return value structure documented with all fields
6. All exceptions documented (FiveTwentyError, ValueError, etc.)
7. Special behavior documented (retries, idempotency, etc.)
```

#### 3.3 Code Example Validation
```python
# For each code example:
1. Imports are correct (no Configuration, use AccountConfig)
2. Client initialization uses correct pattern
3. Method calls use correct signatures
4. Variable names don't conflict with module names
5. Example is executable (would run if copy-pasted)
6. Type hints are correct
7. Error handling shown where appropriate
```

#### 3.4 Response Type Validation
```python
# For methods returning TypedDict:
1. All fields documented
2. Field types match TypedDict definition
3. Required vs optional fields correct
4. Field descriptions accurate
5. Nested models referenced correctly
```

#### 3.5 Specific Endpoint Checks

**Accounts Endpoint (`endpoints/accounts.md`):**
- [ ] `get_accounts()` → returns `list[AccountProperties]`
- [ ] `get_account(account_id)` → returns `AccountResponse`
- [ ] `get_account_summary(account_id)` → returns `AccountSummaryResponse`
- [ ] `get_account_instruments(account_id)` → returns `AccountInstrumentsResponse`
- [ ] `patch_account_configuration(account_id, alias, margin_rate)` → returns `AccountConfigurationResponse`
- [ ] `get_account_changes(account_id, since_transaction_id)` → returns `AccountChangesResponse`

**Orders Endpoint (`endpoints/orders.md`):**
- [ ] `post_order(account_id, order)` → unified order placement
- [ ] `post_market_order(...)` → convenience method
- [ ] `post_limit_order(...)` → convenience method
- [ ] `get_orders(account_id, ids, state, instrument, count, before_id)` → filtering
- [ ] `get_pending_orders(account_id)` → convenience wrapper
- [ ] `get_order(account_id, order_id)` → single order
- [ ] `put_order(account_id, order_id, order)` → replace order
- [ ] `cancel_order(account_id, order_id)` → cancel order

**Trades Endpoint (`endpoints/trades.md`):**
- [ ] All trade management methods
- [ ] CRCDO (close, reduce, client extensions, dependent orders) parameters
- [ ] Trade state filtering

**Positions Endpoint (`endpoints/positions.md`):**
- [ ] `get_positions(account_id)` → all positions
- [ ] `get_open_positions(account_id)` → only open
- [ ] `get_position(account_id, instrument)` → single position
- [ ] `close_position(account_id, instrument, long_units, short_units)` → close with units

**Pricing Endpoint (`endpoints/pricing.md`):**
- [ ] `get_pricing(account_id, instruments, since, include_units_available, include_home_conversions)`
- [ ] `get_pricing_stream(account_id, instruments, snapshot, include_home_conversions, stall_timeout)`
- [ ] `get_account_instrument_candles(account_id, instrument, price, granularity, count, from_time, to_time, smooth, include_first, daily_alignment, alignment_timezone, weekly_alignment)`
- [ ] `get_latest_candles(account_id, candle_specifications, units, smooth, daily_alignment, alignment_timezone, weekly_alignment)`
- [ ] `stream_pricing_with_retries(account_id, instruments, snapshot, include_home_conversions, config)` → enhanced streaming

**Instruments Endpoint (`endpoints/instruments.md`):**
- [ ] Methods match SDK exactly
- [ ] Candles parameters documented completely

**Transactions Endpoint (`endpoints/transactions.md`):**
- [ ] `get_transactions(account_id, from_time, to_time, page_size, type)`
- [ ] `get_transaction(account_id, transaction_id)`
- [ ] `get_transactions_range(account_id, from_id, to_id, type)`
- [ ] `get_transactions_since_id(account_id, id)`
- [ ] `get_transactions_stream(account_id)` → streaming

---

### Phase 4: Model Validation (7 Model Files)

**For each model file, perform these validation checks:**

#### 4.1 Model Field Validation
```python
# For each model class:
1. Class name matches SDK Pydantic model exactly
2. All fields documented
3. Field types match Pydantic Field definitions
4. Field aliases match (camelCase for API, snake_case for Python)
5. Required vs optional matches Pydantic (field: Type vs field: Type | None)
6. Default values match model defaults
7. Field descriptions accurate
8. Validation rules documented (Field constraints)
```

#### 4.2 Type Alias Validation
```python
# For type aliases:
1. Alias name matches SDK
2. Underlying type correct
3. Description explains usage
4. Examples show correct usage
```

#### 4.3 Enum Validation
```python
# For enum types:
1. Enum name matches SDK
2. All enum values present
3. Enum values match SDK exactly (case-sensitive)
4. Descriptions for each value
5. Usage examples correct
```

#### 4.4 Union Type Validation
```python
# For union types (Order, Transaction, etc.):
1. All union members documented
2. Type discrimination explained
3. Examples show how to handle each type
4. Safe attribute access patterns shown
```

#### 4.5 Model Cross-Reference Validation
```python
# For fields referencing other models:
1. Link to referenced model correct
2. Referenced model exists in docs
3. Circular references handled correctly
4. TYPE_CHECKING imports documented where relevant
```

#### 4.6 Specific Model Checks

**Account Models (`models/account-models.md`):**
- [ ] `AccountProperties` - basic account info
- [ ] `Account` - complete account details (98+ fields)
- [ ] `AccountSummary` - condensed account info (similar to Account but subset)
- [ ] `AccountChanges` - account change tracking
- [ ] `AccountChangesState` - state after changes
- [ ] `GuaranteedStopLossOrderParameters` - GSL parameters
- [ ] All field types use correct type aliases (AccountID, AccountUnits, DateTime, etc.)

**Order Models (`models/order-models.md`):**
- [ ] All 8+ order types documented (Market, Limit, Stop, MIT, TP, SL, GSL, TSL)
- [ ] Order request models
- [ ] Order response models
- [ ] Order state models
- [ ] Client extensions documented
- [ ] Dependent order models (TP/SL attached to entry)
- [ ] Union type handling explained

**Trading Models (`models/trading-models.md`):**
- [ ] `Trade` model
- [ ] `TradeSummary` model
- [ ] `Position` model
- [ ] `PositionSide` model
- [ ] `CalculatedPositionState` model

**Transaction Models (`models/transaction-models.md`):**
- [ ] All 20+ transaction types documented
- [ ] Transaction union type explained
- [ ] Type discrimination patterns
- [ ] Common fields vs type-specific fields

**Market Data Models (`models/market-data-models.md`):**
- [ ] `ClientPrice` model
- [ ] `PricingHeartbeat` model
- [ ] `Candlestick` model
- [ ] `CandlestickData` model
- [ ] `HomeConversions` model

**Enum Models (`models/enum-models.md`):**
- [ ] All enums from `enums.py` documented
- [ ] `OrderType`, `OrderState`, `OrderPositionFill`
- [ ] `CandlestickGranularity`
- [ ] `GuaranteedStopLossOrderMode`
- [ ] All other enums

**System Models (`models/system-models.md`):**
- [ ] Type aliases: AccountID, TransactionID, AccountUnits, InstrumentName, DateTime
- [ ] Base model information
- [ ] `ValidationViolation` model
- [ ] `ApiModel` base class

---

### Phase 5: Exception & Error Handling Validation

#### 5.1 Exception Class Validation (`exceptions.md`)

```python
# For each exception class:
1. Class name matches SDK
2. Exception hierarchy correct
3. Constructor parameters documented
4. Attributes documented
5. Usage examples correct
6. When it's raised documented
```

**Specific Checks:**
- [ ] `FiveTwentyError` - base exception
  - [ ] `status_code` attribute
  - [ ] `error_code` attribute
  - [ ] `error_message` attribute
  - [ ] `details` attribute (ErrorDetails)
  - [ ] `request_id` attribute
  - [ ] `response` attribute
- [ ] `StreamStall` - streaming exception
  - [ ] Inheritance from FiveTwentyError
  - [ ] When raised (stall_timeout exceeded)

#### 5.2 Error Handling Patterns (`error-handling.md`)

```python
# Validate documented patterns:
1. Try-except patterns correct
2. Error inspection examples work
3. Retry patterns match SDK behavior
4. Idempotency behavior documented correctly
5. Status code handling correct
```

---

### Phase 6: Code Example Validation

**Automated validation of every code block:**

#### 6.1 Import Validation
```python
# For each code example:
1. All imports exist in SDK
2. Import paths correct
3. No deprecated imports (Configuration → AccountConfig)
4. No unused imports
5. Required imports present
```

#### 6.2 Syntax Validation
```python
# Run through validators:
1. Python syntax valid
2. Type hints valid
3. No undefined names
4. No module attribute access errors
```

#### 6.3 Semantic Validation
```python
# Verify correctness:
1. Client initialization pattern correct
2. Method calls use correct signatures
3. Error handling appropriate
4. Type annotations accurate
5. Variable names don't shadow modules
```

#### 6.4 Execution Validation
```python
# Where possible, verify examples run:
1. Examples that don't require API calls can be validated
2. Examples with API calls can be mocked and validated
3. Async examples use correct patterns
4. Context managers used correctly
```

---

### Phase 7: Cross-Reference Validation

#### 7.1 Internal Link Validation
```python
# For every markdown link:
1. Target file exists
2. Target anchor exists
3. Link text accurate
4. No broken links
5. Relative paths correct
```

#### 7.2 Model Reference Validation
```python
# For every model field referencing another model:
1. Link points to correct model section
2. Referenced model documented
3. Link format consistent
```

#### 7.3 Method Reference Validation
```python
# For every method cross-reference:
1. Method exists in SDK
2. Link points to correct section
3. Method name spelled correctly
```

---

### Phase 8: OANDA API Validation

#### 8.1 Endpoint URL Validation
```python
# For each documented endpoint:
1. URL path matches OANDA API spec
2. HTTP method correct (GET/POST/PUT/PATCH/DELETE)
3. Account ID placeholder correct {accountID}
4. Query parameters documented
5. Request body structure correct
```

#### 8.2 OANDA Documentation Links
```python
# For each OANDA doc link:
1. URL is accessible
2. Points to correct section
3. OANDA doc version correct (v20)
4. Link not deprecated
```

---

### Phase 9: Completeness Validation

#### 9.1 SDK Coverage Check
```python
# Verify 100% SDK coverage:
1. All public classes documented
2. All public methods documented
3. All public properties documented
4. All models documented
5. All enums documented
6. All exceptions documented
7. No undocumented features
```

#### 9.2 Missing Documentation Detection
```python
# Scan SDK for undocumented features:
for module in SDK_MODULES:
    for name in module.__all__:
        if not documented(name):
            report_missing(name)
```

---

### Phase 10: Consistency Validation

#### 10.1 Terminology Consistency
```python
# Verify consistent terminology:
1. "Account ID" vs "account_id" used consistently
2. "Transaction ID" vs "transaction_id" used consistently
3. Model names match SDK exactly
4. Field names use snake_case in Python, camelCase for API
```

#### 10.2 Format Consistency
```python
# Verify consistent formatting:
1. Code blocks use correct language tags
2. Tables formatted consistently
3. Headers follow hierarchy
4. Parameter tables use same columns
5. Return value sections formatted same way
```

#### 10.3 Example Consistency
```python
# Verify example patterns:
1. All examples use async with context manager
2. All examples import from correct locations
3. All examples use zero-config pattern where appropriate
4. All examples handle errors appropriately
```

---

## Validation Execution Strategy

### Automated Validation (Where Possible)
1. **Linting:** All code examples through ruff
2. **Type Checking:** All code examples through mypy
3. **Syntax:** All code through Python parser
4. **Links:** All markdown links through link checker
5. **Imports:** Verify all imports resolve

### Manual Validation (Required)
1. **Semantic Correctness:** Human review of descriptions
2. **API Accuracy:** Compare with OANDA API docs
3. **Model Completeness:** Compare with Pydantic models
4. **Method Signatures:** Line-by-line comparison with SDK
5. **Return Types:** Verify against actual SDK returns

### Validation Order
1. Start with foundational docs (client, configuration)
2. Move to endpoints (validates against client)
3. Then models (validates against endpoints)
4. Then exceptions (validates against all)
5. Finally cross-references and links

---

## Issue Tracking

### Issue Categories
1. **Critical:** Wrong signature, incorrect return type, missing required parameter
2. **High:** Incomplete documentation, incorrect example, broken link
3. **Medium:** Missing optional parameter, unclear description
4. **Low:** Formatting inconsistency, minor typo

### Issue Format
```markdown
**File:** docs/api-reference/client.md
**Line:** 42
**Severity:** Critical
**Issue:** Constructor signature shows `Configuration` but SDK uses `AccountConfig`
**Expected:** `config: AccountConfig | None = None`
**Actual:** `config: Configuration | None = None`
**Fix:** Update import and type annotation
```

---

## Success Criteria

Validation is complete when:
- [ ] Every SDK class has complete documentation
- [ ] Every SDK method has complete documentation
- [ ] Every method signature matches SDK exactly
- [ ] Every model field matches Pydantic definition
- [ ] Every code example passes linting
- [ ] Every code example passes type checking
- [ ] Every code example is executable (or mockable)
- [ ] Every internal link works
- [ ] Every OANDA API reference is correct
- [ ] Zero critical or high severity issues remain
- [ ] 100% SDK coverage achieved

---

## Validation Tools

### Custom Scripts Needed
1. **SDK Scanner:** Extract all public APIs from SDK
2. **Doc Scanner:** Extract all documented APIs from docs
3. **Diff Tool:** Compare SDK vs docs and report discrepancies
4. **Link Checker:** Validate all markdown links
5. **Import Validator:** Verify all imports resolve
6. **Example Runner:** Execute/mock all code examples

### Existing Tools
1. **ruff:** Lint all code examples
2. **mypy:** Type check all code examples
3. **pytest:** Run validation tests
4. **vale:** Check documentation writing quality

---

## Estimated Effort

- **Phase 1-2 (Client/Config):** ~4-6 hours
- **Phase 3 (7 Endpoints):** ~14-21 hours (2-3 hours per endpoint)
- **Phase 4 (7 Models):** ~21-28 hours (3-4 hours per model file)
- **Phase 5 (Exceptions):** ~3-4 hours
- **Phase 6 (Code Examples):** ~8-12 hours
- **Phase 7 (Cross-refs):** ~4-6 hours
- **Phase 8 (OANDA):** ~4-6 hours
- **Phase 9 (Completeness):** ~4-6 hours
- **Phase 10 (Consistency):** ~3-4 hours

**Total Estimated Effort:** 65-93 hours

---

## Notes

This plan ensures **every single line** of API reference documentation is validated against the SDK through:
1. Automated tooling (linting, type checking, syntax validation)
2. Programmatic comparison (signature matching, field verification)
3. Manual review (semantic correctness, accuracy)
4. Cross-validation (links, references, consistency)

The systematic approach guarantees no documentation errors remain and establishes complete SDK coverage.
