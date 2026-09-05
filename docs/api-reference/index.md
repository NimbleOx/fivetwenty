# API reference

Find method signatures, request parameters, response types and model fields. These
pages describe FiveTwenty's Python interface and link to OANDA's documentation for
server behavior and account-specific restrictions.

| Reference | Contents |
| --- | --- |
| [Clients](client.md) | Async and synchronous interfaces, connection settings and cleanup |
| [Configuration](configuration.md) | Credentials, environment loading and local validation |
| [Endpoints](endpoints/index.md) | Methods grouped by API resource |
| [Models](models/index.md) | Parsed response objects, request models and enums |
| [Exceptions](exceptions.md) | Exception attributes and classification helpers |
| [Error handling](error-handling.md) | When requests retry, how to log errors and how to recover |
| [OpenAPI compatibility specification](oanda-openapi-spec.md) | Project-maintained schema and source limitations |

Most methods return a dictionary containing typed models and metadata. For example,
`get_orders()` returns the order models in `response["orders"]` and the transaction
cursor in `response["lastTransactionID"]`. Each method's return description explains
its response shape: `get_accounts()` returns a list directly, while streaming
methods yield records as they arrive.

Order responses vary with the outcome. Check the returned transaction fields to
determine whether an order was created, filled or cancelled.

For a complete first script, use the [authentication tutorial](../tutorials/getting-started/authentication.md).
The [guides](../guides/index.md) explain connection management and workflows that
combine several API calls.
