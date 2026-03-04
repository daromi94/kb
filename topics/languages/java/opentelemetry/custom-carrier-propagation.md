# Custom carrier propagation

The TextMapPropagator inject/extract API is transport-agnostic — it works
with any carrier that supports string key-value pairs. For non-HTTP
transports like Protobuf over Netty, you implement your own
TextMapSetter and TextMapGetter to bridge the propagator to your
message format.

## Carrier design

Add a `map<string, string>` field to the Protobuf message. The
propagator writes trace headers (`traceparent`, `tracestate`) into
this map on the sending side and reads them back on the receiving side.

```protobuf
message MyRequest {
  string payload = 1;
  map<string, string> trace_metadata = 2;
}
```

Any transport works — Unix domain sockets, TCP, shared memory — as
long as the carrier map survives serialization.

## Client-side injection

Build a TextMapSetter that writes into a plain `Map<String, String>`,
then pass the populated map to the Protobuf builder.

```java
private static final TextMapSetter<Map<String, String>> SETTER =
    (carrier, key, value) -> carrier.put(key, value);

public void sendMessage(ChannelHandlerContext ctx, String payload) {
    Map<String, String> traceMetadata = new HashMap<>();

    GlobalOpenTelemetry.getPropagators().getTextMapPropagator()
        .inject(Context.current(), traceMetadata, SETTER);

    MyRequest msg = MyRequest.newBuilder()
        .setPayload(payload)
        .putAllTraceMetadata(traceMetadata)
        .build();

    ctx.writeAndFlush(msg);
}
```

The setter targets a `Map` rather than the Protobuf message directly
because Protobuf builders do not expose a generic `put(key, value)`
method — you populate the map first, then pass it in with
`putAllTraceMetadata()`.

## Server-side extraction

Build a TextMapGetter that reads directly from the Protobuf message's
map accessor. Extract the context and start a server span.

```java
private static final TextMapGetter<MyRequest> GETTER =
        new TextMapGetter<>() {
            @Override
            public Iterable<String> keys(MyRequest carrier) {
                return carrier.getTraceMetadataMap().keySet();
            }

            @Override
            public String get(MyRequest carrier, String key) {
                return carrier.getTraceMetadataMap().get(key);
            }
        };

@Override
protected void channelRead0(ChannelHandlerContext ctx, MyRequest msg) {
    Context extracted = GlobalOpenTelemetry.getPropagators()
            .getTextMapPropagator()
            .extract(Context.root(), msg, GETTER);

    Span span = tracer.spanBuilder("process request")
            .setParent(extracted)
            .setSpanKind(SpanKind.SERVER)
            .startSpan();

    try (Scope scope = span.makeCurrent()) {
        handleRequest(msg);
    } catch (Exception e) {
        span.recordException(e);
        throw e;
    } finally {
        span.end();
    }
}
```

Using `Context.root()` as the base for extraction starts clean — no
risk of inheriting stale context from whatever ran on this event loop
thread previously.

## Async span lifecycle

When the handler offloads work to a blocking executor, the span must
end where the work completes, not where it was submitted. Ending the
span in the Netty handler after `submit()` closes it in microseconds,
long before the actual work finishes.

```java
try (Scope scope = span.makeCurrent()) {
    executor.submit(Context.current().wrap(() -> {
        try {
            doBlockingWork();
        } catch (Exception e) {
            span.recordException(e);
        } finally {
            span.end(); // end here, not in the Netty handler
        }
    }));
} // scope closes on event loop thread; span stays open
```

The `Context.current().wrap()` call bridges the trace context to the
executor thread. For executor-level wrapping with
`Context.taskWrapping()`, see the in-process propagation section in
the context deep dive.

## Related

- [Context deep dive](context-deep-dive.md) - Context mechanics in depth
- [Context and propagation](context-propagation.md) - Overview

---

Return to [OpenTelemetry](_index.md)
