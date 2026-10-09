# Init containers

Init containers run before app containers start. They contain setup scripts or
utilities that aren't needed in the main application image.

## Key characteristics

| Behavior   | Description                                            |
|------------|--------------------------------------------------------|
| Completion | Must exit successfully (code 0) before next one starts |
| Sequential | Run one at a time in the order defined in YAML         |
| Blocking   | Pod stays `Pending` until all init containers succeed  |
| No probes  | Don't support readiness, liveness, or startup probes   |

## Common use cases

**Waiting for dependencies:** A script that waits for a database or external
API before the app starts, preventing repeated crash loops during startup.

**Security and least privilege:** Give the init container tools and permissions
(`git`, `sed`) to fetch secrets or generate config, while keeping those tools
out of the final application image.

**Complex setup:** Run privileged commands to set up network rules or file
permissions, while the main container runs as non-privileged.

**Populating volumes:** Clone a Git repository into a shared volume so the
application has access to latest code or static assets.

## Failure behavior

1. Kubernetes restarts the Pod until the init container succeeds
2. If `restartPolicy: Never`, a failed init container marks the entire Pod as
   failed
3. Init container code should be **idempotent** (safe to run multiple times)

## Example manifest

Wait for a database service before starting the application:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
    - name: myapp-container
      image: nginx:1.25
  initContainers:
    - name: init-myservice
      image: busybox:1.28
      command:
        - sh
        - -c
        - |
          until nslookup myservice.$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace).svc.cluster.local
          do
            echo waiting for myservice
            sleep 2
          done
```

## Resource handling

Kubernetes uses the **higher of**:

- The highest request/limit of any individual init container
- The sum of all requests/limits for all app containers

This ensures the Pod is scheduled on a node that can handle peak load. If an
init container needs 2GB RAM for data migration, the Pod lands on a node with
at least 2GB, even if the main app only needs 512MB.
