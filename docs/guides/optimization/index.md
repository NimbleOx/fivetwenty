# Performance measurement and tuning

Start by measuring where your application spends time: waiting for OANDA, decoding
responses or processing data. Use those measurements to choose a guide below.

| Problem | Guide |
|---|---|
| Repeated connection setup or too many simultaneous requests | [Connection reuse](connection-optimization.md) |
| A consumer falls behind its price stream | [Stream processing](streaming-optimization.md) |
| Buffers or calculations consume increasing resources | [Memory and CPU](memory-cpu-optimization.md) |
| Requests or application decisions take too long | [Latency measurement](latency-optimization.md) |

Measure a representative set of read requests first. Record the sample size, errors
and latency percentiles alongside the average to see how often slow requests occur.
Keep request rates within OANDA's published limits and recommendations. More
connections or shorter timeouts can increase failures without improving successful
throughput.

These techniques address application performance. Order execution also depends on
OANDA and market conditions, so measure it separately from local processing time.
