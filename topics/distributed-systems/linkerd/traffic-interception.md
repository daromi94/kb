# Traffic interception

Linkerd intercepts traffic transparently — the application connects to
the same addresses and ports as before and never knows the proxy
exists. An init container rewires the pod's network namespace before
the application starts.

## linkerd-init

When a pod is injected, the proxy-injector adds an init container
called `linkerd-init`. It runs before the application or proxy
containers, configures iptables rules to redirect all inbound and
outbound TCP traffic to the proxy's listening ports, then exits.

The init container requires the NET_ADMIN capability to modify the
pod's network rules. For environments where granting NET_ADMIN to
workloads is unacceptable, a CNI plugin (`linkerd2-cni`) can install
the rules at the node level instead, removing the need for the init
container entirely.

## Scope

Only TCP traffic is intercepted. UDP bypasses the mesh completely —
the proxy does not handle UDP at any layer.

---

Return to [Linkerd](_index.md)
