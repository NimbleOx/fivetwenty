"""Account configuration management with secure credential handling."""

import os
import re

from pydantic import BaseModel, Field, SecretStr, field_validator

from ._internal.environment import Environment


class AccountConfig(BaseModel):
    """Configuration for a single OANDA trading account."""

    # Identity
    account_id: SecretStr = Field(..., description="OANDA account ID")
    alias: str = Field(..., description="User-friendly name for this account")

    # Authentication
    token: SecretStr = Field(..., description="OANDA API token")
    environment: Environment = Field(..., description="OANDA environment (practice or live)")

    model_config = {
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }

    @field_validator("alias")
    @classmethod
    def validate_alias(cls, v: str) -> str:
        """Ensure alias is safe for use as identifier."""
        if not v or not v.strip():
            raise ValueError("Alias cannot be empty")
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("Alias must be a valid identifier (letters, numbers, underscore)")
        return v

    @field_validator("token", "account_id")
    @classmethod
    def validate_secrets(cls, v: SecretStr) -> SecretStr:
        """Ensure secret fields are not empty and strip whitespace."""
        if not v or not v.get_secret_value().strip():
            raise ValueError("Secret field cannot be empty")
        # Strip whitespace from secret values
        return SecretStr(v.get_secret_value().strip())

    def __repr__(self) -> str:
        """Safe representation that never shows secrets."""
        return f"AccountConfig(alias='{self.alias}', environment={self.environment.value}, token=SecretStr('***'), account_id=SecretStr('***'))"

    def summary(self) -> str:
        """Safe summary for display."""
        return f"{self.alias} ({self.environment.value})"


class ConfigValidator:
    """Basic configuration validation."""

    @staticmethod
    def validate_account_config(config: AccountConfig) -> list[str]:
        """Returns list of validation errors."""
        errors = []

        # Check token
        try:
            token_value = config.token.get_secret_value() if config.token else ""
            if not token_value or not token_value.strip():
                errors.append("Token is required")
        except Exception:
            errors.append("Token is required")

        # Check account_id
        try:
            account_id_value = config.account_id.get_secret_value() if config.account_id else ""
            if not account_id_value or not account_id_value.strip():
                errors.append("Account ID is required")
        except Exception:
            errors.append("Account ID is required")

        # Check alias
        if not config.alias or not config.alias.strip():
            errors.append("Account alias is required")

        return errors

    @staticmethod
    def validate_token(token: str | None) -> bool:
        """Validate OANDA API token format."""
        if not token or not isinstance(token, str):
            return False

        token = token.strip()
        if not token:
            return False

        # OANDA tokens are typically 65+ characters long
        return len(token) >= 8  # Minimum reasonable length

    @staticmethod
    def validate_account_id(account_id: str | None) -> bool:
        """Validate OANDA account ID format."""
        if not account_id or not isinstance(account_id, str):
            return False

        account_id = account_id.strip()
        if not account_id:
            return False

        # OANDA account IDs follow format: XXX-XXX-XXXXXXX-XXX
        pattern = r"^\d{3}-\d{3}-\d{7}-\d{3}$"
        return re.match(pattern, account_id) is not None

    @staticmethod
    def validate_environment(environment: str | None) -> bool:
        """Validate environment string."""
        if not environment or not isinstance(environment, str):
            return False

        return environment.lower() in {"practice", "live"}

    @staticmethod
    def validate_config(config_dict: dict[str, str]) -> dict[str, str]:
        """Validate configuration dictionary and return errors by field."""
        errors = {}

        # Validate token
        if not ConfigValidator.validate_token(config_dict.get("token")):
            errors["token"] = "Invalid token format"

        # Validate account_id
        if not ConfigValidator.validate_account_id(config_dict.get("account_id")):
            errors["account_id"] = "Invalid account ID format"

        # Validate environment
        if not ConfigValidator.validate_environment(config_dict.get("environment")):
            errors["environment"] = "Invalid environment (must be 'practice' or 'live')"

        # Validate alias
        alias = config_dict.get("alias", "").strip()
        if not alias:
            errors["alias"] = "Alias is required"
        elif not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", alias):
            errors["alias"] = "Alias must be a valid identifier"

        return errors


class AccountConfigLoader:
    """Loads account configuration with secret protection."""

    @classmethod
    def load_from_env(cls, prefix: str = "FIVETWENTY_") -> AccountConfig | None:
        """Load account configuration from environment variables if available."""

        # Application is responsible for setting environment variables
        # Library just reads them if present

        token = os.getenv(f"{prefix}OANDA_TOKEN")
        account_id = os.getenv(f"{prefix}OANDA_ACCOUNT")

        # Return None if required fields not found or are just whitespace
        if not token or not account_id or not token.strip() or not account_id.strip():
            return None

        return AccountConfig(
            alias=os.getenv(f"{prefix}OANDA_ACCOUNT_ALIAS", "default"),
            token=SecretStr(token),
            account_id=SecretStr(account_id),
            environment=Environment(os.getenv(f"{prefix}OANDA_ENVIRONMENT", "practice")),
        )

    @classmethod
    def load_default(cls) -> AccountConfig | None:
        """Load the default account configuration."""
        return cls.load_from_env("FIVETWENTY_")

    @classmethod
    def from_env_prefix(cls, prefix: str) -> AccountConfig | None:
        """Load configuration with custom environment variable prefix."""
        return cls.load_from_env(prefix)

    @classmethod
    def load_from_file(cls, config_file: str) -> list[AccountConfig]:
        """Load account configurations from a JSON file."""
        import json
        from pathlib import Path

        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with config_path.open("r") as f:
            data = json.load(f)

        if "accounts" not in data:
            raise ValueError("Configuration file must contain 'accounts' key")

        accounts = []
        for account_data in data["accounts"]:
            config = AccountConfig(
                alias=account_data["alias"],
                token=SecretStr(account_data["token"]),
                account_id=SecretStr(account_data["account_id"]),
                environment=Environment(account_data["environment"]),
            )
            accounts.append(config)

        return accounts

    @classmethod
    def load_by_alias(cls, config_file: str, alias: str) -> AccountConfig | None:
        """Load a specific account configuration by alias from a JSON file."""
        accounts = cls.load_from_file(config_file)
        for account in accounts:
            if account.alias == alias:
                return account
        return None
