# Hostname and DNS

Every Pod is assigned a hostname for internal identification. How that hostname
is determined and discoverable depends on whether you use a Deployment or
StatefulSet.

By default, a Pod's hostname is simply its `metadata.name`.

## Default behavior (stateless)

In a standard Deployment, Pods get random, ephemeral names:

- **Hostname:** `web-574cc94f9-2zbd7`
- **FQDN:** `web-574cc94f9-2zbd7.default.svc.cluster.local`

The hostname changes if the Pod is recreated. You typically use a Service to
load-balance rather than connecting to Pods by hostname.

## Stable hostnames with StatefulSets

StatefulSets provide stable identities with ordinal indexes (`db-0`, `db-1`).

For hostnames to be resolvable, link the StatefulSet to a headless Service. DNS
then creates a record for each Pod:

- **Hostname:** `db-0`
- **FQDN:** `db-0.database-service.default.svc.cluster.local`

This allows `db-1` to reach `db-0` reliably by name, critical for database
clustering and leader election.

## Custom hostname and subdomain

Override these fields in the Pod spec for specific requirements:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: custom-hostname-pod
spec:
  hostname: "my-custom-host"
  subdomain: "my-custom-subdomain"
  containers:
    - name: nginx
      image: nginx
```

With a headless Service named `my-custom-subdomain`, the FQDN becomes:
`my-custom-host.my-custom-subdomain.default.svc.cluster.local`

## DNS policy

The `dnsPolicy` field governs how a Pod resolves hostnames:

| Policy       | Behavior                                                      |
|--------------|---------------------------------------------------------------|
| ClusterFirst | Default; non-cluster queries forwarded to upstream nameserver |
| None         | Ignore K8s DNS; provide your own `dnsConfig`                  |
| Default      | Inherit name resolution from the node (not actually default)  |

## Comparison by workload type

| Feature     | Deployment Pods            | StatefulSet Pods        | Custom spec Pods            |
|-------------|----------------------------|-------------------------|-----------------------------|
| Hostname    | Random (e.g., `web-abc12`) | Ordinal (e.g., `web-0`) | User-defined                |
| Persistence | Lost on restart            | Persistent              | Persistent (if spec static) |
| Discovery   | Via Service IP             | Via individual Pod DNS  | Via subdomain/headless svc  |
| Best for    | Web APIs, workers          | Databases, quorum       | Legacy app requirements     |

## The /etc/hosts file

Kubernetes automatically manages `/etc/hosts` inside each container, mapping
the Pod's own IP to its hostname. The application always knows its own identity.
