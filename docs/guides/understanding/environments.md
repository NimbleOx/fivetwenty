# Practice vs Live Trading Environments

**Problem**: Understanding when and how to use OANDA's practice and live trading environments safely.

**Solution**: Learn the differences between environments, when to use each, and how to transition from development to production trading.

---

## Prerequisites

- FiveTwenty installed and configured
- Basic understanding of trading concepts
- OANDA account (practice accounts are free)

---

## Environment Overview

OANDA runs two separate trading environments. Each has a different job in your development workflow.

### Practice Environment

The practice environment trades virtual funds against real market data:

**Key Features:**
- $100,000 virtual starting balance
- Real-time market data and spreads
- Complete API functionality
- No real money risk
- Instant account creation

**Best For:**
- Learning OANDA trading concepts
- Testing new trading strategies
- Developing and debugging code
- Experimenting with position sizes
- Algorithm backtesting with live data

<!-- fragment: Demo practice environment configuration with comprehensive safety explanations -->
```python
from fivetwenty import AsyncClient, Environment


async def demonstrate_practice_environment_safety() -> None:
    """Demonstrate practice environment configuration with comprehensive safety explanations."""
    print(f"Practice Environment Configuration Demo")

    # Step 1: Initialize AsyncClient with practice environment
    # Practice environment is ALWAYS safe - uses virtual money only
    # OANDA provides $100,000 virtual starting balance for testing
    print(f"\nNote: Environment Configuration:")
    print(f"   Token type: Practice token (safe for experimentation)")
    print(f"   Environment: Practice (virtual money only)")
    print(f"   Starting balance: $100,000 virtual funds")
    print(f"   Risk level: ZERO - no real money involved")

    async with AsyncClient(
        token="your-practice-token",                    # Practice token - separate from live
        environment=Environment.PRACTICE                # Explicit practice environment
    ) as client:

        # Step 2: Verify environment configuration for safety
        # Always confirm you're in practice mode before any operations
        print(f"\nSuccess Environment Verification:")
        print(f"   Current environment: {client.config.environment.value}")
        print(f"   Real money risk: {'YES - DANGER!' if client.config.environment.value == 'live' else 'NO - Safe'}")

        # Step 3: Retrieve account information to understand virtual balance
        # Practice accounts have generous virtual balances for testing
        accounts = await client.accounts.get_accounts()
        practice_account = accounts[0]  # First account in practice environment

        print(f"\nStarting balance: Practice Account Details:")
        print(f"   Account ID: {practice_account.id}")
        print(f"   Virtual balance: ${practice_account.balance}")
        print(f"   Currency: {practice_account.currency}")
        print(f"   Account type: Virtual trading account")

        # Step 4: Demonstrate safe experimentation capabilities
        # Practice environment allows aggressive testing without consequences
        print(f"\nTesting: Safe Experimentation Features:")
        print(f"   Test large position sizes without risk")
        print(f"   Experiment with complex strategies")
        print(f"   Learn from mistakes without financial loss")
        print(f"   Real-time market data with virtual execution")
        print(f"   Complete API functionality available")

        print(f"\nNote Practice Environment Benefits:")
        print(f"   Perfect for learning OANDA trading concepts")
        print(f"   Ideal for strategy development and testing")
        print(f"   Safe environment for debugging trading code")
        print(f"   Risk-free algorithm validation")

        return practice_account.balance


# Usage example - always start here for any new development
print(f"Starting Practice Environment Demo")
try:
    import asyncio
    balance = asyncio.run(demonstrate_practice_environment_safety())
    print(f"Practice environment successfully configured with ${balance} virtual balance")
except Exception as e:
    print(f"Configuration error: {e}")
print(f"Remember: Practice environment is ALWAYS safe for experimentation")
```

### Live Environment

The live environment executes real trades with actual money:

**Key Features:**
- Real money trading
- Live market execution
- Production-grade infrastructure
- KYC verification required
- Account funding required

**Use Only When:**
- Strategy is thoroughly tested in practice
- Code is production-ready with proper error handling
- Risk management is implemented
- You understand the financial implications

<!-- fragment: Demo live environment with comprehensive safety warnings and balance verification -->
```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment


async def demonstrate_live_environment_safety() -> str:
    """Demonstrate live environment with comprehensive safety warnings and balance verification."""
    print(f"⚠️ LIVE ENVIRONMENT DEMONSTRATION - REAL MONEY AT RISK!")

    # Step 1: Critical safety warnings before live environment access
    # Live environment uses REAL MONEY - every operation has financial consequences
    print(f"\n⚠️ CRITICAL SAFETY WARNINGS:")
    print(f"   💸 Real money: Every trade uses actual funds")
    print(f"   Live execution: Orders execute immediately in real markets")
    print(f"   Hot Financial risk: Losses are real and permanent")
    print(f"   ⚠️ Regulatory implications: KYC verification required")
    print(f"   💳 Account funding: Real money must be deposited")

    # Step 2: Pre-live environment checklist verification
    print(f"\nCurrent environment: PRE-LIVE CHECKLIST (verify before proceeding):")
    print(f"   Strategy thoroughly tested in practice environment")
    print(f"   Code production-ready with comprehensive error handling")
    print(f"   Risk management rules implemented and tested")
    print(f"   Position sizing appropriate for account balance")
    print(f"   Stop losses and emergency procedures defined")
    print(f"   Regulatory compliance and KYC completed")

    # Step 3: Initialize live environment client with maximum caution
    # Only proceed if ALL safety requirements are met
    print(f"\nLock Initializing Live Environment Client...")

    async with AsyncClient(
        token="your-live-token",                        # Live token - access to real money
        environment=Environment.LIVE                    # LIVE environment - real financial risk
    ) as client:

        # Step 4: Mandatory environment verification for live trading
        # Always double-check you're in the intended environment
        print(f"\nAnalysis: MANDATORY ENVIRONMENT VERIFICATION:")
        current_env = client.config.environment.value
        print(f"   Environment: {current_env.upper()}")
        print(f"   ⚠️ Risk level: {'MAXIMUM - REAL MONEY' if current_env == 'live' else 'Safe'}")

        if current_env != "live":
            print(f"   Error Environment mismatch - expected live, got {current_env}")
            return "Environment verification failed"

        # Step 5: Retrieve and analyze live account balance with safety checks
        # Live account balance represents real money - handle with extreme care
        accounts = await client.accounts.get_accounts()
        live_account = accounts[0]  # Primary live trading account

        # Convert balance to Decimal for precise financial calculations
        account_balance = Decimal(live_account.balance)

        print(f"\nStarting balance: LIVE ACCOUNT FINANCIAL STATUS:")
        print(f"   Account ID: {live_account.id}")
        print(f"   Real balance: ${account_balance}")
        print(f"   Currency: {live_account.currency}")
        print(f"   Account type: LIVE TRADING ACCOUNT")

        # Step 6: Implement safety thresholds for live trading
        # Protect against insufficient balance or excessive risk
        minimum_safe_balance = Decimal("1000.00")  # $1000 minimum for safe live trading

        print(f"\nSAFETY SAFETY THRESHOLD ANALYSIS:")
        if account_balance < minimum_safe_balance:
            print(f"   ⚠️ WARNING: Balance ${account_balance} below safe minimum ${minimum_safe_balance}")
            print(f"   Note Consider depositing more funds or reducing position sizes")
            print(f"   Security: Recommendation: Start with micro-lots or return to practice")
        else:
            print(f"   Balance ${account_balance} meets safety threshold")
            print(f"   Note Safe to proceed with conservative position sizing")

        # Step 7: Calculate recommended maximum position size
        # Conservative risk management: never risk more than 1-2% per trade
        max_risk_percentage = Decimal("0.02")  # 2% maximum risk per trade
        max_risk_amount = account_balance * max_risk_percentage

        print(f"\nRisk-free algorithm validationRISK MANAGEMENT CALCULATIONS:")
        print(f"   Account balance: ${account_balance}")
        print(f"   Max risk per trade (2%): ${max_risk_amount:.2f}")
        print(f"   Recommended approach: Start with 0.5% risk or less")
        print(f"   Position sizing: Calculate based on stop loss distance")

        # Step 8: Final safety reminders for live trading
        print(f"\n⚠️ FINAL SAFETY REMINDERS:")
        print(f"   ⚠️ Every click/order costs real money")
        print(f"   Mobile Monitor positions actively during market hours")
        print(f"   Stop Have emergency stop procedures ready")
        print(f"   Keep detailed records for tax purposes")
        print(f"   Consider additional education before significant trading")

        return str(account_balance)


# Critical safety warning before any live environment access
print(f"⚠️ LIVE ENVIRONMENT ACCESS - READ ALL WARNINGS FIRST")
print(f"Note: Only proceed if you understand financial risks and have tested thoroughly")
try:
    import asyncio
    # Uncomment only when ready for live trading with real money
    # balance = asyncio.run(demonstrate_live_environment_safety())
    # print(f"Live environment balance verified: ${balance}")
    print(f"⚠️ Live environment demo commented out for safety")
    print(f"Uncomment only when ready for real money trading")
except Exception as e:
    print(f"Live environment error: {e}")
print(f"Security: Remember: Live environment = Real money = Real risk")
```

---

## Development Workflow

### Phase 1: Development (Practice Only)

Start all development in the practice environment:

