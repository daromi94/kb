# Mechanical sympathy

Mechanical sympathy is designing software to work with the CPU and its
memory caches rather than against them. SBE's design is driven by this
principle. Most serialization formats impose costs that are invisible
in typical applications but devastating on a hot path: heap allocation,
branch misprediction, and cache misses. SBE eliminates all three.

## Allocation and GC pressure

Traditional codecs decode into intermediate objects — a Protobuf
message becomes a POJO with heap-allocated strings, nested objects,
and repeated field arrays. Every decode allocates. On a path processing
millions of messages per second, this feeds the garbage collector and
causes pause spikes.

SBE's flyweight pattern eliminates this. The decoder is a view over
the buffer, not a copy of it. No objects are created, so there is
nothing to collect.

## Branch misprediction

Protobuf encodes fields as tag-value pairs. The decoder reads a tag,
branches to determine the field, then reads the value. Every tag is a
conditional branch the CPU must predict. When field order varies
between messages, those branches become unpredictable and stall the
pipeline.

SBE fixed fields sit at known offsets. Reading a field is a direct
memory access — no tag dispatch, no branching.

## Cache misses

Decoding into scattered heap objects means accessing fields requires
pointer-chasing across memory. The CPU cache gets thrashed. SBE keeps
everything in a single contiguous buffer, so reads walk linearly
through memory — exactly what the hardware prefetcher is built for.

## Streaming access

SBE encourages encoding and decoding fields in order — a sequential
memory access pattern, which is the fastest on modern hardware. Random
access to fixed fields is possible (they are at known offsets), but
sequential access is what the CPU and memory subsystem reward.

## Latency distribution

A codec can have good average throughput but terrible tail latency
when GC pauses, branch misprediction cascades, or cache miss stalls
hit. SBE's design produces tight variance on the latency distribution
— consistent low-latency rather than low-average-with-spikes. On a
trading path, a 99.9th percentile spike can cost more than all the
average-case savings.

## Cost summary

| Cost                | Traditional codecs           | SBE                            |
|---------------------|------------------------------|--------------------------------|
| Allocation          | Object tree per decode       | Zero (flyweight over buf)      |
| GC pressure         | Proportional to message rate | None                           |
| Branch prediction   | Tag dispatch per field       | No branches for fixed          |
| Cache behavior      | Pointer-chasing, scattered   | Linear scan, prefetch-friendly |
| Latency consistency | Jitter from GC and stalls    | Tight variance                 |

---

Return to [Simple Binary Encoding](_index.md)
