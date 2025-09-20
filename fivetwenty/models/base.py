"""
Base model classes for OANDA API.

Provides the foundational ApiModel class that all OANDA models inherit from.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, field_serializer


class ApiModel(BaseModel):
    """Base model for OANDA API data structures with automatic Decimal handling."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )

    @field_serializer("*")
    def serialize_decimals_and_datetimes(self, value: Any) -> Any:
        """Convert Decimal and datetime fields to strings for API compatibility (recursive)."""
        if isinstance(value, Decimal):
            return format(value, "f")  # No scientific notation
        if isinstance(value, datetime):
            # Use Z suffix for UTC timezone, otherwise include offset
            if value.tzinfo and value.utcoffset() == timedelta(0):
                return value.replace(tzinfo=None).isoformat() + "Z"
            return value.isoformat()
        if isinstance(value, dict):
            return {k: self.serialize_decimals_and_datetimes(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.serialize_decimals_and_datetimes(item) for item in value]
        return value

    # Remove the field validator for now - we'll let models handle conversion explicitly
    # This approach is simpler and avoids accidentally converting non-financial strings

    @staticmethod
    def _is_decimal_string(value: str) -> bool:
        """Check if string value represents a decimal number."""
        # Handle negative numbers and decimal points
        if not value:
            return False

        # Remove leading minus sign for checking
        check_value = value[1:] if value.startswith("-") else value

        # Check if it's a valid decimal format
        if "." in check_value:
            parts = check_value.split(".")
            if len(parts) != 2:
                return False
            return parts[0].isdigit() and parts[1].isdigit()
        return check_value.isdigit()
