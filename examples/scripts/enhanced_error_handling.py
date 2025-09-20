#!/usr/bin/env python3
"""
Enhanced Error Handling Example for FiveTwenty

This example demonstrates the comprehensive error handling capabilities
of FiveTwenty, including:
- Error categorization and severity levels
- Structured validation error handling
- Retry logic and rate limiting
- Error-specific remediation messages

Before running, set your FiveTwenty token:
    export FIVETWENTY_OANDA_TOKEN="your-token-here"

Then run:
    python examples/enhanced_error_handling.py
"""

import asyncio
import os

from fivetwenty import AsyncClient, Environment, ErrorCategory, ErrorSeverity, FiveTwentyError


async def demonstrate_error_handling() -> None:
    """Demonstrate various error handling patterns."""
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("Please set FIVETWENTY_OANDA_TOKEN environment variable")
        return

    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        print("🚀 Enhanced Error Handling Demonstration")
        print("=" * 60)

        # Get account for examples
        try:
            accounts = await client.accounts.get_accounts()
            if not accounts:
                print("❌ No accounts found")
                return
            account_id = accounts[0].id
        except FiveTwentyError as e:
            print(f"❌ Failed to get accounts: {e}")
            return

        # 1. Authentication Error Example
        print("\n1. Authentication Error Handling:")
        try:
            # Create client with invalid token
            invalid_client = AsyncClient(token="invalid-token", environment=Environment.PRACTICE)
            async with invalid_client:
                await invalid_client.accounts.get_accounts()
        except FiveTwentyError as e:
            print(f"   ❌ Error: {e}")
            print(f"   📊 Category: {e.error_category}")
            print(f"   🔍 Severity: {e.error_severity}")
            print(f"   🔐 Is Auth Error: {e.is_authentication_error}")
            print(f"   💡 Remediation: {e.get_remediation_message()}")

        # 2. Validation Error Example
        print("\n2. Validation Error Handling:")
        try:
            # Attempt to create order with invalid parameters
            await client.orders.post_order(
                account_id=account_id,
                instrument="INVALID_INSTRUMENT",  # type: ignore[arg-type] # Invalid instrument
                units=0,  # Invalid units (must be non-zero)
            )
        except FiveTwentyError as e:
            print(f"   ❌ Error: {e}")
            print(f"   📊 Category: {e.error_category}")
            print(f"   🔍 Is Validation Error: {e.is_validation_error}")

            # Show validation details if available
            if e.details and e.details.has_validation_errors():
                print("   📝 Validation Errors:")
                for field, errors in e.get_validation_errors().items():
                    for error_msg in errors:
                        print(f"      • {field}: {error_msg}")

            remediation = e.get_remediation_message()
            if remediation:
                print(f"   💡 Remediation: {remediation}")

        # 3. Business Logic Error Example
        print("\n3. Business Logic Error Handling:")
        try:
            # Attempt to create a very large order (likely to hit margin limits)
            await client.orders.post_order(
                account_id=account_id,
                instrument="EUR_USD",  # type: ignore[arg-type]
                units=1000000,  # Very large position
            )
        except FiveTwentyError as e:
            print(f"   ❌ Error: {e}")
            print(f"   📊 Category: {e.error_category}")
            print(f"   💰 Is Business Logic: {e.error_category == ErrorCategory.BUSINESS_LOGIC}")

            # Show additional error context if available
            if e.details and e.details.additional_fields:
                print("   📋 Additional Context:")
                for key, value in e.details.additional_fields.items():
                    print(f"      • {key}: {value}")

            remediation = e.get_remediation_message()
            if remediation:
                print(f"   💡 Remediation: {remediation}")

        # 4. Not Found Error Example
        print("\n4. Not Found Error Handling:")
        try:
            # Try to get a non-existent trade
            await client.trades.get_trade(account_id, "999999999")
        except FiveTwentyError as e:
            print(f"   ❌ Error: {e}")
            print(f"   📊 Category: {e.error_category}")
            print(f"   🔍 Is Not Found: {e.is_not_found}")
            print(f"   🔄 Is Retryable: {e.retryable}")

        # 5. Rate Limiting Demonstration
        print("\n5. Rate Limiting and Retry Logic:")
        await demonstrate_retry_logic(client, account_id)

        # 6. Error Severity-Based Handling
        print("\n6. Error Severity-Based Handling:")
        await demonstrate_severity_handling(client, account_id)

        print("\n✅ Error handling demonstration complete!")
        print("\nKey Features Demonstrated:")
        print("- Error categorization (AUTH, VALIDATION, BUSINESS_LOGIC, etc.)")
        print("- Error severity levels (INFO, WARNING, ERROR, CRITICAL)")
        print("- Structured validation error parsing")
        print("- Remediation message suggestions")
        print("- Rate limit handling with retry-after")
        print("- Additional error context extraction")