<!-- fragment: Demo development trading with comprehensive environment variable management -->
```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment


async def demonstrate_development_trading_workflow() -> None:
    """Demonstrate development phase trading with comprehensive environment variable management."""
    print(f"Development Trading Workflow Demonstration")

    # Step 1: Environment variable validation for development safety
    # Always verify environment variables are properly configured
    print(f"\nNote: Environment Variable Validation:")

    # Check for required practice environment variables
    required_env_vars = {
        "PRACTICE_TOKEN": "Practice API token for safe testing",
        "PRACTICE_ACCOUNT": "Practice account ID (optional - can auto-detect)"
    }

    missing_vars = []
    for var_name, description in required_env_vars.items():
        if var_name in os.environ:
            # Mask token for security (show only first/last few characters)
            if "TOKEN" in var_name:
                token_value = os.environ[var_name]
                masked_token = f"{token_value[:8]}...{token_value[-4:]}"
                print(f"   {var_name}: {masked_token} ({description})")
            else:
                print(f"   {var_name}: {os.environ[var_name]} ({description})")
        else:
            missing_vars.append(var_name)
            print(f"   Error {var_name}: Missing ({description})")

    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print(f"Note: Set up .env file with: PRACTICE_TOKEN=your-practice-token")
        return

    # Step 2: Initialize client with practice environment for development
    # Development phase should ALWAYS use practice environment for safety
    print(f"\nTesting: Development Client Initialization:")
    print(f"   Environment: Practice (safe for aggressive testing)")
    print(f"   Risk level: Zero - virtual money only")
    print(f"   Purpose: Strategy development and code testing")

    async with AsyncClient(
        token=os.environ["PRACTICE_TOKEN"],                # Practice token from environment
        environment=Environment.PRACTICE                   # Explicit practice environment
    ) as client:

        # Step 3: Verify development environment configuration
        # Double-check we're in practice mode for development safety
        print(f"\nSuccess Development Environment Verification:")
        print(f"   Environment: {client.config.environment.value}")
        print(f"   Security: Safety status: {'SAFE' if client.config.environment.value == 'practice' else 'UNSAFE'}")

        # Step 4: Retrieve account for development testing
        # Practice accounts provide generous virtual balance for testing
        accounts = await client.accounts.get_accounts()
        development_account = accounts[0]  # Primary development account

        print(f"\nStarting balance: Development Account Status:")
        print(f"   Account ID: {development_account.id}")
        print(f"   Virtual balance: ${development_account.balance}")
        print(f"   Available for testing: Full balance (virtual)")

        # Step 5: Development trading with aggressive testing parameters
        # Practice environment allows testing with larger positions safely
        print(f"\nTesting: Development Trading Parameters:")

        # Calculate development position size (can be aggressive in practice)
        virtual_balance = Decimal(development_account.balance)
        development_position = 10000  # 10K units - safe for practice testing

        # Position size as percentage of virtual balance for context
        position_percentage = (Decimal(str(development_position)) / virtual_balance) * 100

        print(f"   Instrument: EUR_USD (major pair for stable testing)")
        print(f"   Position size: {development_position:,} units")
        print(f"   Position value: ~${development_position * Decimal('1.10'):,.2f} (approx)")
        print(f"   📉 Account percentage: {position_percentage:.2f}% of virtual balance")
        print(f"   Risk assessment: Safe - virtual money only")

        # Step 6: Execute development test order with comprehensive logging
        # Development orders help validate strategy logic and error handling
        try:
            print(f"\nStarting Executing Development Test Order...")

            test_order = await client.orders.post_market_order(
                account_id=development_account.id,
                instrument="EUR_USD",                          # Major pair for reliable execution
                units=development_position                      # Larger size OK for development testing
            )

            # Step 7: Analyze development order execution results
            # Extract key information for development workflow validation
            fill_transaction = test_order.order_fill_transaction

            print(f"\nSuccess Development Order Execution Results:")
            print(f"   Transaction ID: {fill_transaction.id}")
            print(f"   Filled price: {fill_transaction.price}")
            print(f"   Units filled: {fill_transaction.units}")
            print(f"   Virtual P/L impact: {fill_transaction.pl} (immediate)")
            print(f"   Time Execution time: {fill_transaction.time}")

            # Step 8: Development phase learning opportunities
            print(f"\nPerfect for learning: Development Phase Learning Opportunities:")
            print(f"   Strategy logic validation: Order executed successfully")
            print(f"   API integration test: Client communication working")
            print(f"   Error handling test: No exceptions encountered")
            print(f"   Position management: Can track fills and P/L")

            print(f"\nNote Next Development Steps:")
            print(f"   Test edge cases (invalid instruments, large orders)")
            print(f"   Tools Add stop losses and take profits")
            print(f"   Implement position size calculations")
            print(f"   Processing Test error recovery scenarios")
            print(f"   Validate strategy with multiple instruments")

        except Exception as e:
            # Step 9: Development error handling and learning
            # Errors in development phase are learning opportunities
            print(f"\nError Development Order Error: {e}")
            print(f"Note: Development Error Analysis:")
            print(f"   Analysis: Error type: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            print(f"   Tools Next steps: Analyze error and adjust code")
            print(f"   Safety: No real money at risk during development")


# Development workflow execution
print(f"Starting Development Trading Workflow")
try:
    import asyncio
    asyncio.run(demonstrate_development_trading_workflow())
except Exception as e:
    print(f"Development workflow error: {e}")
    print(f"Note: Check environment variables and practice token validity")
print(f"Development trading workflow demonstration complete")
print(f"Remember: Development phase = Practice environment = Safe experimentation")
```

### Phase 2: Testing (Practice Environment)

Validate your strategy thoroughly:

<!-- fragment: Demo comprehensive strategy validation with detailed error analysis -->
```python
import os
import time
from decimal import Decimal
from typing import Dict, List, Any
from fivetwenty import AsyncClient, Environment


async def demonstrate_comprehensive_strategy_validation() -> None:
    """Demonstrate comprehensive strategy validation with detailed error analysis."""
    print(f"Comprehensive Strategy Validation Demonstration")

    # Step 1: Define comprehensive test scenarios for strategy validation
    # Test scenarios should cover different market conditions and instruments
    print(f"\nCurrent environment: Strategy Validation Test Plan:")

    # Define test scenarios with detailed parameters for validation
    test_scenarios = [
        {
            "name": "Major Pair Test - Conservative",
            "instrument": "EUR_USD",               # Most liquid major pair
            "units": 1000,                         # Conservative position size
            "expected_spread": Decimal("0.0002"),  # Typical EUR/USD spread
            "rationale": "Test basic functionality with most stable pair"
        },
        {
            "name": "Major Pair Test - Medium Position",
            "instrument": "GBP_USD",               # Volatile major pair
            "units": 2000,                         # Medium position size
            "expected_spread": Decimal("0.0003"),  # Typical GBP/USD spread
            "rationale": "Test strategy with higher volatility instrument"
        },
        {
            "name": "Cross Pair Test - Standard",
            "instrument": "USD_JPY",               # Major yen cross
            "units": 1500,                         # Standard position size
            "expected_spread": Decimal("0.002"),   # JPY pairs quoted differently
            "rationale": "Test strategy with different quote currency"
        },
        {
            "name": "Exotic Pair Test - Small Position",
            "instrument": "AUD_CAD",               # Minor pair
            "units": 500,                          # Smaller position for exotic
            "expected_spread": Decimal("0.0005"),  # Wider spread for minor pair
            "rationale": "Test strategy with less liquid instrument"
        }
    ]

    # Display test scenario overview for validation planning
    print(f"\nRisk-free algorithm validationTest Scenarios Overview:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"   {i}. {scenario['name']}")
        print(f"      Instrument: {scenario['instrument']}")
        print(f"      Position: {scenario['units']:,} units")
        print(f"      Note Purpose: {scenario['rationale']}")

    # Step 2: Initialize practice client for comprehensive validation
    print(f"\nTesting: Initializing Validation Environment:")
    print(f"   Environment: Practice (safe for comprehensive testing)")
    print(f"   Risk level: Zero - virtual money validation")
    print(f"   Validation scope: Multi-instrument strategy testing")

    async with AsyncClient(
        token=os.environ["PRACTICE_TOKEN"],                # Practice token for safe validation
        environment=Environment.PRACTICE                   # Explicit practice environment
    ) as client:

        # Step 3: Pre-validation environment and account checks
        # Verify environment and account status before strategy validation
        print(f"\nSuccess Pre-Validation Checks:")
        print(f"   Environment: {client.config.environment.value}")
        print(f"   Account ID: {client.account_id}")

        # Get account status for validation context
        account = await client.accounts.get_account(client.account_id)
        starting_balance = Decimal(account.balance)
        print(f"   Starting balance: ${starting_balance}")
        print(f"   Available margin: ${account.margin_available}")

        # Step 4: Initialize validation tracking and results
        # Comprehensive tracking helps identify strategy strengths/weaknesses
        validation_results = {
            "total_tests": len(test_scenarios),
            "successful_tests": 0,
            "failed_tests": 0,
            "execution_times": [],
            "spread_analysis": {},
            "error_patterns": [],
            "performance_metrics": {}
        }

        print(f"\nStarting Starting Strategy Validation Tests...")

        # Step 5: Execute comprehensive validation test scenarios
        for test_number, scenario in enumerate(test_scenarios, 1):
            print(f"\n--- Test {test_number}/{len(test_scenarios)}: {scenario['name']} ---")

            # Record test start time for performance analysis
            test_start_time = time.perf_counter()

            try:
                # Step 6: Execute individual test scenario with detailed logging
                print(f"   Instrument: {scenario['instrument']}")
                print(f"   Position size: {scenario['units']:,} units")
                print(f"   Note Test rationale: {scenario['rationale']}")

                # Execute market order for strategy validation
                test_order = await client.orders.post_market_order(
                    account_id=client.account_id,
                    instrument=scenario["instrument"],
                    units=scenario["units"]
                )

                # Step 7: Analyze successful test execution results
                fill_transaction = test_order.order_fill_transaction
                execution_time = time.perf_counter() - test_start_time

                # Extract execution metrics for validation analysis
                filled_price = Decimal(fill_transaction.price)
                filled_units = int(fill_transaction.units)
                immediate_pl = Decimal(fill_transaction.pl)

                print(f"   Execution successful:")
                print(f"      Transaction ID: {fill_transaction.id}")
                print(f"      Fill price: {filled_price}")
                print(f"      Units filled: {filled_units:,}")
                print(f"      Immediate P/L: ${immediate_pl}")
                print(f"      Time Execution time: {execution_time:.3f} seconds")

                # Step 8: Record successful validation metrics
                validation_results["successful_tests"] += 1
                validation_results["execution_times"].append(execution_time)
                validation_results["performance_metrics"][scenario["instrument"]] = {
                    "execution_time": execution_time,
                    "fill_price": str(filled_price),
                    "immediate_pl": str(immediate_pl),
                    "status": "success"
                }

                print(f"   Validation status: PASSED")

            except Exception as validation_error:
                # Step 9: Comprehensive error analysis for validation learning
                execution_time = time.perf_counter() - test_start_time

                print(f"   Error Validation test failed:")
                print(f"      Analysis: Error type: {type(validation_error).__name__}")
                print(f"      Error message: {str(validation_error)}")
                print(f"      Time Time to failure: {execution_time:.3f} seconds")

                # Analyze error patterns for strategy improvement
                error_analysis = {
                    "test_name": scenario["name"],
                    "instrument": scenario["instrument"],
                    "error_type": type(validation_error).__name__,
                    "error_message": str(validation_error),
                    "units_attempted": scenario["units"]
                }

                validation_results["failed_tests"] += 1
                validation_results["error_patterns"].append(error_analysis)

                # Step 10: Error categorization for strategic insights
                if "401" in str(validation_error) or "403" in str(validation_error):
                    print(f"      Note Error category: Authentication/Authorization")
                    print(f"      Tools Suggestion: Check token validity and permissions")
                elif "400" in str(validation_error):
                    print(f"      Note Error category: Invalid Request Parameters")
                    print(f"      Tools Suggestion: Verify instrument and position size")
                elif "Market" in str(validation_error) or "Closed" in str(validation_error):
                    print(f"      Note Error category: Market Conditions")
                    print(f"      Tools Suggestion: Check market hours and instrument availability")
                else:
                    print(f"      Note Error category: Unexpected/Network")
                    print(f"      Tools Suggestion: Check network connectivity and retry")

                print(f"   📉 Validation status: FAILED")

        # Step 11: Comprehensive validation results analysis
        print(f"\nRisk-free algorithm validationStrategy Validation Results Summary:")

        # Calculate validation success metrics
        success_rate = (validation_results["successful_tests"] / validation_results["total_tests"]) * 100
        avg_execution_time = (
            sum(validation_results["execution_times"]) / len(validation_results["execution_times"])
            if validation_results["execution_times"] else 0
        )

        print(f"\nAccount type: Overall Validation Metrics:")
        print(f"   Total tests: {validation_results['total_tests']}")
        print(f"   Successful: {validation_results['successful_tests']}")
        print(f"   Error Failed: {validation_results['failed_tests']}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Time Average execution time: {avg_execution_time:.3f} seconds")

        # Step 12: Strategy readiness assessment based on validation results
        print(f"\n🚦 Strategy Readiness Assessment:")
        if success_rate >= 100:
            print(f"   Green EXCELLENT: All tests passed - strategy ready for live testing")
        elif success_rate >= 75:
            print(f"   Yellow GOOD: Most tests passed - review failed scenarios")
        elif success_rate >= 50:
            print(f"   🟠 MODERATE: Mixed results - significant improvements needed")
        else:
            print(f"   Red POOR: Major issues detected - strategy requires substantial work")

        # Error pattern analysis for improvement guidance
        if validation_results["error_patterns"]:
            print(f"\nAnalysis: Error Pattern Analysis:")
            for error in validation_results["error_patterns"]:
                print(f"   Error {error['test_name']}: {error['error_type']}")
                print(f"      Instrument: {error['instrument']}")
                print(f"      Issue: {error['error_message'][:50]}...")

        # Step 13: Next steps recommendations based on validation results
        print(f"\nNote Next Steps Recommendations:")
        if success_rate == 100:
            print(f"   Perfect validation - ready for advanced testing")
            print(f"   Consider testing with stop losses and take profits")
            print(f"   Test with different market conditions")
            print(f"   Starting Prepare for limited live environment testing")
        else:
            print(f"   Tools Address failed test scenarios before proceeding")
            print(f"   Analysis: Investigate error patterns and root causes")
            print(f"   Testing: Rerun validation after fixing identified issues")
            print(f"   📚 Consider additional practice environment testing")


# Strategy validation execution
print(f"Starting Comprehensive Strategy Validation")
try:
    import asyncio
    asyncio.run(demonstrate_comprehensive_strategy_validation())
except Exception as e:
    print(f"Strategy validation error: {e}")
    print(f"Note: Ensure practice environment is properly configured")
print(f"Strategy validation demonstration complete")
print(f"Remember: Thorough validation prevents costly live trading mistakes")
```

