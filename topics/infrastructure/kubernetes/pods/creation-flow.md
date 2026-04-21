# Creation flow

A Pod passes through four components between `kubectl apply` and a
running process: the API server, etcd, the scheduler, and the kubelet
on the target node. The Pod has an IP once the kubelet sets up its
network namespace, but the control plane does not learn that IP
until the kubelet reports it back.

## End-to-end sequence

```text
+------------------+
|  kubectl apply   |
+--------+---------+
         |
         v
+------------------+
|  kube-apiserver  |
|  authn / authz   |
|   / admission    |
+--------+---------+
         | persist
         v
+------------------+
|       etcd       |
+--------+---------+
         |
         v
+------------------+
|  kube-scheduler  |
|  filter + score  |
|      + bind      |
+--------+---------+
         | Pod now has a nodeName
         v
+------------------+
| kubelet (watch)  |
|  CRI, CNI, CSI   |
+--------+---------+
         | report status + IP
         v
+------------------+
|    apiserver     |
|   updates etcd   |
+------------------+
```

## Control plane

The **API server** receives the YAML, runs authentication,
authorization, and admission controllers, then persists the Pod to
etcd. At this point the Pod exists as an object but has no node
assignment.

The **scheduler** watches for Pods with no `nodeName`. It runs
filter and score phases to pick a node, then writes a binding back
through the API server. The Pod now has a `nodeName` but is still
not running — only assigned.

Every state transition from here — the initial create, the binding,
and each status update from the kubelet — lands in etcd.

## Kubelet on the node

The kubelet watches the API server (not polls) for Pods assigned to
its node. When a new assignment arrives, it delegates to three
plugin interfaces:

| Interface | Responsibility                              |
|-----------|---------------------------------------------|
| CRI       | Pull the image and start the containers     |
| CNI       | Attach the Pod to the network and assign IP |
| CSI       | Mount volumes into the containers           |

CRI handles both container startup and image pulling — its API
defines RuntimeService and ImageService.

Once CNI reports a successful IP assignment, the Pod is reachable
from anything already on its network — but the control plane does
not yet know.

## Status reporting

The kubelet sends a status update to the API server carrying the
Pod's IP, container states, and conditions. This update makes the
Pod visible as Running with an addressable IP to the rest of the
cluster. Before it lands, the Pod exists only on its node.

The asymmetry — kubelet knows first, API server learns second — is
why tools reading from the API server can briefly disagree with
what's actually running on the node.

## Related

- [Fundamentals](fundamentals.md) - What a Pod is
- [Lifecycle](lifecycle.md) - States and transitions after creation
- [Scheduling](scheduling.md) - How the scheduler picks a node

---

Return to [Pods](_index.md)