async def demonstrate_retry_logic(client: AsyncClient, account_id: str) -> None:
    """Demonstrate retry logic for rate-limited requests."""
    print("   Simulating rapid requests to trigger rate limiting...")

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            # Make rapid requests to potentially trigger rate limiting
            tasks = []
            for _ in range(10):
                task = client.accounts.get_account(account_id)
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)
            print("   ✅ All requests completed successfully")
            break

        except FiveTwentyError as e:
            if e.is_rate_limited:
                retry_count += 1
                retry_after = e.retry_after or 1

                print(f"   ⏰ Rate limited! Retry {retry_count}/{max_retries}")
                print(f"   🔄 Waiting {retry_after} seconds...")
                print(f"   📊 Error: {e}")

                if retry_count < max_retries:
                    await asyncio.sleep(retry_after)
                else:
                    print("   ❌ Max retries exceeded")
                    break
            else:
                print(f"   ❌ Non-retryable error: {e}")
                break


async def demonstrate_severity_handling(client: AsyncClient, account_id: str) -> None:
    """Demonstrate handling errors based on severity levels."""
    print("   Demonstrating severity-based error handling...")

    # Dictionary to track errors by severity
    errors_by_severity: dict[ErrorSeverity, list[FiveTwentyError]] = {
        ErrorSeverity.INFO: [],
        ErrorSeverity.WARNING: [],
        ErrorSeverity.ERROR: [],
        ErrorSeverity.CRITICAL: [],
    }

    # Simulate various error conditions
    error_scenarios = [
        # Critical: Invalid authentication
        ("invalid_token", lambda: AsyncClient(token="invalid", environment=Environment.PRACTICE)),
        # Error: Invalid order parameters
        ("validation_error", lambda: client.orders.post_order(account_id, instrument="EUR_USD", units=0)),  # type: ignore[arg-type]
        # Warning: Non-existent trade
        ("not_found", lambda: client.trades.get_trade(account_id, "999999999")),
    ]

    for scenario_name, error_func in error_scenarios:
        try:
            if scenario_name == "invalid_token":
                # Special handling for invalid token scenario
                invalid_client = error_func()  # type: ignore[no-untyped-call]
                async with invalid_client:  # type: ignore[attr-defined]
                    await invalid_client.accounts.get_accounts()  # type: ignore[attr-defined]
            else:
                await error_func()  # type: ignore[no-untyped-call,misc]
        except FiveTwentyError as e:
            severity = e.error_severity
            errors_by_severity[severity].append(e)

            print(f"   📊 {scenario_name}: {severity} - {e.code}")

    # Summary by severity
    print("\n   📈 Error Summary by Severity:")
    for severity, errors in errors_by_severity.items():
        if errors:
            print(f"   {severity}: {len(errors)} error(s)")
            for error in errors:
                action = get_action_for_severity(severity)
                print(f"      • {error.code} - {action}")


def get_action_for_severity(severity: ErrorSeverity) -> str:
    """Get recommended action based on error severity."""
    actions = {
        ErrorSeverity.INFO: "Log for monitoring",
        ErrorSeverity.WARNING: "Log and potentially retry",
        ErrorSeverity.ERROR: "Handle gracefully, notify user",
        ErrorSeverity.CRITICAL: "Stop execution, require immediate attention",
    }
    return actions.get(severity, "Unknown action")


if __name__ == "__main__":
    asyncio.run(demonstrate_error_handling())