### Phase 3: Production (Live Environment)

Transition to live trading with small positions:

<!-- fragment: Demo production trading with comprehensive safety protocols and conservative risk management -->
```python
import os
from decimal import Decimal
from typing import Dict, Any
from fivetwenty import AsyncClient, Environment


async def demonstrate_production_trading_protocols() -> None:
    """Demonstrate production trading with comprehensive safety protocols and conservative risk management."""
    print(f"⚠️ PRODUCTION TRADING DEMONSTRATION - REAL MONEY AT RISK!")

    # Step 1: Critical pre-production safety checklist
    # Every item must be verified before any live trading
    print(f"\nCurrent environment: MANDATORY PRE-PRODUCTION SAFETY CHECKLIST:")
    safety_checklist = {
        "strategy_validation": "Strategy thoroughly tested in practice environment",
        "error_handling": "Comprehensive error handling implemented and tested",
        "risk_management": "Stop losses, position sizing, and risk limits defined",
        "account_funding": "Account adequately funded for planned trading",
        "market_knowledge": "Understanding of trading hours and market conditions",
        "emergency_procedures": "Emergency stop and position closure procedures ready",
        "regulatory_compliance": "KYC verification and regulatory requirements met",
        "psychological_readiness": "Mental preparation for real money trading stress"
    }

    for item, description in safety_checklist.items():
        print(f"   ☐ {description}")

    print(f"\n⚠️ CRITICAL WARNING: Only proceed if ALL checklist items are complete!")

    # Step 2: Environment variable validation for production safety
    print(f"\nLock Production Environment Validation:")

    # Validate required production environment variables
    required_live_vars = {
        "LIVE_TOKEN": "Live API token - access to real money",
        "LIVE_ACCOUNT": "Live account ID (optional if using default)"
    }

    for var_name, description in required_live_vars.items():
        if var_name in os.environ:
            if "TOKEN" in var_name:
                # Security: Never log full live tokens
                token_value = os.environ[var_name]
                masked_token = f"{token_value[:6]}{'*' * 20}{token_value[-4:]}"
                print(f"   {var_name}: {masked_token} ({description})")
            else:
                print(f"   {var_name}: {os.environ[var_name]} ({description})")
        else:
            print(f"   Error {var_name}: MISSING - {description}")
            print(f"      ⚠️ Cannot proceed without live credentials")
            return

    # Step 3: Initialize production client with maximum safety measures
    print(f"\nHot Initializing LIVE Production Environment...")
    print(f"   ⚠️ Environment: LIVE - Real money trading active")
    print(f"   💸 Risk level: MAXIMUM - Every operation costs real money")
    print(f"   Trading mode: Production (conservative start)")

    async with AsyncClient(
        token=os.environ["LIVE_TOKEN"],                    # Live token - real money access
        environment=Environment.LIVE                       # LIVE environment - maximum risk
    ) as client:

        # Step 4: Mandatory production environment verification
        # Triple-check we're in live environment for safety
        print(f"\nAnalysis: MANDATORY PRODUCTION VERIFICATION:")
        current_env = client.config.environment.value
        print(f"   Environment: {current_env.upper()}")
        print(f"   ⚠️ Risk status: {'LIVE - REAL MONEY' if current_env == 'live' else 'Safe'}")
        print(f"   Account: {client.account_id}")

        if current_env != "live":
            print(f"   Error Environment verification failed - expected live, got {current_env}")
            return

        # Step 5: Comprehensive account analysis for production readiness
        account = await client.accounts.get_account(client.account_id)
        live_balance = Decimal(account.balance)
        available_margin = Decimal(account.margin_available)
        used_margin = Decimal(account.margin_used)

        print(f"\nStarting balance: LIVE ACCOUNT FINANCIAL ANALYSIS:")
        print(f"   Account balance: ${live_balance}")
        print(f"   Available margin: ${available_margin}")
        print(f"   Used margin: ${used_margin}")
        print(f"   Margin utilization: {(used_margin / live_balance * 100):.1f}%")

        # Step 6: Production risk management parameter calculation
        # Conservative risk management for production environment
        print(f"\nSAFETY PRODUCTION RISK MANAGEMENT CALCULATIONS:")

        # Ultra-conservative risk parameters for production start
        max_risk_per_trade = live_balance * Decimal("0.005")  # 0.5% maximum risk per trade
        recommended_position_size = 100  # Micro position for production start
        position_value_estimate = Decimal(str(recommended_position_size)) * Decimal("1.10")  # Approximate EUR/USD value

        print(f"   Account balance: ${live_balance}")
        print(f"   Max risk per trade (0.5%): ${max_risk_per_trade:.2f}")
        print(f"   📉 Recommended start position: {recommended_position_size} units")
        print(f"   Estimated position value: ${position_value_estimate:.2f}")
        print(f"   Security: Risk assessment: Ultra-conservative for production start")

        # Step 7: Production safety threshold verification
        minimum_production_balance = Decimal("2000.00")  # $2000 minimum for production

        print(f"\n🚦 PRODUCTION SAFETY THRESHOLD CHECK:")
        if live_balance < minimum_production_balance:
            print(f"   ⚠️ WARNING: Balance ${live_balance} below production minimum ${minimum_production_balance}")
            print(f"   Stop RECOMMENDATION: Increase account funding or return to practice")
            print(f"   Note Safe production requires adequate capitalization")
            return
        else:
            print(f"   Balance ${live_balance} meets production safety threshold")
            print(f"   Safe to proceed with micro position trading")

        # Step 8: Production order execution with comprehensive risk management
        print(f"\nStarting EXECUTING PRODUCTION ORDER WITH FULL RISK MANAGEMENT...")

        # Calculate conservative stop loss for risk management
        # Stop loss should limit risk to predetermined amount
        stop_loss_distance = Decimal("0.0050")  # 50 pips stop loss
        current_eur_usd_estimate = Decimal("1.1000")  # Approximate current price
        stop_loss_price = current_eur_usd_estimate - stop_loss_distance

        print(f"   Trade Parameters:")
        print(f"      Instrument: EUR_USD (most liquid major pair)")
        print(f"      Position size: {recommended_position_size} units (micro position)")
        print(f"      Stop Stop loss: {stop_loss_price:.4f} (50 pip protection)")
        print(f"      Maximum risk: ~${max_risk_per_trade:.2f}")
        print(f"      Time Order type: Market (immediate execution)")

        try:
            # Execute ultra-conservative production order
            production_order = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument="EUR_USD",                               # Most liquid pair
                units=recommended_position_size,                    # Micro position size
                stop_loss_on_fill={
                    "price": str(stop_loss_price),                 # Risk management stop
                    "time_in_force": "GTC"                         # Good till cancelled
                }
            )

            # Step 9: Production order execution analysis
            fill_transaction = production_order.order_fill_transaction
            fill_price = Decimal(fill_transaction.price)
            actual_units = int(fill_transaction.units)
            immediate_pl = Decimal(fill_transaction.pl)

            print(f"\nSuccess PRODUCTION ORDER EXECUTED SUCCESSFULLY:")
            print(f"   Transaction ID: {fill_transaction.id}")
            print(f"   Fill price: {fill_price:.5f}")
            print(f"   Units filled: {actual_units}")
            print(f"   Immediate P/L: ${immediate_pl}")
            print(f"   Stop Stop loss active: {stop_loss_price:.4f}")
            print(f"   Time Execution time: {fill_transaction.time}")

            # Step 10: Post-execution production monitoring guidance
            print(f"\nMobile PRODUCTION MONITORING REQUIREMENTS:")
            print(f"   👀 Monitor position actively during market hours")
            print(f"   Track P/L and margin usage regularly")
            print(f"   🔔 Set up alerts for significant moves")
            print(f"   📚 Keep detailed records for analysis")
            print(f"   Stop Have emergency closure procedures ready")

            # Risk monitoring calculations
            current_risk = abs(fill_price - stop_loss_price) * Decimal(str(actual_units))
            print(f"\nSAFETY CURRENT RISK EXPOSURE:")
            print(f"   💸 Maximum potential loss: ${current_risk:.2f}")
            print(f"   Risk as % of balance: {(current_risk / live_balance * 100):.2f}%")
            print(f"   Risk assessment: {('ACCEPTABLE' if current_risk / live_balance <= 0.01 else 'REVIEW NEEDED')}")

        except Exception as production_error:
            # Step 11: Production error handling with immediate analysis
            print(f"\nError PRODUCTION ORDER FAILED:")
            print(f"   Analysis: Error type: {type(production_error).__name__}")
            print(f"   Error details: {str(production_error)}")
            print(f"   ⚠️ Impact: No position opened - no financial loss")

            # Production error categorization for immediate response
            if "insufficient" in str(production_error).lower():
                print(f"   Note Error category: Insufficient margin/funds")
                print(f"   Tools Action required: Reduce position size or add funds")
            elif "market closed" in str(production_error).lower():
                print(f"   Note Error category: Market closed")
                print(f"   Tools Action required: Wait for market open or use pending orders")
            else:
                print(f"   Note Error category: Technical/API issue")
                print(f"   Tools Action required: Check connectivity and retry")

        # Step 12: Production trading success metrics and next steps
        print(f"\nAccount type: PRODUCTION TRADING NEXT STEPS:")
        print(f"   Monitor first position closely for learning")
        print(f"   Gradually increase position sizes as confidence builds")
        print(f"   Continue testing strategy with small real money amounts")
        print(f"   📚 Keep detailed trading journal for analysis")
        print(f"   Security: Never exceed risk management parameters")

        print(f"\n⚠️ FINAL PRODUCTION REMINDERS:")
        print(f"   💸 Every trade costs real money - trade responsibly")
        print(f"   Mobile Monitor positions during active market hours")
        print(f"   Stop Use stop losses on every position")
        print(f"   Track performance and adjust strategy accordingly")
        print(f"   Continue learning and improving risk management")


# Production trading demonstration (commented for safety)
print(f"⚠️ PRODUCTION TRADING PROTOCOL DEMONSTRATION")
print(f"⚠️ WARNING: This involves real money trading - use extreme caution")
print(f"\nNote SAFETY NOTE: Production code is commented out by default")
print(f"🔓 Uncomment only when ready for actual live trading with real money")

try:
    # SAFETY: Comment out actual execution for demonstration
    # Uncomment the lines below ONLY when ready for real money trading

    # import asyncio
    # print(f"Executing production trading protocols...")
    # asyncio.run(demonstrate_production_trading_protocols())
    # print(f"Production trading execution complete")

    print(f"Production trading protocols demonstrated (safety mode)")
    print(f"All safety procedures and risk management protocols defined")

except Exception as e:
    print(f"Production trading error: {e}")
    print(f"Note: Review error details and ensure all safety requirements are met")

print(f"Security: REMEMBER: Production = Real money = Real financial responsibility")
print(f"📚 Only proceed when fully prepared and risk-aware")
```

