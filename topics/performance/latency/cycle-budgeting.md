# Cycle budgeting

Divide the fleet's total CPU cycles by the target throughput. That
is the per-request cycle budget, on average. Most proposed designs
blow past it by orders of magnitude — which you want to know
before you start building, not after.

Cycle budgeting is a cheap pre-design filter. One napkin
calculation rules out entire classes of infeasible architecture
before any code is written.

## The formula

Given $C$ cores at clock frequency $f$ Hz serving throughput
$\lambda$ requests per second, the per-request cycle budget is:

$$B = \frac{C \cdot f}{\lambda}$$

A fleet of 10,000 cores at 3 GHz serving $10^8$ RPS:

$$B = \frac{10{,}000 \times 3 \times 10^9}{10^8} = 300{,}000 \text{ cycles/request}$$

Roughly 100 μs of CPU time per request. Every operation on the hot
path has to fit inside that.

## What the budget rules out

| Operation              | Rough cost                        |
|------------------------|-----------------------------------|
| Kernel context switch  | thousands of cycles + cache flush |
| Blocking syscall       | thousands of cycles               |
| Full stop-the-world GC | millions of cycles                |
| TLS handshake          | millions of cycles                |

Anything above a few thousand cycles per request must be amortized
across many requests, moved off the hot path, or eliminated.
Operations in the millions cannot run per request at all.

## Designs the budget kills on paper

Common hot-path ambitions fail the check without a prototype:
synchronous cross-service RPCs, per-request TLS handshakes,
redundant JSON reparsing at each layer. All identifiable as
infeasible before the first line of code.

Cycle budgeting is the computational twin of Little's Law. One
caps how many requests can be in flight; the other caps how much
work each can do.

---

Return to [Latency](_index.md)
