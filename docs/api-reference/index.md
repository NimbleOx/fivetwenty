# API reference

Look up the Python interface, request parameters and response structures here. The
reference describes the SDK's current surface; OANDA's linked documentation defines
server behavior and account-specific restrictions.

| Reference | Contents |
| --- | --- |
| [Clients](client.md) | Async and synchronous interfaces, transport settings and ownership |
| [Configuration](configuration.md) | Credentials, environment loading and local validation |
| [Endpoints](endpoints/index.md) | Methods grouped by API resource |
| [Models](models/index.md) | Parsed response objects, request models and enums |
| [Exceptions](exceptions.md) | Exception attributes and classification helpers |
| [Error handling](error-handling.md) | Retry boundaries, logging and recovery |
| [OpenAPI compatibility specification](oanda-openapi-spec.md) | Project-maintained schema and source limitations |

Most methods return a dictionary containing typed models and metadata. Read the
return description before accessing a result: a collection envelope, a single
model and an iterator have different interfaces. `get_accounts()` returns its list
directly. Conditional order-response fields are not present in every outcome.

For a complete first script, use the [authentication tutorial](../tutorials/getting-started/authentication.md).
The [guides](../guides/index.md) explain resource ownership and multi-step workflows.