---

## Environment Configuration Patterns

### Environment-Specific Configuration

Use environment variables to manage different environments:

```bash
# .env.practice
FIVETWENTY_OANDA_TOKEN=practice-token-here
FIVETWENTY_OANDA_ACCOUNT=practice-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice

# .env.live
FIVETWENTY_OANDA_TOKEN=live-token-here
FIVETWENTY_OANDA_ACCOUNT=live-account-id
FIVETWENTY_OANDA_ENVIRONMENT=live
```

### Environment Validation

Always validate your environment configuration:

<!-- fragment: Demo comprehensive environment validation with detailed safety protocols -->
```python
from decimal import Decimal
from typing import Dict, Any
from fivetwenty import AsyncClient, Environment


async def demonstrate_comprehensive_environment_validation() -> str:
    """Demonstrate comprehensive environment validation with detailed safety protocols."""
    print(f"Analysis: Comprehensive Environment Validation Demonstration")

    # Step 1: Initialize client with zero-config for environment detection
    # Client automatically detects environment from configuration
    print(f"\nNote: Environment Detection Process:")
    print(f"   Method: Automatic detection from client configuration")
    print(f"   Purpose: Verify intended trading environment")
    print(f"   SAFETY Importance: Critical for financial safety")

    async with AsyncClient() as client:

        # Step 2: Extract and analyze current environment configuration
        current_environment = client.config.environment
        environment_name = current_environment.value

        print(f"\nRisk-free algorithm validationEnvironment Analysis Results:")
        print(f"   Detected environment: {environment_name.upper()}")
        print(f"   Link Environment object: {current_environment}")
        print(f"   Configuration source: Client configuration")

        # Step 3: Environment-specific validation and safety protocols
        if current_environment == Environment.LIVE:
            # LIVE ENVIRONMENT - Maximum safety protocols required
            print(f"\n⚠️ LIVE ENVIRONMENT DETECTED - IMPLEMENTING MAXIMUM SAFETY PROTOCOLS")

            # Step 4: Comprehensive live environment safety analysis
            print(f"\n⚠️ LIVE ENVIRONMENT SAFETY ANALYSIS:")
            print(f"   💸 Financial risk: MAXIMUM - Real money at risk")
            print(f"   Trading impact: Every operation costs real money")
            print(f"   Requirements: All testing must be complete")
            print(f"   Security: Risk management: Mandatory for all positions")
            print(f"   📚 Experience level: Should be confident and prepared")

            # Step 5: Mandatory live environment readiness checklist
            print(f"\nCurrent environment: MANDATORY LIVE ENVIRONMENT READINESS CHECKLIST:")
            live_readiness_items = [
                "Strategy tested extensively in practice environment",
                "Risk management rules implemented and validated",
                "Stop loss and position sizing procedures defined",
                "Error handling tested for all failure scenarios",
                "Account adequately funded for planned trading",
                "Market hours and trading session knowledge confirmed",
                "Emergency position closure procedures established",
                "Trading psychology and emotional control prepared"
            ]

            for i, item in enumerate(live_readiness_items, 1):
                print(f"   {i}. ☐ {item}")

            print(f"\n⚠️ CRITICAL: All checklist items must be complete before live trading!")

            # Step 6: Live account financial safety analysis
            print(f"\nStarting balance: LIVE ACCOUNT FINANCIAL SAFETY ANALYSIS:")

            try:
                account = await client.accounts.get_account(client.account_id)
                live_balance = Decimal(account.balance)
                available_margin = Decimal(account.margin_available)
                margin_rate = Decimal(account.margin_rate)

                print(f"   Account ID: {account.id}")
                print(f"   Current balance: ${live_balance}")
                print(f"   Available margin: ${available_margin}")
                print(f"   Margin rate: {margin_rate}")
                print(f"   Account currency: {account.currency}")

                # Step 7: Live account balance safety threshold analysis
                # Define safety thresholds for responsible live trading
                minimum_safe_balance = Decimal("1000.00")    # $1000 minimum
                recommended_balance = Decimal("5000.00")     # $5000 recommended
                conservative_balance = Decimal("10000.00")   # $10000 conservative

                print(f"\n🚦 BALANCE SAFETY THRESHOLD ANALYSIS:")
                print(f"   Current balance: ${live_balance}")
                print(f"   Red Minimum safe: ${minimum_safe_balance}")
                print(f"   Yellow Recommended: ${recommended_balance}")
                print(f"   Green Conservative: ${conservative_balance}")

                # Determine balance safety category
                if live_balance < minimum_safe_balance:
                    print(f"   ⚠️ DANGER: Balance below minimum safe threshold")
                    print(f"   Note Action required: Increase funding or return to practice")
                    print(f"   ⚠️ Risk level: EXTREMELY HIGH - Consider practice environment")
                    balance_safety = "DANGEROUS"
                elif live_balance < recommended_balance:
                    print(f"   ⚠️ CAUTION: Balance below recommended threshold")
                    print(f"   Note Recommendation: Use micro positions and strict risk management")
                    print(f"   Risk level: HIGH - Extra caution required")
                    balance_safety = "CAUTION"
                elif live_balance < conservative_balance:
                    print(f"   Yellow MODERATE: Balance meets basic requirements")
                    print(f"   Note Recommendation: Conservative position sizing")
                    print(f"   Risk level: MODERATE - Standard risk management")
                    balance_safety = "MODERATE"
                else:
                    print(f"   Green EXCELLENT: Balance supports conservative trading")
                    print(f"   Note Status: Well-capitalized for responsible trading")
                    print(f"   Risk level: MANAGEABLE - Good safety margin")
                    balance_safety = "EXCELLENT"

                # Step 8: Position sizing recommendations for live environment
                print(f"\nRisk-free algorithm validationLIVE ENVIRONMENT POSITION SIZING RECOMMENDATIONS:")
                max_risk_per_trade = live_balance * Decimal("0.01")  # 1% max risk
                conservative_risk = live_balance * Decimal("0.005")  # 0.5% conservative

                print(f"   Account balance: ${live_balance}")
                print(f"   📉 Maximum risk per trade (1%): ${max_risk_per_trade:.2f}")
                print(f"   Security: Conservative risk (0.5%): ${conservative_risk:.2f}")
                print(f"   Recommended start: Use conservative risk or lower")
                print(f"   Ruler Position size: Calculate based on stop loss distance")

            except Exception as account_error:
                print(f"   Error Account analysis failed: {account_error}")
                print(f"   Analysis: Error type: {type(account_error).__name__}")
                print(f"   Note Possible causes: Network issues, authentication, or API limits")
                balance_safety = "UNKNOWN"

            print(f"\nAccount type: LIVE ENVIRONMENT VALIDATION RESULT: {balance_safety}")

        else:
            # PRACTICE ENVIRONMENT - Safe for all experimentation
            print(f"\nSuccess PRACTICE ENVIRONMENT DETECTED - SAFE FOR ALL EXPERIMENTATION")

            # Step 9: Practice environment benefits and capabilities
            print(f"\nTesting: PRACTICE ENVIRONMENT BENEFITS:")
            print(f"   Financial risk: ZERO - Virtual money only")
            print(f"   Experimentation: Safe to test any strategy")
            print(f"   Learning: Perfect for skill development")
            print(f"   Position sizes: Can test with any size safely")
            print(f"   Processing Mistakes: Learning opportunities without cost")
            print(f"   Real data: Actual market conditions with virtual execution")

            # Step 10: Practice environment account analysis
            print(f"\nStarting balance: PRACTICE ACCOUNT ANALYSIS:")

            try:
                account = await client.accounts.get_account(client.account_id)
                practice_balance = Decimal(account.balance)

                print(f"   Account ID: {account.id}")
                print(f"   Virtual balance: ${practice_balance}")
                print(f"   Starting balance: Typically $100,000 virtual")
                print(f"   Reset capability: Can be reset if needed")
                print(f"   Account currency: {account.currency}")

                # Practice environment usage recommendations
                print(f"\nPerfect for learning: PRACTICE ENVIRONMENT USAGE RECOMMENDATIONS:")
                print(f"   Test strategies extensively before live trading")
                print(f"   Experiment with different position sizes")
                print(f"   Testing: Practice risk management techniques")
                print(f"   Validate error handling and edge cases")
                print(f"   📚 Learn market behavior and trading patterns")

            except Exception as practice_error:
                print(f"   Error Practice account analysis failed: {practice_error}")
                print(f"   Note This is normal - continue with practice environment")

            print(f"\nAccount type: PRACTICE ENVIRONMENT VALIDATION RESULT: SAFE")

        # Step 11: Environment validation summary and recommendations
        print(f"\nCurrent environment: ENVIRONMENT VALIDATION SUMMARY:")
        print(f"   Environment: {environment_name.upper()}")
        print(f"   Safety level: {'MAXIMUM RISK' if environment_name == 'live' else 'SAFE'}")
        print(f"   Note Recommendation: {'Proceed with extreme caution' if environment_name == 'live' else 'Safe to experiment'}")

        # Next steps guidance based on environment
        if environment_name == "live":
            print(f"\n⚠️ LIVE ENVIRONMENT NEXT STEPS:")
            print(f"   Verify all safety checklist items are complete")
            print(f"   Start with micro positions and conservative risk")
            print(f"   👀 Monitor all positions actively")
            print(f"   Stop Have emergency stop procedures ready")
        else:
            print(f"\nTesting: PRACTICE ENVIRONMENT NEXT STEPS:")
            print(f"   Experiment freely with different strategies")
            print(f"   Test with various position sizes")
            print(f"   Build confidence before live trading")
            print(f"   📚 Learn from mistakes without financial cost")

        return environment_name


# Environment validation execution
print(f"Analysis: Starting Comprehensive Environment Validation")
try:
    import asyncio
    detected_env = asyncio.run(demonstrate_comprehensive_environment_validation())
    print(f"\nSuccess Environment validation complete")
    print(f"Detected environment: {detected_env.upper()}")
    print(f"Note: Proceed according to environment-specific safety protocols")
except Exception as e:
    print(f"Environment validation error: {e}")
    print(f"Note: Check client configuration and credentials")
print(f"Security: Remember: Environment validation is critical for trading safety")
```

