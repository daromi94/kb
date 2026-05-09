# Little's law

Little's law relates three metrics in any stable queuing system:

$$L = \lambda \times W$$

| Variable  | Meaning            | Example             |
|-----------|--------------------|---------------------|
| $L$       | Concurrency (load) | In-flight requests  |
| $\lambda$ | Throughput (rate)  | Requests per second |
| $W$       | Latency (time)     | Response time       |

The law holds regardless of arrival distribution — Poisson, uniform,
or bursty. It only requires that the system is stable (arrivals
balance departures over the measurement window).

## Worked example

A service handles 800,000 requests per minute at 50 ms average
response time:

$$\lambda = \frac{800{,}000}{60} \approx 13{,}333 \text{ RPS}$$

$$L = 13{,}333 \times 0.05 = 667 \text{ concurrent requests}$$

That 667 is the minimum structural capacity the system needs. In a
thread-per-request model it means 667 threads; in an event-loop
model it means 667 lightweight objects on the heap.

## The death spiral

Because $L$ and $W$ are linearly proportional, a latency spike
multiplies required concurrency at constant throughput. If response
time jumps from 50 ms to 500 ms, concurrency jumps from 667 to
6,667. When concurrency exceeds a hard cap (thread pool, connection
pool), requests queue, latency rises further, and the system
collapses — even though arrival rate never changed.

## Assumptions

**Stationarity.** Arrival rate must equal departure rate over the
measurement window. During a traffic ramp the formula captures a
lagging snapshot, not the true state.

**No loss.** Every request that enters must eventually leave. Dropped
connections and timeout-killed requests violate conservation of flow
and make the formula undercount true load.

**Mean values.** The law uses averages. A mean latency of 50 ms with
a p99 of 1 s means 1% of requests hold concurrency slots 20x longer
than average, disproportionately consuming capacity (head-of-line
blocking). Real provisioning must account for tail latency.

**Burstiness.** Traffic is not smooth. If the average concurrency is
667, microbursts may push instantaneous concurrency past 1,000.
Provision for the peak, not the mean.

## Three levers

Since $L = \lambda \times W$ must balance, changing one variable
forces a change in the others.

**Reduce latency ($W$).** The most cost-effective lever. Halving
response time halves required concurrency at the same throughput.
Optimize queries, add caching, shorten the code path.

**Cap throughput ($\lambda$).** The stability lever. When concurrency
hits a hard limit and latency rises, the only way to prevent collapse
is to reject work — rate limiting or load shedding. Serving 80% of
users beats crashing and serving 0%.

**Increase concurrency capacity ($L$).** The scaling lever. Add
servers (horizontal), add resources (vertical), or switch from
thread-per-request to async I/O to raise the concurrency ceiling per
machine.

| Goal                    | Lever                                 |
|-------------------------|---------------------------------------|
| Handle more traffic     | Reduce $W$ or increase $L$            |
| Survive a latency spike | Shed load ($\lambda$) or increase $L$ |
| Reduce infrastructure   | Reduce $W$ or restrict $\lambda$      |

---

Return to [Latency](_index.md)
