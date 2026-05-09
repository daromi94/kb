# Design principles

Every design decision in SBE optimizes for the decode path. A message
is encoded once but may be decoded by many consumers, so the codec
pushes all complexity to compile time and keeps the runtime path bare.

## Copy-free

The buffer is the message. Flyweight decoders wrap it directly —
`decoder.price()` reads at a calculated offset, not from a copy.
Encoders write directly into the send buffer. No staging area, no
intermediate representation, no memcpy between wire format and
domain access.

## Native type mapping

Primitives are encoded in their native binary representation — an
int64 is 8 bytes in little-endian, a double is IEEE 754. On x86,
reading an SBE integer is a single MOV instruction. No varint
encoding, no zig-zag encoding, no decode-time transformation.

## Allocation-free

No heap allocation on the encode or decode path. Flyweight objects are
pre-allocated and reused: call `wrap()` with a new buffer and offset,
and the same object reads a different message. One decoder object,
millions of messages.

## Streaming access

Fields are encoded and decoded in schema order. Repeating groups use
an iterator (`next()` to advance), and variable-length data must be
accessed after fixed fields and groups. This forward-only traversal
gives the hardware prefetcher a linear pattern to predict. Random
access to fixed fields works (known offsets within a block), but the
overall message walk is sequential by design.

## Word-aligned access

Fields sit at offsets respecting their natural alignment — int32 at
a 4-byte boundary, int64 at 8-byte. The schema compiler calculates
offsets with proper padding, like a C struct layout. This avoids the
cache line boundary penalty on x86 and the alignment faults that
some ARM variants raise.

## Deterministic size

For fixed-size messages (no groups, no varData), the encoded size is
known at compile time. Even with variable parts, the minimum size is
known. Transport layers can pre-allocate exact buffer space and
reason about capacity without inspecting message content.

## Constraints as tradeoffs

Each missing feature protects the hot-path performance profile:

| Omitted feature          | Reason                                     |
|--------------------------|--------------------------------------------|
| Optional fields          | Would require branching to check presence  |
| Maps                     | Would require hashing or searching         |
| Self-describing messages | Field tags waste cache, force tag dispatch |

---

Return to [Simple Binary Encoding](_index.md)
