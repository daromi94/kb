# Latency definition

Latency is the delay between a cause and its observed effect.

## The stopwatch rule

To measure latency, you must define exactly when to start and stop the clock:

| Definition                              | Includes                   |
|-----------------------------------------|----------------------------|
| Request hits server → Response sent     | Server processing only     |
| User clicks button → First byte arrives | Network + server           |
| User clicks → Page fully rendered       | Network + server + browser |

**Context is everything.** Different boundaries produce different numbers, and
optimizations target different layers.

## The cost of abstraction

Every abstraction layer adds latency. To reduce latency, you often must
remove layers, getting closer to raw hardware.

**Dumb switch:** Close circuit → electrons flow → light. Nanoseconds.

**Smart bulb:** Tap screen → phone CPU → Wi-Fi → router → hub → Zigbee →
bulb CPU → LED. Milliseconds to seconds.

## The two questions

When analyzing any slow system:

1. Where does the stopwatch start? (The cause)
2. Where does the stopwatch stop? (The observed effect)

Without agreement on these boundaries, you cannot fix the problem.

---

Return to [Latency](_index.md)
