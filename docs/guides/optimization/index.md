# Performance measurement and tuning

Start by measuring the work your application performs. Separate time spent waiting
for OANDA, decoding responses and processing data. Optimizing one component does
not establish a particular order fill rate or execution latency.

| Problem | Guide |
|---|---|
| Repeated connection setup or too many simultaneous requests | [Connection reuse](connection-optimization.md) |
| A consumer falls behind its price stream | [Stream processing](streaming-optimization.md) |
| Buffers or calculations consume increasing resources | [Memory and CPU](memory-cpu-optimization.md) |
| Requests or application decisions take too long | [Latency measurement](latency-optimization.md) |

Use a representative read workload first. Record percentiles, errors and sample
size, not just average latency. Keep request rates within OANDA's published limits
and recommendations. More connections or shorter timeouts can increase failures
without improving successful throughput.

The SDK provides no guaranteed throughput, fill rate or latency target. These
guides explain application techniques; they do not turn the REST API into a
high-frequency execution service.
