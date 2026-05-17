# kube-proxy

kube-proxy runs on every node and implements the Service abstraction. When
a pod sends traffic to a ClusterIP, kube-proxy's rules on the local host
rewrite the destination to one of the Service's backing pods.

It does not proxy traffic itself. It watches the API server for Services
and EndpointSlices and programs the kernel's packet filter to do the
redirection — once the rules are in place, packets never leave the kernel.

## Modes

Each mode expresses the same ClusterIP DNAT rewrite through a different
kernel subsystem.

| Mode     | Kernel mechanism              | Trade-off                         |
|----------|-------------------------------|-----------------------------------|
| iptables | netfilter rule chains         | Sync cost grows with endpoints    |
| nftables | netfilter via the nft API     | Faster rule updates               |
| IPVS     | netfilter + kernel hash table | $O(1)$ lookup; more LB algorithms |

Endpoint selection is random by default; session affinity by ClientIP is
the alternative.

## eBPF replacement

CNIs like Cilium can replace kube-proxy entirely. They attach eBPF programs
to kernel hooks and keep the Service-to-endpoint table in eBPF maps, so
lookups happen closer to the socket or NIC and endpoint updates land by
writing to a map instead of rebuilding rules.

---

Return to [Networking](_index.md)
