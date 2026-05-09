# Instrumentation tuning

The Java agent auto-instruments dozens of libraries (Spring Web, JDBC,
Kafka clients, etc.). Tuning controls which libraries produce telemetry
and how much trace data is exported.

## Module control

Disable all instrumentation at once, then selectively re-enable:

```text
OTEL_INSTRUMENTATION_COMMON_DEFAULT_ENABLED=false
OTEL_INSTRUMENTATION_SPRING_WEB_ENABLED=true
```

Or suppress individual noisy modules while keeping everything else on:

```text
OTEL_INSTRUMENTATION_JDBC_ENABLED=false
```

The naming pattern is `OTEL_INSTRUMENTATION_[NAME]_ENABLED`. Library
names use underscores (e.g., `SPRING_WEB`, `KAFKA_CLIENTS`).

## Peer service mapping

Raw hostnames or IPs in outbound spans can be mapped to logical service
names:

```text
OTEL_INSTRUMENTATION_COMMON_PEER_SERVICE_MAPPING=10.0.0.5=user-database
```

This makes downstream dependencies readable in service graphs without
requiring the target to instrument itself.

## Sampling

Sampling controls the fraction of traces that are serialized and
exported, directly affecting storage costs and network bandwidth.

| Env var                   | System property           | Purpose            |
|---------------------------|---------------------------|--------------------|
| `OTEL_TRACES_SAMPLER`     | `otel.traces.sampler`     | Sampling strategy  |
| `OTEL_TRACES_SAMPLER_ARG` | `otel.traces.sampler.arg` | Strategy parameter |

Built-in sampler values:

| Sampler                    | Behavior                                       |
|----------------------------|------------------------------------------------|
| `parentbased_always_on`    | Default. Sample if parent sampled; root: yes   |
| `parentbased_always_off`   | Respect parent; root: no                       |
| `parentbased_traceidratio` | Respect parent; root: ratio-based              |
| `always_on`                | Unconditionally sample every span              |
| `always_off`               | Drop everything                                |
| `traceidratio`             | Sample a fixed percentage regardless of parent |

For `traceidratio` and `parentbased_traceidratio`, pass the ratio as
the sampler arg (e.g., `0.05` retains 5% of traces).

---

Return to [OpenTelemetry](_index.md)
