# Wire format

The wire format is the binary representation of data on the network or disk.
Unlike JSON, which includes field names in every message, Protobuf uses numeric
field tags.

## Field tags

In a schema, each field is assigned an integer tag:

```protobuf
message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

**Serialization:** The encoder sends the tag (e.g., `1`) followed by the binary
value. The receiver uses its copy of the schema to map the tag back to the
field name.

**Size reduction:** Instead of sending the string `"email"`, Protobuf sends the
small numeric tag `3`.

## Varint encoding

Protobuf uses variable-length integers (varints) to minimize space. A small
integer that would take 4 bytes in standard memory might only take 1 byte in
Protobuf.

## Skip logic

The binary format allows parsers to skip unknown fields. This enables forward
and backward compatibility—old code can ignore new fields it doesn't recognize.

## Example usage

Given the schema above, generated code provides type-safe builders and
serialization:

```java
Person john = Person.newBuilder()
        .setId(1234)
        .setName("John Doe")
        .setEmail("jdoe@example.com")
        .build();

output = new FileOutputStream(args[0]);

john.writeTo(output);
```

## Size constraints

Protobuf is optimized for messages up to a few megabytes, balancing compression
with parsing speed.

---

Return to [Protocol Buffers](_index.md)
