# FiveTwenty Documentation Code Validation Report

Generated: /Users/antares/dev/fivetwenty

## Summary

- **Total Files Analyzed**: 72
- **Total Issues**: 3558
  - **Errors**: 130 ❌
  - **Warnings**: 3428 ⚠️
- **Success Rate**: 0.5%

## Issue Categories

### Most Common Rule Violations

- **code_undefined_variable**: 3399 issues
- **code_async_outside_function**: 89 issues
- **code_missing_account_id**: 41 issues
- **code_import_unavailable**: 28 issues
- **markdown_list_spacing**: 1 issues


## Detailed Analysis by File

Files sorted by issue count (highest first):


### 📄 /docs/how-to-guides/production-deployment/monitoring-observability.md

**Issues**: 221 total (0 errors, 221 warnings)


### 📄 /docs/how-to-guides/production-deployment/security-compliance.md

**Issues**: 198 total (0 errors, 198 warnings)


### 📄 /docs/tutorials/advanced-orders/validation-best-practices.md

**Issues**: 196 total (0 errors, 196 warnings)


### 📄 /docs/contributing/code-style.md

**Issues**: 173 total (1 errors, 172 warnings)

#### Errors ❌

- **Line 477**: AsyncClient with token parameter requires account_id parameter
  - Context: `return AsyncClient(token="test-token", environment="practice")`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/explanation/best-practices.md

**Issues**: 169 total (1 errors, 168 warnings)

#### Errors ❌

- **Line 1000**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'


### 📄 /docs/tutorials/advanced-orders/automated-systems.md

**Issues**: 159 total (0 errors, 159 warnings)


### 📄 /docs/how-to-guides/manage-orders-effectively.md

**Issues**: 125 total (7 errors, 118 warnings)

#### Errors ❌

- **Line 31**: 'async with' or 'await' found outside async function
  - Context: `await client.orders.post_market_order(`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 45**: 'async with' or 'await' found outside async function
  - Context: `market_response = await client.orders.post_market_order(`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 629**: 'async with' or 'await' found outside async function
  - Context: `order_details = await client.orders.get_order(account_id, 
order_id)`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 639**: 'async with' or 'await' found outside async function
  - Context: `account = await client.accounts.get_account(account_id)`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 653**: 'async with' or 'await' found outside async function
  - Context: `account = await client.accounts.get_account(account_id)`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'


### 📄 /docs/how-to-guides/implement-stop-loss-strategies.md

**Issues**: 120 total (9 errors, 111 warnings)

#### Errors ❌

- **Line 34**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token="your-token", 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 104**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token="your-token", 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 161**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token="your-token", 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 243**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token="your-token", 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 311**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token="your-token", 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/tutorials/decimal-best-practices.md

**Issues**: 119 total (0 errors, 119 warnings)


### 📄 /docs/api-reference/configuration.md

**Issues**: 113 total (3 errors, 110 warnings)

#### Errors ❌

- **Line 701**: AsyncClient with token parameter requires account_id parameter
  - Context: `client = AsyncClient(token="token", 
environment=Environment.PRACTICE)`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 701**: AsyncClient with token parameter requires account_id parameter
  - Context: `client = AsyncClient(token="token", 
environment=Environment.PRACTICE)`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 723**: AsyncClient with token parameter requires account_id parameter
  - Context: `client = AsyncClient(token=token, 
environment=Environment.PRACTICE)`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/explanation/error-handling.md

**Issues**: 104 total (0 errors, 104 warnings)


### 📄 /docs/contributing/testing-guide.md

**Issues**: 100 total (2 errors, 98 warnings)

#### Errors ❌

- **Line 165**: AsyncClient with token parameter requires account_id parameter
  - Context: `return AsyncClient(token="test-token", environment="practice")`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 456**: AsyncClient with token parameter requires account_id parameter
  - Context: `return AsyncClient(token="test-token", environment="practice")`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/explanation/configuration.md

**Issues**: 95 total (9 errors, 86 warnings)

#### Errors ❌

