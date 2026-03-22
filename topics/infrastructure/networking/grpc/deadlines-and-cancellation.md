# Deadlines and cancellation

gRPC calls can fail for reasons beyond application logic: network
issues, slow servers, or explicit cancellation.

## Deadlines

Clients specify how long they will wait for an RPC to complete. If the
deadline passes, the call terminates with `DEADLINE_EXCEEDED`.

Depending on the language, this is expressed as a timeout (duration
from now) or a deadline (fixed point in time). Servers can query
whether a call has timed out or how much time remains.

## Cancellation

Either side can cancel an RPC at any time. Cancellation terminates the
call immediately — no further work is done. Changes made before the
cancellation are not rolled back.

## Termination independence

Client and server determine call success independently and locally.
Their conclusions may not match. An RPC can succeed on the server
(response sent) but fail on the client (response arrived after the
deadline).

---

Return to [gRPC](_index.md)