---

## Safety Considerations

### Pre-Live Checklist

Before transitioning to live trading:

- [ ] Strategy tested extensively in practice environment
- [ ] Error handling implemented for all scenarios
- [ ] Risk management rules defined and coded
- [ ] Position sizing appropriate for account balance
- [ ] Stop losses and take profits configured
- [ ] Maximum daily/weekly loss limits set
- [ ] Emergency stop procedures defined

### Environment Isolation

Keep environments completely separate:

<!-- fragment: Demo comprehensive trading environment management with safety protocols -->
```python
from decimal import Decimal
from typing import Dict, Any, Optional
from fivetwenty import AsyncClient, Environment


class ComprehensiveTradingEnvironment:
    """Environment-specific trading configuration with comprehensive safety protocols."""

    def __init__(self, env_type: str, account_balance: Optional[Decimal] = None) -> None:
        """Initialize trading environment with safety-first configuration."""
        # Step 1: Store environment type and validate input
        # Environment type determines all safety and risk parameters
        self.env_type = env_type.lower()
        self.account_balance = account_balance

        print(f"Initializing Trading Environment: {self.env_type.upper()}")

        # Step 2: Configure environment-specific parameters
        # Different environments require dramatically different risk parameters
        if self.env_type == "practice":
            # Practice environment - safe for aggressive experimentation
            print(f"\nTesting: Practice Environment Configuration:")

            self.max_position_size = 100000                    # Large positions safe for testing
            self.risk_checks_enabled = False                   # Allow aggressive testing
            self.position_size_limit_percentage = Decimal("0.50")  # 50% of balance allowed
            self.mandatory_stop_loss = False                   # Optional for testing
            self.max_daily_trades = 100                        # High limit for testing
            self.risk_per_trade_limit = Decimal("0.10")        # 10% virtual risk allowed

            print(f"   Max position size: {self.max_position_size:,} units")
            print(f"   Risk checks: {'Enabled' if self.risk_checks_enabled else 'Disabled (safe for testing)'}")
            print(f"   Position limit: {self.position_size_limit_percentage*100}% of balance")
            print(f"   Stop Mandatory stop loss: {'Yes' if self.mandatory_stop_loss else 'No (testing mode)'}")
            print(f"   Daily trade limit: {self.max_daily_trades}")
            print(f"   SAFETY Risk per trade: {self.risk_per_trade_limit*100}% (virtual)")

        elif self.env_type == "live":
            # Live environment - maximum safety and conservative parameters
            print(f"\n⚠️ Live Environment Configuration (CONSERVATIVE):")

            self.max_position_size = 1000                      # Very conservative sizing
            self.risk_checks_enabled = True                    # Strict risk management
            self.position_size_limit_percentage = Decimal("0.02")  # 2% of balance maximum
            self.mandatory_stop_loss = True                    # Required for all positions
            self.max_daily_trades = 10                         # Conservative daily limit
            self.risk_per_trade_limit = Decimal("0.01")        # 1% real money risk maximum

            print(f"   Max position size: {self.max_position_size:,} units")
            print(f"   Risk checks: {'Enabled' if self.risk_checks_enabled else 'Disabled'}")
            print(f"   Position limit: {self.position_size_limit_percentage*100}% of balance")
            print(f"   Stop Mandatory stop loss: {'Yes' if self.mandatory_stop_loss else 'No'}")
            print(f"   Daily trade limit: {self.max_daily_trades}")
            print(f"   SAFETY Risk per trade: {self.risk_per_trade_limit*100}% (REAL MONEY)")

        else:
            # Invalid environment type - fail safely
            raise ValueError(f"Invalid environment type: {env_type}. Must be 'practice' or 'live'")

        # Step 3: Initialize tracking and safety monitoring
        # Comprehensive tracking helps maintain safety discipline
        self.daily_trade_count = 0
        self.total_risk_exposure = Decimal("0.00")
        self.open_positions: Dict[str, Dict[str, Any]] = {}
        self.safety_violations: list[str] = []

        print(f"\nCurrent environment: Safety Monitoring Initialized:")
        print(f"   Daily trade tracking: 0/{self.max_daily_trades}")
        print(f"   Risk exposure tracking: $0.00")
        print(f"   Position monitoring: Active")
        print(f"   ⚠️ Safety violation alerts: Enabled")

    async def create_client(self) -> AsyncClient:
        """Create environment-appropriate client with safety verification."""
        # Step 4: Create client with proper environment configuration
        # Client environment must match trading environment configuration
        print(f"\nNote: Creating {self.env_type.upper()} Environment Client...")

        if self.env_type == "practice":
            target_environment = Environment.PRACTICE
            print(f"   Testing: Target: Practice environment (safe for testing)")
        elif self.env_type == "live":
            target_environment = Environment.LIVE
            print(f"   ⚠️ Target: Live environment (REAL MONEY RISK)")
        else:
            raise ValueError(f"Cannot create client for unknown environment: {self.env_type}")

        # Create client with explicit environment specification
        client = AsyncClient(environment=target_environment)

        # Step 5: Verify client environment matches configuration
        print(f"   Client created for {target_environment.value} environment")
        print(f"   Analysis: Environment verification: {client.config.environment.value}")

        if client.config.environment != target_environment:
            error_msg = f"Environment mismatch: expected {target_environment.value}, got {client.config.environment.value}"
            print(f"   Error {error_msg}")
            raise ValueError(error_msg)

        return client

    def validate_position_size(self, units: int, instrument: str) -> bool:
        """Validate position size against environment safety parameters."""
        # Step 6: Comprehensive position size validation
        print(f"\nSAFETY Position Size Validation for {instrument}:")
        print(f"   Requested units: {units:,}")
        print(f"   Environment: {self.env_type.upper()}")

        # Check against maximum position size
        if abs(units) > self.max_position_size:
            violation = f"Position size {abs(units):,} exceeds maximum {self.max_position_size:,}"
            print(f"   Error {violation}")
            self.safety_violations.append(violation)
            return False

        # Check against account balance percentage (if available)
        if self.account_balance:
            position_value_estimate = Decimal(str(abs(units))) * Decimal("1.10")  # Rough estimate
            position_percentage = position_value_estimate / self.account_balance

            if position_percentage > self.position_size_limit_percentage:
                violation = f"Position {position_percentage*100:.1f}% of balance exceeds limit {self.position_size_limit_percentage*100:.1f}%"
                print(f"   Error {violation}")
                self.safety_violations.append(violation)
                return False

        # Check daily trade limit
        if self.daily_trade_count >= self.max_daily_trades:
            violation = f"Daily trade limit {self.max_daily_trades} exceeded"
            print(f"   Error {violation}")
            self.safety_violations.append(violation)
            return False

        print(f"   Position size validation passed")
        print(f"   Units: {units:,} (within {self.max_position_size:,} limit)")
        print(f"   Daily trades: {self.daily_trade_count}/{self.max_daily_trades}")

        return True

    def requires_stop_loss(self) -> bool:
        """Check if stop loss is required for this environment."""
        # Step 7: Stop loss requirement based on environment
        if self.mandatory_stop_loss:
            print(f"   Stop Stop loss REQUIRED for {self.env_type.upper()} environment")
            return True
        else:
            print(f"   Processing Stop loss optional for {self.env_type.upper()} environment")
            return False

    def get_safety_summary(self) -> Dict[str, Any]:
        """Get comprehensive safety configuration summary."""
        # Step 8: Generate comprehensive safety summary
        return {
            "environment_type": self.env_type,
            "max_position_size": self.max_position_size,
            "risk_checks_enabled": self.risk_checks_enabled,
            "position_size_limit_percentage": self.position_size_limit_percentage,
            "mandatory_stop_loss": self.mandatory_stop_loss,
            "max_daily_trades": self.max_daily_trades,
            "risk_per_trade_limit": self.risk_per_trade_limit,
            "daily_trade_count": self.daily_trade_count,
            "total_risk_exposure": self.total_risk_exposure,
            "safety_violations": self.safety_violations,
            "financial_risk_level": "ZERO" if self.env_type == "practice" else "MAXIMUM"
        }


# Demonstration of comprehensive trading environment management
print(f"Comprehensive Trading Environment Management Demo")

# Practice environment example
print(f"\nTesting: PRACTICE ENVIRONMENT EXAMPLE:")
practice_env = ComprehensiveTradingEnvironment("practice", Decimal("100000.00"))
print(f"Practice environment validation for 5000 units:")
practice_valid = practice_env.validate_position_size(5000, "EUR_USD")
print(f"Stop loss required: {practice_env.requires_stop_loss()}")

# Live environment example
print(f"\n⚠️ LIVE ENVIRONMENT EXAMPLE:")
live_env = ComprehensiveTradingEnvironment("live", Decimal("5000.00"))
print(f"Live environment validation for 500 units:")
live_valid = live_env.validate_position_size(500, "EUR_USD")
print(f"Stop loss required: {live_env.requires_stop_loss()}")

print(f"\nRisk-free algorithm validationSafety Summary Comparison:")
print(f"Practice safety: {practice_env.get_safety_summary()['financial_risk_level']}")
print(f"Live safety: {live_env.get_safety_summary()['financial_risk_level']}")
print(f"Environment management demonstration complete")
```

### Monitoring and Alerts

Implement environment-specific monitoring:

