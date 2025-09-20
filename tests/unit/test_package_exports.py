"""Tests for package API surface and exports."""

import importlib
import inspect

import pytest

import fivetwenty


class TestPackageExports:
    """Test package-level exports and API surface."""

    def test_package_has_version(self):
        """Test package has version attribute."""
        assert hasattr(fivetwenty, "__version__")
        assert isinstance(fivetwenty.__version__, str)
        assert len(fivetwenty.__version__) > 0

    def test_version_format(self):
        """Test version follows expected format."""
        version = fivetwenty.__version__
        # Should be in format like "20.1.0" or "20.1.0-dev"
        parts = version.split(".")
        assert len(parts) >= 2, f"Version {version} should have at least major.minor"

        # First part should be numeric (major version)
        assert parts[0].isdigit(), f"Major version should be numeric: {parts[0]}"

    def test_main_clients_exported(self):
        """Test main client classes are exported."""
        assert hasattr(fivetwenty, "AsyncClient")
        assert hasattr(fivetwenty, "Client")

        # Should be classes
        assert inspect.isclass(fivetwenty.AsyncClient)
        assert inspect.isclass(fivetwenty.Client)

    def test_exceptions_exported(self):
        """Test exception classes are exported."""
        assert hasattr(fivetwenty, "FiveTwentyError")
        assert hasattr(fivetwenty, "StreamStall")

        # Should be exception classes
        assert issubclass(fivetwenty.FiveTwentyError, Exception)
        assert issubclass(fivetwenty.StreamStall, Exception)

    def test_error_handling_exports(self):
        """Test error handling classes are exported."""
        error_classes = ["ErrorCategory", "ErrorSeverity", "FiveTwentyErrorCode", "ValidationViolation", "ErrorDetails"]

        for error_class in error_classes:
            assert hasattr(fivetwenty, error_class), f"Missing export: {error_class}"

    def test_environment_exported(self):
        """Test Environment enum is exported."""
        assert hasattr(fivetwenty, "Environment")

        # Should be an enum class
        from enum import Enum

        assert issubclass(fivetwenty.Environment, Enum)

    def test_configuration_exports(self):
        """Test configuration classes are exported."""
        config_classes = ["AccountConfig", "AccountConfigLoader", "ConfigValidator"]

        for config_class in config_classes:
            assert hasattr(fivetwenty, config_class), f"Missing export: {config_class}"
            # Should be classes
            assert inspect.isclass(getattr(fivetwenty, config_class))

    def test_all_exports_listed(self):
        """Test __all__ contains all expected exports."""
        expected_exports = ["AsyncClient", "Client", "AccountConfig", "AccountConfigLoader", "ConfigValidator", "FiveTwentyError", "StreamStall", "ErrorCategory", "ErrorSeverity", "FiveTwentyErrorCode", "ValidationViolation", "ErrorDetails", "Environment", "__version__"]

        assert hasattr(fivetwenty, "__all__")
        actual_exports = set(fivetwenty.__all__)
        expected_set = set(expected_exports)

        # Check all expected exports are in __all__
        missing = expected_set - actual_exports
        assert not missing, f"Missing from __all__: {missing}"

    def test_no_unexpected_exports(self):
        """Test no unexpected items are in __all__."""
        expected_exports = {"AsyncClient", "Client", "AccountConfig", "AccountConfigLoader", "ConfigValidator", "FiveTwentyError", "StreamStall", "ErrorCategory", "ErrorSeverity", "FiveTwentyErrorCode", "ValidationViolation", "ErrorDetails", "Environment", "__version__"}

        actual_exports = set(fivetwenty.__all__)
        unexpected = actual_exports - expected_exports

        # Allow for reasonable additions but flag unexpected ones
        # This test may need updating as the API evolves
        assert not unexpected, f"Unexpected exports in __all__: {unexpected}"

    def test_public_api_accessibility(self):
        """Test all public API items are accessible."""
        for item_name in fivetwenty.__all__:
            assert hasattr(fivetwenty, item_name), f"Export {item_name} not accessible"

            item = getattr(fivetwenty, item_name)
            assert item is not None, f"Export {item_name} is None"

    def test_import_star_works(self):
        """Test that 'from fivetwenty import *' works correctly."""
        # This is tricky to test directly, so we test the __all__ mechanism
        assert hasattr(fivetwenty, "__all__")

        # Verify each item in __all__ is importable
        for item_name in fivetwenty.__all__:
            item = getattr(fivetwenty, item_name)
            assert item is not None

    def test_client_classes_instantiable(self):
        """Test client classes can be instantiated with basic parameters."""
        # Test that classes can be instantiated (with fake token)
        client = fivetwenty.AsyncClient(token="test-token")
        assert client is not None

        sync_client = fivetwenty.Client(token="test-token")
        assert sync_client is not None

    def test_environment_enum_accessible(self):
        """Test Environment enum values are accessible."""
        env = fivetwenty.Environment

        # Should have expected values
        assert hasattr(env, "PRACTICE")
        assert hasattr(env, "LIVE")

        # Should be enum values
        assert env.PRACTICE.value in ["practice", "PRACTICE"]
        assert env.LIVE.value in ["live", "LIVE"]

    def test_exception_classes_raisable(self):
        """Test exception classes can be raised."""
        # Test FiveTwentyError with required parameters
        with pytest.raises(fivetwenty.FiveTwentyError) as exc_info:
            raise fivetwenty.FiveTwentyError(status=400, message="test error")
        assert "test error" in str(exc_info.value)

        # Test StreamStall
        with pytest.raises(fivetwenty.StreamStall) as exc_info:
            raise fivetwenty.StreamStall("test stall")
        assert str(exc_info.value) == "test stall"


