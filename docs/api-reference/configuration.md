# Configuration API reference

Configuration stores account credentials and selects an OANDA environment. Its
validation checks local values; it does not authenticate a token or verify server
permissions.

## AccountConfig

All four fields are required when constructing an `AccountConfig`:

| Field | Type | Validation |
| --- | --- | --- |
| `alias` | `str` | ASCII letter first, then letters, digits or underscores |
| `token` | `SecretStr` | Trimmed and nonempty |
| `account_id` | `SecretStr` | Trimmed and nonempty |
| `environment` | `Environment` | `PRACTICE` or `LIVE` |

This example reads credentials from the process environment and does not make a
network request:

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Environment

config = AccountConfig(
    alias="practice_account",
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
)
print(config.summary())  # practice_account (practice)
```

`summary()` returns `"{alias} ({environment})"`. `SecretStr` masks normal display
and serialization of the secret fields. It does not prevent a caller from exposing
`get_secret_value()`, HTTP authorization headers, environment variables or other
sensitive context. Do not put credentials in the alias or log raw requests.

## AccountConfigLoader

### load_default()

`load_default() -> AccountConfig | None` reads:

| Variable | Meaning |
| --- | --- |
| `FIVETWENTY_OANDA_TOKEN` | Required token |
| `FIVETWENTY_OANDA_ACCOUNT` | Required account ID |
| `FIVETWENTY_OANDA_ENVIRONMENT` | `practice` or `live`; defaults to `practice` |

The alias is `default`. Missing token or account values return `None`; malformed
present values can raise validation errors. There is no account-alias environment
variable. The loader reads `os.environ` and does not load `.env` files.

### from_env_prefix()

`from_env_prefix(prefix: str) -> AccountConfig | None` prepends the exact prefix to
the standard names. For `"RESEARCH_"`, use `RESEARCH_FIVETWENTY_OANDA_TOKEN`,
`RESEARCH_FIVETWENTY_OANDA_ACCOUNT` and `RESEARCH_FIVETWENTY_OANDA_ENVIRONMENT`.
The generated alias is the prefix lowercased with trailing underscores removed.

```python
from fivetwenty import AccountConfigLoader

config = AccountConfigLoader.from_env_prefix("RESEARCH_")
if config is None:
    message = "Missing research account credentials"
    raise ValueError(message)
print(config.summary())
```

Check for `None` before passing the result to a client. Passing `config=None` would
allow the client to select its default configuration source instead.

### Other loader methods

`load_from_env(prefix="")` is the underlying environment loader used by both
convenience methods above. `load_from_file(config_file)` reads a JSON object with
an `accounts` list; each entry supplies `alias`, `token`, `account_id` and
`environment`. It returns a list of validated configurations.

`load_by_alias(config_file, alias)` loads that file and returns the first matching
configuration, or `None` if no alias matches. Missing files, malformed JSON and
invalid entries raise errors. JSON credential values are stored as plain text on
disk; `SecretStr` masking applies after loading, not to the file itself.

## ConfigValidator

`validate_account_config(config: AccountConfig) -> list[str]` returns local
configuration diagnostics. It checks that token, account ID and alias are present.
The separate `validate_config()` dictionary helper also checks token length, account
ID shape, alias format and environment membership. An empty list means those checks passed, not that the
token grants access to the account.

Construction already performs Pydantic field validation. The additional validator
is useful for diagnostics before a read-only authentication check; it is not a
complete specification of every credential OANDA may issue.

## Environment

| Enum member | Wire value | REST base URL |
| --- | --- | --- |
| `Environment.PRACTICE` | `practice` | `https://api-fxpractice.oanda.com/v3` |
| `Environment.LIVE` | `live` | `https://api-fxtrade.oanda.com/v3` |

`Environment.base_url` exposes the corresponding URL. Live mode uses real account
funds; the SDK does not prompt before a write. Verify the resolved environment in
code when an example or deployment requires a specific mode.

## Configuration precedence

`AsyncClient` first uses an explicit `config`, with an optional direct `account_id`
override. Otherwise a direct token selects direct credentials and requires an
account ID. Without either, it uses the environment loader. Passing only
`environment` or `account_id` does not override that environment-loaded configuration.

See the [client constructor](client.md#configuration-priority) and
[configuration guide](../guides/understanding/configuration.md) for lifecycle examples.

## Error reference

Pydantic `ValidationError` reports malformed model fields. A missing `os.environ`
key raises `KeyError`. Loader methods return `None` for missing required credentials;
invalid environment strings can raise `ValueError`. The client raises `ValueError`
when it cannot resolve the credentials required by its selected source.

Handle the actual operation's failure instead of treating every configuration
exception as an OANDA authentication response. A read-only account request is the
next step for verifying access.