<!-- fragment: Demo comprehensive environment monitoring with detailed alerting systems -->
```python
import time
from decimal import Decimal
from typing import Dict, List, Any, Optional
from fivetwenty import AsyncClient, Environment


class ComprehensiveEnvironmentMonitor:
    """Comprehensive environment monitoring with detailed alerting systems."""

    def __init__(self, alert_thresholds: Optional[Dict[str, Decimal]] = None) -> None:
        """Initialize environment monitor with customizable alert thresholds."""
        # Step 1: Initialize monitoring system with environment-specific thresholds
        print(f"Initializing Comprehensive Environment Monitoring System")

        # Default alert thresholds - can be customized per environment
        self.alert_thresholds = alert_thresholds or {
            "live_loss_warning": Decimal("500.00"),        # $500 loss warning for live
            "live_loss_critical": Decimal("1000.00"),      # $1000 loss critical for live
            "live_margin_warning": Decimal("0.80"),        # 80% margin utilization warning
            "practice_loss_info": Decimal("5000.00"),      # $5000 virtual loss info threshold
            "position_count_warning": 10,                   # 10+ open positions warning
            "daily_trade_warning": 50                       # 50+ daily trades warning
        }

        # Step 2: Initialize monitoring state and history tracking
        self.monitoring_history: List[Dict[str, Any]] = []
        self.alert_count = 0
        self.last_check_time = time.time()
        self.monitoring_active = False

        print(f"Monitoring system initialized with environment-specific thresholds")
        print(f"Alert thresholds configured for comprehensive safety monitoring")

    async def perform_comprehensive_environment_monitoring(self) -> Dict[str, Any]:
        """Perform comprehensive environment monitoring with detailed analysis."""
        print(f"\nRisk-free algorithm validationStarting Comprehensive Environment Monitoring...")

        self.monitoring_active = True
        current_time = time.time()

        async with AsyncClient() as client:

            # Step 3: Determine environment and configure monitoring intensity
            current_environment = client.config.environment
            environment_name = current_environment.value

            print(f"\nAnalysis: Environment Detection and Configuration:")
            print(f"   Environment: {environment_name.upper()}")
            print(f"   ⚠️ Risk level: {'MAXIMUM' if environment_name == 'live' else 'ZERO'}")
            print(f"   Monitoring intensity: {'HIGH' if environment_name == 'live' else 'STANDARD'}")
            print(f"   Time Monitoring timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")

            # Step 4: Retrieve comprehensive account information
            try:
                account = await client.accounts.get_account(client.account_id)

                # Extract critical account metrics for monitoring
                account_balance = Decimal(account.balance)
                unrealized_pl = Decimal(account.unrealized_pl)
                margin_used = Decimal(account.margin_used)
                margin_available = Decimal(account.margin_available)
                total_margin = margin_used + margin_available
                margin_utilization = (margin_used / total_margin) if total_margin > 0 else Decimal("0")

                print(f"\nStarting balance: Account Financial Status:")
                print(f"   Account ID: {account.id}")
                print(f"   Balance: ${account_balance}")
                print(f"   Unrealized P/L: ${unrealized_pl}")
                print(f"   Margin used: ${margin_used}")
                print(f"   Margin available: ${margin_available}")
                print(f"   SAFETY Margin utilization: {margin_utilization*100:.1f}%")

            except Exception as account_error:
                print(f"   Error Account data retrieval failed: {account_error}")
                return {"status": "error", "message": str(account_error)}

            # Step 5: Environment-specific monitoring and alerting
            monitoring_results = {
                "environment": environment_name,
                "timestamp": current_time,
                "account_balance": account_balance,
                "unrealized_pl": unrealized_pl,
                "margin_utilization": margin_utilization,
                "alerts": [],
                "status": "normal"
            }

            if current_environment == Environment.LIVE:
                # LIVE ENVIRONMENT - Critical monitoring with immediate alerts
                print(f"\n⚠️ LIVE ENVIRONMENT CRITICAL MONITORING:")

                # Step 6: Live environment loss monitoring
                if unrealized_pl <= -self.alert_thresholds["live_loss_critical"]:
                    critical_alert = f"CRITICAL LOSS: ${abs(unrealized_pl)} unrealized loss"
                    print(f"   Red {critical_alert}")
                    print(f"   ⚠️ IMMEDIATE ACTION REQUIRED:")
                    print(f"      1. Review all open positions immediately")
                    print(f"      2. Consider closing losing positions")
                    print(f"      3. Implement emergency stop procedures")
                    print(f"      4. Contact support if needed")

                    monitoring_results["alerts"].append({
                        "level": "CRITICAL",
                        "message": critical_alert,
                        "action_required": "IMMEDIATE",
                        "timestamp": current_time
                    })
                    monitoring_results["status"] = "critical"

                elif unrealized_pl <= -self.alert_thresholds["live_loss_warning"]:
                    warning_alert = f"WARNING: ${abs(unrealized_pl)} unrealized loss"
                    print(f"   🟠 {warning_alert}")
                    print(f"   ⚠️ RECOMMENDED ACTIONS:")
                    print(f"      1. Review position management strategy")
                    print(f"      2. Consider tightening stop losses")
                    print(f"      3. Monitor more frequently")
                    print(f"      4. Prepare exit strategy if losses increase")

                    monitoring_results["alerts"].append({
                        "level": "WARNING",
                        "message": warning_alert,
                        "action_required": "REVIEW",
                        "timestamp": current_time
                    })
                    monitoring_results["status"] = "warning"

                else:
                    print(f"   P/L Status: Within acceptable range (${unrealized_pl})")

                # Step 7: Live environment margin monitoring
                if margin_utilization >= self.alert_thresholds["live_margin_warning"]:
                    margin_alert = f"HIGH MARGIN USAGE: {margin_utilization*100:.1f}% utilized"
                    print(f"   🟠 {margin_alert}")
                    print(f"   Note MARGIN MANAGEMENT ACTIONS:")
                    print(f"      1. Consider reducing position sizes")
                    print(f"      2. Close non-essential positions")
                    print(f"      3. Add funds if planning continued trading")
                    print(f"      4. Monitor for margin calls")

                    monitoring_results["alerts"].append({
                        "level": "WARNING",
                        "message": margin_alert,
                        "action_required": "MARGIN_MANAGEMENT",
                        "timestamp": current_time
                    })

                else:
                    print(f"   Margin Status: Healthy utilization ({margin_utilization*100:.1f}%)")

                # Step 8: Live environment safety recommendations
                print(f"\nSecurity: LIVE ENVIRONMENT SAFETY REMINDERS:")
                print(f"   💸 Every position involves real money risk")
                print(f"   Mobile Monitor during active trading hours")
                print(f"   Stop Have stop losses on all positions")
                print(f"   Keep detailed records for analysis")
                print(f"   Continue education and risk management")

            else:
                # PRACTICE ENVIRONMENT - Relaxed monitoring for learning
                print(f"\nTesting: PRACTICE ENVIRONMENT EDUCATIONAL MONITORING:")

                # Step 9: Practice environment learning-focused monitoring
                if unrealized_pl <= -self.alert_thresholds["practice_loss_info"]:
                    learning_alert = f"LEARNING OPPORTUNITY: ${abs(unrealized_pl)} virtual loss"
                    print(f"   📚 {learning_alert}")
                    print(f"   Note LEARNING ANALYSIS:")
                    print(f"      1. Analyze what led to virtual losses")
                    print(f"      2. Review position sizing strategy")
                    print(f"      3. Test improved risk management")
                    print(f"      4. Practice makes perfect - keep learning!")

                    monitoring_results["alerts"].append({
                        "level": "LEARNING",
                        "message": learning_alert,
                        "action_required": "ANALYZE",
                        "timestamp": current_time
                    })

                else:
                    print(f"   Virtual P/L: ${unrealized_pl} (no real money impact)")

                print(f"\nPerfect for learning: PRACTICE ENVIRONMENT BENEFITS:")
                print(f"   Safe experimentation with any strategy")
                print(f"   Learn from mistakes without financial cost")
                print(f"   Testing: Test risk management techniques")
                print(f"   Virtual losses provide valuable learning")
                print(f"   📚 Build confidence before live trading")

            # Step 10: Record monitoring session for historical analysis
            self.monitoring_history.append(monitoring_results)
            self.alert_count += len(monitoring_results["alerts"])

            # Final monitoring summary
            print(f"\nRisk-free algorithm validationMONITORING SESSION SUMMARY:")
            print(f"   Environment: {environment_name.upper()}")
            print(f"   Account balance: ${account_balance}")
            print(f"   Unrealized P/L: ${unrealized_pl}")
            print(f"   ⚠️ Alerts generated: {len(monitoring_results['alerts'])}")
            print(f"   Overall status: {monitoring_results['status'].upper()}")
            print(f"   Time Monitoring duration: {time.time() - current_time:.2f} seconds")

            return monitoring_results

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring history summary."""
        # Step 11: Generate comprehensive monitoring summary
        return {
            "total_sessions": len(self.monitoring_history),
            "total_alerts": self.alert_count,
            "monitoring_active": self.monitoring_active,
            "last_check": self.last_check_time,
            "alert_thresholds": self.alert_thresholds
        }


# Comprehensive environment monitoring demonstration
async def demonstrate_environment_monitoring() -> None:
    """Demonstrate comprehensive environment monitoring system."""
    print(f"Environment Monitoring System Demonstration")

    # Initialize monitoring system
    monitor = ComprehensiveEnvironmentMonitor()

    # Perform monitoring
    results = await monitor.perform_comprehensive_environment_monitoring()

    # Display results
    print(f"\nCurrent environment: Monitoring Results Summary:")
    print(f"   Status: {results['status']}")
    print(f"   ⚠️ Alerts: {len(results['alerts'])}")
    print(f"   Summary: {monitor.get_monitoring_summary()}")


# Environment monitoring execution
print(f"Starting Environment Monitoring Demonstration")
try:
    import asyncio
    asyncio.run(demonstrate_environment_monitoring())
except Exception as e:
    print(f"Monitoring system error: {e}")
    print(f"Note: Check client configuration and network connectivity")
print(f"Environment monitoring demonstration complete")
print(f"Remember: Active monitoring prevents costly trading mistakes")
```

---

## Common Environment Issues

### Token Mismatch

**Problem**: Using practice token with live environment or vice versa.

**Solution**: Validate token/environment combinations:

