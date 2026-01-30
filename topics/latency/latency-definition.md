# Latency Definition

**Latency:** The time delay between a cause and its observed effect.

This definition transforms "it feels slow" (a feeling) into "it took 200ms" (a
metric). You cannot optimize what you cannot measure.

## The stopwatch rule

To measure latency, you must define exactly when to start and stop the clock:

| Definition                              | Includes                   |
| --------------------------------------- | -------------------------- |
| Request hits server → Response sent     | Server processing only     |
| User clicks button → First byte arrives | Network + server           |
| User clicks → Page fully rendered       | Network + server + browser |

**Context is everything.** Different boundaries produce different numbers, and
optimizations target different layers.

## The cost of abstraction

Consider the evolution from dumb switch to smart bulb:

**Dumb switch:** Close circuit → electrons flow → light. Nanoseconds.

**Smart bulb:** Tap screen → phone CPU → WiFi → router → hub → Zigbee →
bulb CPU → LED. Milliseconds to seconds.

Every layer of abstraction (TCP/IP, Bluetooth, JSON, encryption) adds latency.
To reduce latency, you often must remove layers, getting closer to raw hardware
performance.

## The two questions

When analyzing any slow system:

1. Where does the stopwatch start? (The cause)
2. Where does the stopwatch stop? (The observed effect)

Without agreement on these boundaries, you cannot fix the problem.

## Related

- [Latency constants](latency-constants.md) - Physical limits at each time scale
- [Bandwidth and throughput](bandwidth-throughput.md) - Distinguishing speed
  from volume
