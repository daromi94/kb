# Overview

SBE encodes messages as flat, fixed-layout binary structs so the decoder
reads any fixed field by jumping straight to its byte offset — no parsing,
no schema lookup at runtime, no allocation. SBE originated in the FIX
trading protocol ecosystem and pairs well with Aeron for transport, but
works with any messaging layer.

## Mechanical sympathy

SBE is built on mechanical sympathy — software that works with the CPU
and its memory caches rather than against them.

**Flyweight pattern.** The SBE tool reads an XML schema and generates
flyweight encoder/decoder classes (Java, C++, C#, Rust, Go) that wrap a
raw byte buffer at a given offset. The encoder writes directly into the
buffer; the decoder reads directly from it. No intermediate objects, no
heap allocation, no copying.

**Deterministic memory access.** Field lengths and positions are known at
compile time, so the CPU can prefetch effectively. A field read is a
single indexed access like `buffer.getInt(offset + 12)` — no scanning,
no branching.

## Schema and codegen

Messages are defined in an XML schema specifying types, fields, enums,
sets, composites, groups, and varData. The SBE tool generates type-safe
flyweight codecs for the target language.

```xml
<sbe:messageSchema xmlns:sbe="http://fixprotocol.io/2016/sbe" package="trading" id="1" version="0">
    <types>
        <composite name="messageHeader">
            <type name="blockLength" primitiveType="uint16"/>
            <type name="templateId" primitiveType="uint16"/>
            <type name="schemaId" primitiveType="uint16"/>
            <type name="version" primitiveType="uint16"/>
        </composite>
        <composite name="decimal">
            <type name="mantissa" primitiveType="int64"/>
            <type name="exponent" primitiveType="int8"/>
        </composite>
        <composite name="varAsciiEncoding">
            <type name="length" primitiveType="uint32" maxValue="1073741824"/>
            <type name="varData" primitiveType="uint8" length="0" characterEncoding="ASCII"/>
        </composite>
        <enum name="side" encodingType="uint8">
            <validValue name="Buy">0</validValue>
            <validValue name="Sell">1</validValue>
        </enum>
    </types>
    <sbe:message name="Order" id="1">
        <field name="id" id="1" type="uint64"/>
        <field name="price" id="2" type="decimal"/>
        <field name="quantity" id="3" type="uint32"/>
        <field name="side" id="4" type="side"/>
        <data name="symbol" id="5" type="varAsciiEncoding"/>
    </sbe:message>
</sbe:messageSchema>
```

The schema defines composites (decimal, varAsciiEncoding) and enums
(side) that the codegen maps to type-safe accessors. Fixed fields come
first, varData (symbol) last — matching the wire layout rules.

## Tradeoffs vs Protobuf

Fixed-size fields use fixed-width integers — an int64 always takes 8
bytes on the wire. This costs bandwidth compared to Protobuf's varint
encoding but eliminates the bit-shifting and branching that varints
require during decoding.

| Aspect            | SBE                          | Protobuf                    |
|-------------------|------------------------------|-----------------------------|
| Integer encoding  | Fixed-width                  | Varint (variable-length)    |
| Field access      | Direct offset                | Sequential tag scanning     |
| Decode allocation | Zero (flyweight over buffer) | Object tree on heap         |
| Schema flex       | Additive-only, no optionals  | Optional, oneof, maps, any  |
| Wire size         | Larger (fixed-width padding) | Smaller (varint + tags)     |
| Sweet spot        | Hot-path, known schema shape | General-purpose RPC and IPC |

SBE is the right choice when the message shape is known at compile time
and a hot path demands deterministic, allocation-free encode/decode.

## Related

- [Wire layout](wire-layout.md) - How fields are arranged on the wire
- [Schema evolution](schema-evolution.md) - Additive-only versioning rules

---

Return to [Simple Binary Encoding](_index.md)