<!-- fragment: Demo comprehensive token and environment validation with detailed error analysis -->
```python
import os
from typing import Dict, Any, Optional
from fivetwenty import AsyncClient, Environment


async def demonstrate_comprehensive_token_environment_validation() -> Dict[str, Any]:
    """Demonstrate comprehensive token and environment validation with detailed error analysis."""
    print(f"Lock Comprehensive Token and Environment Validation Demonstration")

    # Step 1: Environment variable detection and validation
    print(f"\nAnalysis: Environment Variable Detection:")

    # Check for environment variables that indicate intended environment
    env_indicators = {
        "PRACTICE_TOKEN": "Practice environment token",
        "LIVE_TOKEN": "Live environment token",
        "OANDA_TOKEN": "Generic token (environment ambiguous)",
        "FIVETWENTY_OANDA_TOKEN": "FiveTwenty-specific token",
        "FIVETWENTY_OANDA_ENVIRONMENT": "Explicit environment specification"
    }

    detected_vars = {}
    for var_name, description in env_indicators.items():
        if var_name in os.environ:
            value = os.environ[var_name]
            # Mask sensitive token values for security
            if "TOKEN" in var_name and value:
                masked_value = f"{value[:6]}{'*' * 20}{value[-4:]}"
                detected_vars[var_name] = masked_value
                print(f"   {var_name}: {masked_value} ({description})")
            else:
                detected_vars[var_name] = value
                print(f"   {var_name}: {value} ({description})")
        else:
            print(f"   Error {var_name}: Not found ({description})")

    # Step 2: Determine intended environment from available indicators
    intended_environment = None
    if "FIVETWENTY_OANDA_ENVIRONMENT" in detected_vars:
        intended_environment = detected_vars["FIVETWENTY_OANDA_ENVIRONMENT"].lower()
        print(f"\nAccount type: Intended environment detected: {intended_environment.upper()}")
    elif "PRACTICE_TOKEN" in detected_vars:
        intended_environment = "practice"
        print(f"\nAccount type: Practice token detected - intended environment: PRACTICE")
    elif "LIVE_TOKEN" in detected_vars:
        intended_environment = "live"
        print(f"\nAccount type: Live token detected - intended environment: LIVE")
    else:
        print(f"\n⚠️ Cannot determine intended environment from variables")
        print(f"Note: Consider using explicit environment variables")

    # Step 3: Initialize client for validation testing
    print(f"\nNote: Client Initialization for Token Validation...")

    validation_results = {
        "token_valid": False,
        "environment_match": False,
        "detected_environment": None,
        "intended_environment": intended_environment,
        "error_details": None,
        "account_access": False,
        "validation_timestamp": None
    }

    try:
        # Step 4: Create client and attempt token validation
        async with AsyncClient() as client:
            validation_start_time = time.time()

            # Extract actual environment from client configuration
            actual_environment = client.config.environment.value
            validation_results["detected_environment"] = actual_environment
            validation_results["validation_timestamp"] = validation_start_time

            print(f"   Client configuration:")
            print(f"      Detected environment: {actual_environment.upper()}")
            print(f"      Intended environment: {intended_environment.upper() if intended_environment else 'UNKNOWN'}")
            print(f"      Link Client initialized successfully")

            # Step 5: Attempt to retrieve accounts for token validation
            print(f"\nLock Token Authentication Validation:")

            try:
                accounts = await client.accounts.get_accounts()
                validation_results["token_valid"] = True
                validation_results["account_access"] = True

                print(f"   Token authentication: SUCCESSFUL")
                print(f"   Account access: GRANTED")
                print(f"   Accounts found: {len(accounts)}")

                if accounts:
                    primary_account = accounts[0]
                    print(f"   Primary account balance: ${primary_account.balance}")
                    print(f"   Account currency: {primary_account.currency}")
                    print(f"   Account alias: {primary_account.alias or 'N/A'}")

            except Exception as auth_error:
                validation_results["token_valid"] = False
                validation_results["error_details"] = str(auth_error)

                print(f"   Error Token authentication: FAILED")
                print(f"   Analysis: Error type: {type(auth_error).__name__}")
                print(f"   Error message: {str(auth_error)}")

                # Step 6: Detailed error analysis for troubleshooting
                print(f"\nAnalysis: Token Validation Error Analysis:")

                if "401" in str(auth_error) or "Unauthorized" in str(auth_error):
                    print(f"   Error Category: AUTHENTICATION FAILURE")
                    print(f"   Note Likely causes:")
                    print(f"      1. Invalid or expired token")
                    print(f"      2. Token/environment mismatch")
                    print(f"      3. Token not authorized for this environment")
                    print(f"   Tools Troubleshooting steps:")
                    print(f"      1. Verify token is correct and active")
                    print(f"      2. Check practice tokens use PRACTICE environment")
                    print(f"      3. Check live tokens use LIVE environment")
                    print(f"      4. Regenerate token if expired")

                elif "403" in str(auth_error) or "Forbidden" in str(auth_error):
                    print(f"   Error Category: AUTHORIZATION FAILURE")
                    print(f"   Note Likely causes:")
                    print(f"      1. Token valid but lacks required permissions")
                    print(f"      2. Account access restrictions")
                    print(f"      3. Regional or regulatory restrictions")
                    print(f"   Tools Troubleshooting steps:")
                    print(f"      1. Check token permissions in OANDA portal")
                    print(f"      2. Verify account is active and accessible")
                    print(f"      3. Contact OANDA support for access issues")

                elif "network" in str(auth_error).lower() or "connection" in str(auth_error).lower():
                    print(f"   Error Category: NETWORK/CONNECTIVITY")
                    print(f"   Note Likely causes:")
                    print(f"      1. Internet connectivity issues")
                    print(f"      2. OANDA API server issues")
                    print(f"      3. Firewall or proxy blocking requests")
                    print(f"   Tools Troubleshooting steps:")
                    print(f"      1. Check internet connection")
                    print(f"      2. Try again in a few minutes")
                    print(f"      3. Check OANDA API status")

                else:
                    print(f"   Error Category: UNKNOWN/OTHER")
                    print(f"   Note General troubleshooting:")
                    print(f"      1. Check error message for specific details")
                    print(f"      2. Verify all configuration is correct")
                    print(f"      3. Contact support if issue persists")

            # Step 7: Environment matching validation
            print(f"\nProcessing Environment Matching Validation:")

            if intended_environment and actual_environment:
                if actual_environment.lower() == intended_environment.lower():
                    validation_results["environment_match"] = True
                    print(f"   Environment match: SUCCESSFUL")
                    print(f"   Intended: {intended_environment.upper()}")
                    print(f"   Actual: {actual_environment.upper()}")
                    print(f"   Configuration: CORRECT")
                else:
                    validation_results["environment_match"] = False
                    print(f"   Error Environment mismatch: DETECTED")
                    print(f"   Intended: {intended_environment.upper()}")
                    print(f"   Actual: {actual_environment.upper()}")
                    print(f"   ⚠️ Configuration: INCORRECT")

                    print(f"\nTools Environment Mismatch Resolution:")
                    if intended_environment == "practice" and actual_environment == "live":
                        print(f"   ⚠️ CRITICAL: Using LIVE environment with practice intent!")
                        print(f"   💸 DANGER: Real money at risk!")
                        print(f"   Stop ACTION: Switch to practice token immediately")
                    elif intended_environment == "live" and actual_environment == "practice":
                        print(f"   ⚠️ Using practice environment with live intent")
                        print(f"   Note ACTION: Switch to live token for real trading")
                        print(f"   Testing: NOTE: No real trading possible in practice")
            else:
                print(f"   ⚠️ Environment matching: Cannot determine (insufficient information)")
                print(f"   Note Recommendation: Use explicit environment configuration")

    except Exception as client_error:
        validation_results["error_details"] = str(client_error)
        print(f"\nError Client initialization failed: {client_error}")
        print(f"Analysis: Error type: {type(client_error).__name__}")
        print(f"Note: Check environment variables and token configuration")

    # Step 8: Final validation summary and recommendations
    print(f"\nRisk-free algorithm validationTOKEN AND ENVIRONMENT VALIDATION SUMMARY:")
    print(f"   Lock Token valid: {'Success YES' if validation_results['token_valid'] else 'Error NO'}")
    print(f"   Account access: {'Success YES' if validation_results['account_access'] else 'Error NO'}")
    print(f"   Processing Environment match: {'Success YES' if validation_results['environment_match'] else 'Error NO'}")
    print(f"   Detected environment: {validation_results['detected_environment'] or 'UNKNOWN'}")

    # Overall validation status
    if validation_results["token_valid"] and validation_results["environment_match"]:
        overall_status = "SUCCESS"
        status_emoji = "Success"
        print(f"\n{status_emoji} OVERALL VALIDATION: {overall_status}")
        print(f"Configuration is correct and ready for trading")
    elif validation_results["token_valid"] and not validation_results["environment_match"]:
        overall_status = "PARTIAL"
        status_emoji = "⚠️"
        print(f"\n{status_emoji} OVERALL VALIDATION: {overall_status}")
        print(f"Token works but environment configuration needs attention")
    else:
        overall_status = "FAILURE"
        status_emoji = "Error"
        print(f"\n{status_emoji} OVERALL VALIDATION: {overall_status}")
        print(f"Token and/or environment configuration requires fixing")

    validation_results["overall_status"] = overall_status
    return validation_results


# Token and environment validation execution
print(f"Lock Starting Comprehensive Token and Environment Validation")
try:
    import asyncio
    import time

    results = asyncio.run(demonstrate_comprehensive_token_environment_validation())

    print(f"\nCurrent environment: Final Validation Results:")
    print(f"   Overall status: {results['overall_status']}")
    print(f"   Lock Token validation: {'Passed' if results['token_valid'] else 'Failed'}")
    print(f"   Processing Environment match: {'Correct' if results['environment_match'] else 'Mismatch'}")

except Exception as e:
    print(f"Validation system error: {e}")
    print(f"Note: Check environment setup and try again")

print(f"Token and environment validation demonstration complete")
print(f"Remember: Proper validation prevents costly configuration mistakes")
```

### Account Access Issues

**Problem**: Token doesn't have access to specified account.

**Solution**: Verify account ownership and permissions:

