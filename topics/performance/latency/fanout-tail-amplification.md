# Fanout tail amplification

User latency under fanout is the max of $N$ leaf latencies. A tail
that is rare at one leaf is typical at the user. With 100 leaves
each slow 1% of the time, 63% of user requests are slow.

## The math

The user avoids the tail only when every leaf avoids it:

$$P(\text{no tail}) = (1 - p)^N$$

| Leaf tail | Fanout $N$ | User tail exposure |
|-----------|------------|--------------------|
| 1%        | 10         | 10%                |
| 1%        | 50         | 39%                |
| 1%        | 100        | 63%                |
| 1%        | 1000       | >99%               |

## What this means for leaves

A leaf with a 5 ms median and an 80 ms p99 looks healthy on a
dashboard, but under $N = 100$ fanout most user requests hit that
p99. A leaf must target a percentile deep enough that, after fanout
amplification, it still meets the user SLO. With 1000 leaves, that
is p99.99.

Optimize the tail, not the mean.

## Related

- [Rarity as frequency](rarity-as-frequency.md) - Distribution thinking at scale
- [Tail-targeted engineering](tail-targeted-engineering.md) - Variance-reduction techniques
- [Deadline propagation](deadline-propagation.md) - Carrying a budget through the call tree
- [Cooperative cancellation](cooperative-cancellation.md) - Actually stopping work on deadline

---

Return to [Latency](_index.md)
