"""Simple focused tests to improve coverage on specific missing lines."""

from decimal import Decimal

from fivetwenty._internal.utils import stringify_decimals


class TestUtilsSimple:
    """Test utils function edge cases."""

    def test_stringify_decimals_none_handling(self):
        """Test stringify_decimals handles None values correctly."""
        # Test with None input (line that was missing coverage)
        result = stringify_decimals(None)
        assert result is None

    def test_stringify_decimals_empty_collections(self):
        """Test stringify_decimals with empty collections."""
        # Test empty dict
        result = stringify_decimals({})
        assert result == {}

        # Test empty list
        result = stringify_decimals([])
        assert result == []

    def test_stringify_decimals_basic_types(self):
        """Test stringify_decimals with basic non-Decimal types."""
        # Test string (should pass through unchanged)
        result = stringify_decimals("test_string")
        assert result == "test_string"

        # Test int (should pass through unchanged)
        result = stringify_decimals(42)
        assert result == 42

        # Test float (should pass through unchanged)
        result = stringify_decimals(3.14)
        assert result == 3.14

    def test_stringify_decimals_with_decimals(self):
        """Test stringify_decimals converts Decimal objects to strings."""
        # Test single Decimal
        result = stringify_decimals(Decimal("1.234"))
        assert result == "1.234"

        # Test list with Decimals
        result = stringify_decimals([Decimal("1.1"), Decimal("2.2")])
        assert result == ["1.1", "2.2"]

        # Test dict with Decimals
        result = stringify_decimals({"price": Decimal("100.50")})
        assert result == {"price": "100.50"}
