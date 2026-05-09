# Watch API

The watch API is how controllers, kubelets, and schedulers learn
about cluster state changes. A component opens a long-lived HTTP
connection and receives change events as they happen, instead of
polling for current state.

## How it works on the wire

A watch is a GET with `?watch=true`. The server responds with HTTP
200 and `Transfer-Encoding: chunked`, then streams one JSON event
per line for as long as the connection stays open. Each event has a
type (`ADDED`, `MODIFIED`, `DELETED`, or `BOOKMARK`) and the full
object.

Clients process events as they arrive — no request-response
round-trip per object. Protobuf can be negotiated via the `Accept`
header for higher throughput.

## resourceVersion and resumable watches

Every Kubernetes object has a **resourceVersion** in its metadata —
an opaque string that increments monotonically as changes happen. A
watch can pass `resourceVersion=X` to resume from a known point:

```text
GET /api/v1/pods?watch=true&resourceVersion=12345
```

When a connection drops, the client reconnects with the last
resourceVersion it processed and receives every event it missed —
as long as the version is still within etcd's retention window. If
it has aged out, the server returns `410 Gone` and the client must
`LIST` to resync before watching again.

## BOOKMARK events

On a quiet watch, the client's last-seen resourceVersion drifts
behind the cluster's current one. If the connection drops after a
long silence, the client reconnects with a stale version that may
have aged out.

Bookmarks prevent this. Periodically — even without real changes —
the server sends a synthetic `BOOKMARK` event carrying the current
resourceVersion. The client records it without doing any work and
keeps a fresh resume point for free.

---

Return to [Control plane](_index.md)
