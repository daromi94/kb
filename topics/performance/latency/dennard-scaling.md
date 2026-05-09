# Dennard scaling

The collapse of Dennard scaling made latency a software engineering
problem. Hardware no longer solves it automatically.

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

| Era         | Strategy       | Software implication                          |
|-------------|----------------|-----------------------------------------------|
| Before 2006 | One fast core  | Code runs faster automatically                |
| After 2006  | Multiple cores | Code only faster if rewritten for parallelism |

This is why concurrent programming and async I/O became essential —
clock speeds will not get significantly faster.

---

Return to [Latency](_index.md)
