# Latency percentiles

Latency is a distribution, not a number. A test that reports only the
average hides the slow tail where real user pain lives. Always report
percentiles — p50, p95, p99, and for high-volume services p99.9.

## Why averages lie

A service with a 100ms average and a 5-second p99 is a service where
one request in a hundred takes fifty times longer than typical. The
average looks healthy. The user behind that one request is having a
bad time, and at scale one in a hundred becomes thousands of bad
sessions per hour.

The percentiles preserve the shape the average flattens. p50 is the
typical request, p95 catches the common slow path, and p99 and p99.9
expose the tail outliers that a single-number summary erases
entirely.

## Related

- [Performance signals](performance-signals.md) - Where latency sits in the metric set
- [Performance testing](performance-testing.md) - Continuous tests that watch the percentiles

---

Return to [Testing](_index.md)
