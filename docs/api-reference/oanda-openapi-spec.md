# FiveTwenty OpenAPI Compatibility Specification

This page provides access to the project-maintained OpenAPI 3.1.0 compatibility specification for the FiveTwenty SDK surface.

It is not OANDA's official OpenAPI specification and should not be treated as complete coverage of every OANDA v20 endpoint. OANDA publishes an official Swagger 2.0 specification separately, and the live developer documentation can differ from that file.

## OpenAPI Specification File

📁 **Download**: [openapi.yaml](openapi.yaml) - FiveTwenty SDK compatibility specification

## Streaming Responses

Streaming endpoints return `application/octet-stream` containing newline-delimited
JSON records. The response body schema describes a binary stream; the
`x-oanda-record-schema` extension describes each JSON line. Transaction records
are bare transaction objects with their concrete OANDA type, interspersed with
heartbeats. Generated clients must decode these lines; there is no enclosing
`transaction` property.

## Known Source Difference

The current OANDA REST-v20 navigation publishes Instrument definitions but no longer publishes a live `instrument-ep` page. FiveTwenty keeps the instrument candle, order book, and position book methods because those endpoints remain part of OANDA's official v20 OpenAPI repository and are still represented in the cached parity source.

## Related Documentation

- [FiveTwenty API Reference](index.md) - Python SDK documentation
- [OANDA Developer Portal](https://developer.oanda.com/rest-live-v20/introduction/) - Official API documentation
- [OANDA v20 OpenAPI Repository](https://github.com/oanda/v20-openapi) - Official OANDA Swagger 2.0 specification
