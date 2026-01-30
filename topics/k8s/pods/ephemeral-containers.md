# Ephemeral containers

Ephemeral containers are temporary containers for troubleshooting running Pods.
Unlike standard containers, they can be added to an already-running Pod without
restart.

## The problem

Production containers often use distroless or minimal images (`scratch`,
`alpine`) without debugging tools like `curl`, `dig`, `tcpdump`, or even a
shell.

Previous options were limited:

1. **Rebuild the image:** Add tools and redeploy (might make the bug disappear)
2. **Use `kubectl exec`:** Only works if a shell exists in the container

Ephemeral containers provide a third way: attach a new container with your
tools to the existing, running Pod.

## Key characteristics

| Constraint        | Description                                            |
|-------------------|--------------------------------------------------------|
| No resources      | Don't support `requests` or `limits`                   |
| Immutable specs   | Many fields forbidden (`ports`, `livenessProbe`, etc.) |
| Cannot be removed | Remain in Pod status until Pod is deleted              |
| Shared namespaces | Share network and IPC; can share PID with Pod spec     |

## Usage

Add ephemeral containers with `kubectl debug`, not YAML manifests:

```bash
kubectl debug -it web-app --image=busybox --target=main-container
```

- `--image=busybox`: Image containing debugging tools
- `--target=main-container`: Share process namespace with this container
  (requires `shareProcessNamespace: true` in Pod spec)

## Use cases for SREs

- **Network troubleshooting:** Run `tcpdump` or `nmap` to diagnose connectivity
- **File system inspection:** Check logs or config not exposed via logging
- **Process analysis:** Use `top`, `ps`, or `gdb` for memory leaks or deadlocks
- **Security auditing:** Run vulnerability scanner against live container

## Container type comparison

| Feature    | Regular container        | Init container           | Ephemeral container    |
|------------|--------------------------|--------------------------|------------------------|
| Creation   | At Pod startup           | At Pod startup           | Anytime (post-startup) |
| Lifecycle  | Runs for Pod life        | Runs to completion       | For debugging only     |
| Resources  | Supports limits/requests | Supports limits/requests | No resource controls   |
| Purpose    | Core application logic   | Setup/Preparation        | Interactive debugging  |
| Restarting | Based on `restartPolicy` | Restarts on failure      | Never restarts         |

## Security consideration

Ephemeral containers bypass the minimalist security of distroless images.
Access to the `pods/ephemeralcontainers` subresource should be strictly
controlled via RBAC, granted only to trusted administrators.