<!-- fragment: partial account verification example -->
<!-- fragment: Demo comprehensive account access verification with detailed permission analysis -->
```python
import time
from decimal import Decimal
from typing import Dict, List, Any, Optional
from fivetwenty import AsyncClient, Environment


async def demonstrate_comprehensive_account_access_verification() -> Dict[str, Any]:
    """Demonstrate comprehensive account access verification with detailed permission analysis."""
    print(f"Comprehensive Account Access Verification Demonstration")

    # Step 1: Initialize verification tracking
    verification_start_time = time.time()
    verification_results = {
        "account_accessible": False,
        "account_details": {},
        "permissions_verified": [],
        "permission_issues": [],
        "error_details": None,
        "verification_timestamp": verification_start_time
    }

    print(f"\nAnalysis: Account Access Verification Process:")
    print(f"   Time Verification start: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(verification_start_time))}")
    print(f"   Purpose: Verify token can access intended account")
    print(f"   Scope: Account details, permissions, and operational capabilities")

    async with AsyncClient() as client:

        # Step 2: Environment context for verification
        current_environment = client.config.environment.value
        print(f"\nEnvironment: Environment Context:")
        print(f"   Environment: {current_environment.upper()}")
        print(f"   Account type: {'Live trading account' if current_environment == 'live' else 'Practice account'}")
        print(f"   Risk level: {'Real money' if current_environment == 'live' else 'Virtual money'}")

        try:
            # Step 3: Primary account access verification
            print(f"\nLock Primary Account Access Test:")
            print(f"   Account ID: {client.account_id}")
            print(f"   Processing Attempting account data retrieval...")

            account = await client.accounts.get_account(client.account_id)
            verification_results["account_accessible"] = True

            # Step 4: Extract and analyze account details
            account_balance = Decimal(account.balance)
            unrealized_pl = Decimal(account.unrealized_pl)
            margin_used = Decimal(account.margin_used)
            margin_available = Decimal(account.margin_available)
            open_trade_count = account.open_trade_count
            open_position_count = account.open_position_count

            verification_results["account_details"] = {
                "id": account.id,
                "alias": account.alias,
                "currency": account.currency,
                "balance": str(account_balance),
                "unrealized_pl": str(unrealized_pl),
                "margin_used": str(margin_used),
                "margin_available": str(margin_available),
                "open_trades": open_trade_count,
                "open_positions": open_position_count,
                "created_time": account.created_time
            }

            print(f"   Account access: SUCCESSFUL")
            print(f"\nRisk-free algorithm validationAccount Details Retrieved:")
            print(f"   Account alias: {account.alias or 'No alias set'}")
            print(f"   Account currency: {account.currency}")
            print(f"   Balance: ${account_balance}")
            print(f"   Unrealized P/L: ${unrealized_pl}")
            print(f"   Open trades: {open_trade_count}")
            print(f"   Open positions: {open_position_count}")
            print(f"   🗓️ Account created: {account.created_time}")

            # Step 5: Comprehensive permission verification
            print(f"\nLock Permission Verification Tests:")

            # Test 1: Account list access
            try:
                print(f"   Analysis: Testing account list access...")
                accounts = await client.accounts.get_accounts()
                verification_results["permissions_verified"].append("account_list_access")
                print(f"      Account list access: GRANTED ({len(accounts)} accounts visible)")

                # Verify our target account is in the list
                target_account_found = any(acc.id == client.account_id for acc in accounts)
                if target_account_found:
                    print(f"      Target account found in account list")
                else:
                    print(f"      ⚠️ Target account not found in account list")
                    verification_results["permission_issues"].append("target_account_not_in_list")

            except Exception as list_error:
                print(f"      Error Account list access: DENIED ({type(list_error).__name__})")
                verification_results["permission_issues"].append(f"account_list_access_denied: {str(list_error)}")

            # Test 2: Account summary access
            try:
                print(f"   Analysis: Testing account summary access...")
                summary = await client.accounts.get_account_summary(client.account_id)
                verification_results["permissions_verified"].append("account_summary_access")
                print(f"      Account summary access: GRANTED")
                print(f"      Summary NAV: ${summary.nav}")
                print(f"      Summary balance: ${summary.balance}")

            except Exception as summary_error:
                print(f"      Error Account summary access: DENIED ({type(summary_error).__name__})")
                verification_results["permission_issues"].append(f"account_summary_denied: {str(summary_error)}")

            # Test 3: Position access (if any positions exist)
            try:
                print(f"   Analysis: Testing position access...")
                positions = await client.positions.get_positions(client.account_id)
                verification_results["permissions_verified"].append("position_access")
                print(f"      Position access: GRANTED ({len(positions)} positions visible)")

            except Exception as position_error:
                print(f"      Error Position access: DENIED ({type(position_error).__name__})")
                verification_results["permission_issues"].append(f"position_access_denied: {str(position_error)}")

            # Test 4: Order access
            try:
                print(f"   Analysis: Testing order access...")
                orders = await client.orders.get_orders(client.account_id)
                verification_results["permissions_verified"].append("order_access")
                print(f"      Order access: GRANTED ({len(orders)} orders visible)")

            except Exception as order_error:
                print(f"      Error Order access: DENIED ({type(order_error).__name__})")
                verification_results["permission_issues"].append(f"order_access_denied: {str(order_error)}")

            # Test 5: Transaction history access (limited test)
            try:
                print(f"   Analysis: Testing transaction history access...")
                # Get recent transactions (limit to 10 for testing)
                transactions = await client.transactions.get_transactions(client.account_id, count=10)
                verification_results["permissions_verified"].append("transaction_access")
                print(f"      Transaction access: GRANTED ({len(transactions)} recent transactions)")

            except Exception as transaction_error:
                print(f"      Error Transaction access: DENIED ({type(transaction_error).__name__})")
                verification_results["permission_issues"].append(f"transaction_access_denied: {str(transaction_error)}")

            # Step 6: Account health and readiness assessment
            print(f"\n🏥 Account Health Assessment:")

            # Balance health check
            if current_environment == "live":
                minimum_live_balance = Decimal("1000.00")
                if account_balance >= minimum_live_balance:
                    print(f"   Balance health: GOOD (${account_balance} ≥ ${minimum_live_balance})")
                else:
                    print(f"   ⚠️ Balance health: LOW (${account_balance} < ${minimum_live_balance})")
                    print(f"      Note Consider adding funds for safer live trading")
            else:
                print(f"   Practice balance: ${account_balance} (virtual - always safe)")

            # Margin health check
            total_margin = margin_used + margin_available
            if total_margin > 0:
                margin_utilization = (margin_used / total_margin) * 100
                if margin_utilization < 50:
                    print(f"   Margin health: EXCELLENT ({margin_utilization:.1f}% utilized)")
                elif margin_utilization < 80:
                    print(f"   Yellow Margin health: MODERATE ({margin_utilization:.1f}% utilized)")
                else:
                    print(f"   🟠 Margin health: HIGH ({margin_utilization:.1f}% utilized)")
                    print(f"      ⚠️ Consider reducing positions or adding funds")
            else:
                print(f"   Info Margin status: No active positions")

        except Exception as access_error:
            verification_results["account_accessible"] = False
            verification_results["error_details"] = str(access_error)

            print(f"   Error Account access: FAILED")
            print(f"   Analysis: Error type: {type(access_error).__name__}")
            print(f"   Error message: {str(access_error)}")

            # Step 7: Detailed error analysis for troubleshooting
            print(f"\nAnalysis: Account Access Error Analysis:")

            if "403" in str(access_error) or "Forbidden" in str(access_error):
                print(f"   Error Category: PERMISSION DENIED")
                print(f"   Note Likely causes:")
                print(f"      1. Token lacks permission to access this account")
                print(f"      2. Account ID doesn't match token's authorized accounts")
                print(f"      3. Account has restricted access or is suspended")
                print(f"   Tools Troubleshooting steps:")
                print(f"      1. Verify account ID matches your OANDA account")
                print(f"      2. Check token was created for correct account")
                print(f"      3. Verify account is active and accessible")
                print(f"      4. Contact OANDA support if account appears correct")

            elif "404" in str(access_error) or "Not Found" in str(access_error):
                print(f"   Error Category: ACCOUNT NOT FOUND")
                print(f"   Note Likely causes:")
                print(f"      1. Account ID is incorrect or mistyped")
                print(f"      2. Account doesn't exist in this environment")
                print(f"      3. Account ID format is invalid")
                print(f"   Tools Troubleshooting steps:")
                print(f"      1. Double-check account ID spelling and format")
                print(f"      2. Verify using practice account ID for practice tokens")
                print(f"      3. Verify using live account ID for live tokens")
                print(f"      4. Check OANDA portal for correct account ID")

            elif "401" in str(access_error) or "Unauthorized" in str(access_error):
                print(f"   Error Category: AUTHENTICATION FAILURE")
                print(f"   Note Likely causes:")
                print(f"      1. Invalid or expired token")
                print(f"      2. Token/environment mismatch")
                print(f"   Tools Troubleshooting steps:")
                print(f"      1. Verify token is valid and not expired")
                print(f"      2. Check token matches environment (practice/live)")
                print(f"      3. Regenerate token if needed")

            else:
                print(f"   Error Category: OTHER/NETWORK")
                print(f"   Note General troubleshooting:")
                print(f"      1. Check internet connection")
                print(f"      2. Verify OANDA API is accessible")
                print(f"      3. Try again in a few minutes")
                print(f"      4. Contact support if issue persists")

    # Step 8: Final verification summary
    verification_duration = time.time() - verification_start_time

    print(f"\nRisk-free algorithm validationACCOUNT ACCESS VERIFICATION SUMMARY:")
    print(f"   Account accessible: {'Success YES' if verification_results['account_accessible'] else 'Error NO'}")
    print(f"   Lock Permissions verified: {len(verification_results['permissions_verified'])}")
    print(f"   ⚠️ Permission issues: {len(verification_results['permission_issues'])}")
    print(f"   Time Verification time: {verification_duration:.2f} seconds")

    if verification_results["account_accessible"]:
        print(f"\nSuccess VERIFICATION SUCCESSFUL:")
        print(f"   Account access confirmed")
        print(f"   Account details retrieved")
        print(f"   Lock Permissions verified: {', '.join(verification_results['permissions_verified'])}")
        if verification_results["permission_issues"]:
            print(f"   ⚠️ Minor issues detected: {len(verification_results['permission_issues'])}")
    else:
        print(f"\nError VERIFICATION FAILED:")
        print(f"   ⚠️ Cannot access account")
        print(f"   Tools Review error analysis and fix configuration")

    return verification_results


# Account access verification execution
print(f"Starting Comprehensive Account Access Verification")
try:
    import asyncio

    results = asyncio.run(demonstrate_comprehensive_account_access_verification())

    print(f"\nCurrent environment: Final Verification Summary:")
    print(f"   Account access: {'Successful' if results['account_accessible'] else 'Failed'}")
    print(f"   Lock Permissions working: {len(results['permissions_verified'])}")
    print(f"   ⚠️ Issues found: {len(results['permission_issues'])}")

except Exception as e:
    print(f"Verification system error: {e}")
    print(f"Note: Check client configuration and credentials")

print(f"Account access verification demonstration complete")
print(f"Remember: Proper access verification prevents operational surprises")
```

---

## Best Practices

### Development Best Practices

1. **Always start with practice** - Never develop directly in live environment
2. **Use realistic position sizes** - Test with sizes you'd actually trade
3. **Test edge cases** - Try invalid instruments, large orders, insufficient margin
4. **Validate error handling** - Ensure your code handles API failures gracefully

### Production Best Practices

1. **Start small** - Begin live trading with minimal position sizes
2. **Monitor closely** - Watch initial live trades carefully
3. **Have exit strategies** - Know how to quickly close all positions
4. **Regular reviews** - Assess performance and adjust strategies

### Security Best Practices

1. **Separate credentials** - Use different tokens for practice and live
2. **Environment validation** - Always confirm which environment you're using
3. **Access controls** - Limit who can access live trading credentials
4. **Regular rotation** - Rotate API tokens periodically

---

## Next Steps

**Related Guides:**
- [Configuration Patterns](configuration.md) - Advanced environment configuration
- [Best Practices](best-practices.md) - Production trading considerations
- [Security Guidelines](best-practices.md#token-security) - Protecting your credentials

**Task Complete**: You can now keep practice and live credentials separate, validate which environment a token targets, and move a strategy from practice to live in stages.