# Configuration

Choose one source for account identity and credentials, then supply client options
such as timeouts and retry counts. Construction validates local configuration; it
does not authenticate with OANDA until a request is sent.

## Environment variables

`AsyncClient()` and `Client()` read these process environment variables when no
configuration object or direct token is supplied:

| Variable | Meaning |
|---|---|
| `FIVETWENTY_OANDA_TOKEN` | API token; required |
| `FIVETWENTY_OANDA_ACCOUNT` | Account ID; required |
| `FIVETWENTY_OANDA_ENVIRONMENT` | `practice` or `live`; defaults to `practice` |

The loader generates the alias `default`. It does not read an
`FIVETWENTY_OANDA_ACCOUNT_ALIAS` variable. Set an alias in `AccountConfig` when you
need a particular name.

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

If these values are in `.env`, load them with `python-dotenv` before creating the
client. FiveTwenty does not read `.env` files itself. An environment variable that
is already set may take precedence over `load_dotenv()`'s default behavior; inspect
the resolved environment, not just the file you edited.

## Direct credentials

Provide both token and account ID. In this form, `environment` selects the host:

```python
import os

from fivetwenty import Client, Environment

with Client(
    token=os.environ["FIVETWENTY_OANDA_TOKEN"],
    account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
    environment=Environment.PRACTICE,
) as client:
    print(client.config.summary())
```

This example creates and closes a client without making an API request.

## Reusable configuration objects

`AccountConfig` requires `token`, `account_id`, `environment` and `alias`. An alias
starts with a letter and contains only letters, digits and underscores.

```python
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, Client, Environment

config = AccountConfig(
    alias="research",
    token=SecretStr(os.environ["FIVETWENTY_OANDA_TOKEN"]),
    account_id=SecretStr(os.environ["FIVETWENTY_OANDA_ACCOUNT"]),
    environment=Environment.PRACTICE,
)
with Client(config=config, timeout=30.0, max_retries=2) as client:
    print(client.config.summary())
```

## Configuration priority

Resolution selects a source; it does not merge all sources field by field:

1. If `config` is supplied, its credentials and environment are used. A direct
   `account_id` can override that object's account ID; direct `token` and
   `environment` values do not override it.
2. Otherwise, a direct `token` requires a direct `account_id` and uses the constructor's
   `environment` value.
3. Otherwise, the default environment-variable loader supplies the configuration.
   Passing only `environment=...` or `account_id=...` does not override that loader.

To change the environment, change the selected configuration source. Verify
`client.config.environment` before submitting orders.

## Multiple accounts and custom prefixes

`AccountConfigLoader.from_env_prefix("RESEARCH_")` reads
`RESEARCH_FIVETWENTY_OANDA_TOKEN`, `RESEARCH_FIVETWENTY_OANDA_ACCOUNT` and
`RESEARCH_FIVETWENTY_OANDA_ENVIRONMENT`. Its generated alias is `research`.
Missing token or account values return `None`; malformed supplied values can raise
validation errors. Do not silently fall back to a different account.

For a complete pattern, see [multiple accounts](../practical-solutions/multi-account-configuration.md).
JSON-file loading is described in the [configuration reference](../../api-reference/configuration.md).
A configuration file contains actual credentials; `SecretStr` does not encrypt it.

## Client settings and transports

`timeout`, `max_retries`, `datetime_format`, `logger` and HTTP options are client
settings, not `AccountConfig` fields. `max_retries=0` sends one request. UNIX datetime
format affects wire values while parsed attributes remain Python datetimes.

If you pass `transport=`, supply an `httpx.AsyncClient`, including its base URL,
proxy, TLS and pooling options. Constructor options for creating a default HTTPX
client do not reconfigure an injected one. The SDK closes the injected HTTPX client
when it closes.

## Credentials and troubleshooting

`SecretStr` masks normal configuration display, and SDK request logs redact
Authorization headers. Extracted secret values, custom log messages and JSON files
are not protected by that masking. Log the alias and environment rather than the token.

Local token checks only inspect basic shape or presence. A successful account
request verifies access at that time. For 401/403 errors, check the token, selected
environment and account access; see [authentication](../../tutorials/getting-started/authentication.md).
