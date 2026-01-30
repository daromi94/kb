# Dennard Scaling

The collapse of Dennard scaling is why latency became a software engineering
problem rather than something hardware engineers solved automatically.

## The golden age (1974-2005)

Robert Dennard observed that smaller transistors require less voltage to
switch. This created a "free lunch":

1. Shrink transistors → power usage drops
2. Increase clock frequency → power usage rises back to previous level
3. Net result: faster CPU, same power and heat

For 30 years, software automatically ran 2x faster every 18 months without any
code changes.

## The collapse (2006+)

Transistors approached atomic scales, hitting two physical limits:

**Leakage:** Electrons quantum-tunnel through transistors even when "off,"
generating heat regardless of activity.

**Voltage floor:** Below a threshold voltage, transistors cannot reliably
distinguish on from off.

Since voltage couldn't decrease further, increasing frequency would cause power
density to melt the chip. CPU speeds hit a wall at 3-4 GHz and haven't moved
significantly since.

## The shift to multicore

Unable to make single cores faster, manufacturers added more cores:

| Era         | Strategy           | Software implication                          |
| ----------- | ------------------ | --------------------------------------------- |
| Before 2006 | One fast core      | Code runs faster automatically                |
| After 2006  | Multiple mid cores | Code only faster if rewritten for parallelism |

This is why concurrency, threading, and async I/O became essential skills. You
can no longer rely on hardware to fix latency problems - the raw clock speed is
never getting significantly faster again.

## Related

- [Latency-throughput tradeoff](latency-throughput-tradeoff.md) - Why adding
  cores doesn't linearly improve performance