- **Line 70**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient() as client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 133**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(config=practice_config) as practice_client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 161**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient() as client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 179**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(config=momentum_config) as momentum_client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 311**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'


### 📄 /docs/tutorials/getting-started/authentication.md

**Issues**: 89 total (13 errors, 76 warnings)

#### Errors ❌

- **Line 81**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient() as client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 125**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient() as client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 159**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(config=practice_config) as practice_client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 194**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(config=momentum_config) as momentum_client:`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'

- **Line 327**: 'async with' or 'await' found outside async function
  - Context: `async with AsyncClient(`
  - Rule: `code_async_outside_function`
  - 💡 Wrap async code in 'async def main():' function and call with 
'asyncio.run(main())'


### 📄 /docs/tutorials/advanced-orders/order-strategies.md

**Issues**: 88 total (0 errors, 88 warnings)


### 📄 /docs/tutorials/getting-started/environments.md

**Issues**: 73 total (0 errors, 73 warnings)


### 📄 /docs/tutorials/advanced-orders/dynamic-management.md

**Issues**: 64 total (0 errors, 64 warnings)


### 📄 /docs/tutorials/basic-trading/lesson-5-position-management.md

**Issues**: 63 total (1 errors, 62 warnings)

#### Errors ❌

- **Line 26**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as 
client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/explanation/async-vs-sync.md

**Issues**: 58 total (4 errors, 54 warnings)

#### Errors ❌

- **Line 164**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=token, 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 193**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=token, 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 284**: AsyncClient with token parameter requires account_id parameter
  - Context: `client = AsyncClient(token="your-token", 
environment=Environment.PRACTICE)`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 345**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=token, 
environment=Environment.PRACTICE) as client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call


### 📄 /docs/tutorials/risk-management/stop-loss-strategies.md

**Issues**: 56 total (2 errors, 54 warnings)

#### Errors ❌

- **Line 38**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as 
client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call

- **Line 122**: AsyncClient with token parameter requires account_id parameter
  - Context: `async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as 
client:`
  - Rule: `code_missing_account_id`
  - 💡 Add account_id='your-account-id' parameter to AsyncClient call



## Recommendations

### High Priority Fixes (Errors)

1. **Async Function Wrappers**: 89 files need proper async function wrappers
   - Add `async def main():` wrapper around async code
   - Add `asyncio.run(main())` to execute async functions
   - Most affected: API reference documentation

2. **Missing Account ID**: 41 instances need account_id parameter
   - Add `account_id` parameter when providing token directly to AsyncClient

### Medium Priority Fixes (Warnings)

1. **Missing Imports**: 3399 undefined variables
   - Add proper import statements at the top of code examples
   - Most common missing imports: AsyncClient, Environment, Decimal, InstrumentName

2. **Import Organization**: Standardize import statements across all code examples

### Suggested Action Plan

1. **Phase 1**: Fix all async function wrapper errors (89 issues)
2. **Phase 2**: Add missing imports to reduce warning noise
3. **Phase 3**: Create code example templates for consistency

## Files Requiring Immediate Attention

These files have the most critical errors:

- **/docs/explanation/forex-trading-concepts.md**: 17 errors
- **/docs/tutorials/getting-started/authentication.md**: 13 errors
- **/docs/api-reference/endpoints/orders.md**: 11 errors
- **/docs/explanation/configuration.md**: 9 errors
- **/docs/how-to-guides/implement-stop-loss-strategies.md**: 9 errors
- **/docs/explanation/sdk-architecture.md**: 7 errors
- **/docs/how-to-guides/manage-orders-effectively.md**: 7 errors
- **/docs/api-reference/endpoints/accounts.md**: 6 errors
- **/docs/api-reference/endpoints/trades.md**: 6 errors
- **/docs/api-reference/endpoints/transactions.md**: 5 errors


## Validation Configuration

The validation is currently configured to check:

- ✅ Python syntax in code blocks
- ✅ Async/await usage patterns
- ✅ FiveTwenty-specific API usage
- ✅ Import availability
- ✅ Variable definition checking

Consider adjusting validation rules based on this report to focus on the most impactful issues.
