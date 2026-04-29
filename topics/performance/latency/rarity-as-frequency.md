# Rarity as frequency

"One in a million" sounds negligible. At $10^8$ requests per second
it happens 100 times per second. At scale, the word "rare" stops
meaning anything useful — what matters is how many events per
second the fleet sees, not how unlikely each one is per request.

## Multiply first, then decide

A per-request probability only becomes meaningful after you
multiply by throughput.

| Per-request rate | At $10^8$ RPS      | How it feels        |
|------------------|--------------------|---------------------|
| $10^{-2}$        | $10^6$ events/sec  | a constant firehose |
| $10^{-4}$        | $10^4$ events/sec  | one every 100 μs    |
| $10^{-6}$        | 100 events/sec     | one every 10 ms     |
| $10^{-9}$        | 1 event per 10 sec | background noise    |

A bug dismissed as "one in a million" in test fires 100 times per
second in production. It needs a runbook, a dashboard, and
handler code — not a comment saying "shouldn't happen."

## The design consequence

At fleet scale you engineer for every event that isn't
astronomically rare. The threshold for "things I have to handle"
is not a probability. It is how many times per day the event
shows up.

This is why hyperscale systems bake retries, timeouts, failure
detection, and reconciliation loops into every layer. At that
volume, every dropped packet, every timing race, every memory
bit-flip, every TCP reset happens constantly. The rare-event path
*is* the common case, just distributed across many types of rare.

---

Return to [Latency](_index.md)
