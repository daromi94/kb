# Latency Constants

The speed of light establishes hard physical limits on system design. Grace
Hopper famously distributed 11.8-inch wires to visualize a nanosecond.

| Time Unit     | Distance       | Context                                    |
| ------------- | -------------- | ------------------------------------------ |
| 1 nanosecond  | ~30 cm         | CPU cache territory - data must be on-chip |
| 1 microsecond | ~300 meters    | Datacenter territory - same rack/building  |
| 1 millisecond | ~300 km        | Internet territory - cross-city requests   |
| 1 second      | ~300,000 km    | 7.5x around Earth, 80% to the Moon         |

## Implications for system design

**Nanoseconds:** L1/L2 cache access. Data must be inches away on the chip
itself.

**Microseconds:** Network calls within a datacenter. 300 meters provides enough
cable to reach switches and return. This is your budget for in-memory databases
and local service calls.

**Milliseconds:** Geographic distance becomes the constraint. A 1ms latency
budget cannot accommodate a round-trip to a city 200 miles away - light
physically cannot travel fast enough. This is why CDNs and edge computing
exist.

The massive jump from microseconds to milliseconds explains why distributed
systems pay such a high latency tax compared to local operations.
