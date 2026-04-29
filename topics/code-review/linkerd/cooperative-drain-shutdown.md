# Cooperative drain shutdown

Shut down a multi-subsystem service by broadcasting a signal and
waiting for every subsystem to acknowledge completion, with a hard
timeout as a backstop.

## How linkerd2-proxy does it

A drain primitive is shared with every subsystem at startup. When
shutdown is triggered, every subsystem observes the signal and begins
winding down at its own pace. The drain completes only when all
subsystems have released their handle. A timeout wraps the entire
drain so the process exits regardless if something gets stuck.

## Why it works

Each subsystem controls its own cleanup without a centralized
teardown order. No cascading cancellations that drop in-flight work.
The hard timeout prevents a stuck subsystem from blocking exit
indefinitely — critical in Kubernetes, where exceeding
terminationGracePeriodSeconds results in a SIGKILL.

## Takeaway

Broadcast shutdown intent, let each subsystem drain at its own pace,
and gate process exit on all acknowledgments with a hard timeout.
This separates the "when to stop" decision from the "how to stop"
logic in each subsystem. Treating acknowledgment as reference
counting — completion means all holders released, not that anyone
sent a message — keeps the mechanism simple and decoupled.

## Related

- [Structured config loading](structured-config-loading.md) - Startup discipline

---

Return to [Linkerd2-proxy](_index.md)