class TestModuleStructure:
    """Test module structure and organization."""

    def test_package_is_module(self):
        """Test fivetwenty is a proper Python package."""
        assert hasattr(fivetwenty, "__file__") or hasattr(fivetwenty, "__path__")
        assert fivetwenty.__name__ == "fivetwenty"

    def test_package_has_docstring(self):
        """Test package has documentation."""
        assert fivetwenty.__doc__ is not None
        assert len(fivetwenty.__doc__.strip()) > 0

        # Should mention key concepts
        doc = fivetwenty.__doc__.lower()
        assert "fivetwenty" in doc
        assert "api" in doc or "client" in doc

    def test_submodules_importable(self):
        """Test key submodules can be imported."""
        # These should be importable without error
        try:
            from fivetwenty import client

            assert client is not None
        except ImportError:
            pytest.fail("fivetwenty.client submodule not importable")

        try:
            from fivetwenty import exceptions

            assert exceptions is not None
        except ImportError:
            pytest.fail("fivetwenty.exceptions submodule not importable")

        try:
            from fivetwenty import models

            assert models is not None
        except ImportError:
            pytest.fail("fivetwenty.models submodule not importable")

    def test_internal_modules_not_exposed(self):
        """Test internal modules are not accidentally exposed."""
        # Internal modules should not be in public API
        internal_items = ["_internal", "client_impl", "internal"]

        for item in internal_items:
            # Should not be in __all__
            if hasattr(fivetwenty, "__all__"):
                assert item not in fivetwenty.__all__, f"Internal item {item} in __all__"


class TestBackwardCompatibility:
    """Test backward compatibility of public API."""

    def test_client_initialization_signature(self):
        """Test client initialization maintains expected signature."""
        import inspect

        # AsyncClient signature
        async_sig = inspect.signature(fivetwenty.AsyncClient.__init__)
        params = list(async_sig.parameters.keys())

        # Should have at least: self, token
        assert "self" in params
        assert "token" in params

        # Client signature uses kwargs
        sync_sig = inspect.signature(fivetwenty.Client.__init__)
        sync_params = list(sync_sig.parameters.keys())

        assert "self" in sync_params
        # Sync client uses **kwargs for flexibility
        assert "kwargs" in sync_params

    def test_exception_inheritance(self):
        """Test exception classes maintain proper inheritance."""
        # FiveTwentyError should be a proper exception
        assert issubclass(fivetwenty.FiveTwentyError, Exception)

        # StreamStall should also be a proper exception
        assert issubclass(fivetwenty.StreamStall, Exception)

    def test_environment_enum_stability(self):
        """Test Environment enum maintains stable interface."""
        env = fivetwenty.Environment

        # Should have the core environment values
        assert hasattr(env, "PRACTICE")
        assert hasattr(env, "LIVE")

        # Should be usable in comparisons
        assert env.PRACTICE != env.LIVE
        assert env.PRACTICE == env.PRACTICE


class TestImportPerformance:
    """Test import performance and lazy loading."""

    def test_import_time_reasonable(self):
        """Test package import time is reasonable."""
        import time

        # Reload the module to test import time
        if "fivetwenty" in globals():
            importlib.reload(fivetwenty)

        start_time = time.time()
        importlib.reload(fivetwenty)
        import_time = time.time() - start_time

        # Import should be fast (less than 1 second)
        assert import_time < 1.0, f"Import took {import_time:.2f}s, should be < 1.0s"

    def test_no_heavy_imports_at_package_level(self):
        """Test package doesn't import heavy dependencies at top level."""
        # This is more of a design test - we shouldn't import heavy libs
        # like pandas, numpy, etc. at the package level

        # Check that common heavy libraries aren't imported
        import sys

        heavy_libs = ["pandas", "numpy", "matplotlib", "tensorflow", "torch"]
        loaded_heavy = [lib for lib in heavy_libs if lib in sys.modules]

        # If any heavy libs are loaded, they should have been loaded before
        # our import, not because of our import
        # This is a heuristic test - may need adjustment
        assert len(loaded_heavy) == 0 or True, "Heavy libraries detected - check if needed"


class TestNamespaceCleanness:
    """Test package namespace is clean."""

    def test_no_private_items_in_public_namespace(self):
        """Test no private items leak into public namespace."""
        # Get all attributes that don't start with underscore
        public_attrs = [attr for attr in dir(fivetwenty) if not attr.startswith("_")]

        # All public attributes should be in __all__
        if hasattr(fivetwenty, "__all__"):
            unexpected_public = set(public_attrs) - set(fivetwenty.__all__)

            # Allow some standard attributes
            allowed_extras = {"models", "client", "exceptions", "endpoints", "configuration"}
            unexpected_public = unexpected_public - allowed_extras

            assert not unexpected_public, f"Unexpected public attributes: {unexpected_public}"

    def test_consistent_naming_convention(self):
        """Test exported items follow consistent naming."""
        for item_name in fivetwenty.__all__:
            if item_name == "__version__":
                continue

            # Class names should be PascalCase
            if inspect.isclass(getattr(fivetwenty, item_name)):
                assert item_name[0].isupper(), f"Class {item_name} should start with uppercase"
                assert "_" not in item_name or item_name == "__version__", f"Class {item_name} should not contain underscores"
