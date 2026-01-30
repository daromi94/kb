# Sidecar containers

Native sidecar containers (stable in Kubernetes v1.29) solve long-standing
issues with startup and shutdown ordering for helper containers.

## Definition

A native sidecar is defined in `initContainers` with `restartPolicy: Always`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app-with-proxy
spec:
  initContainers:
    - name: network-proxy
      image: proxy-image:latest
      restartPolicy: Always  # Makes it a native sidecar
      ports:
        - containerPort: 8080
  containers:
    - name: main-app
      image: my-app:v1
```

This hybrid placement gives them unique properties:

- **Start before app containers:** Being in `initContainers`, they begin first
- **Don't block app containers:** Unlike standard init containers, they don't
  need to exit; app starts once sidecar is ready
- **Stay running:** Continue for the entire Pod lifetime like regular containers

## Problems solved

Before native sidecars, managing helper containers was difficult:

| Problem            | Old behavior                          | Native sidecar behavior         |
|--------------------|---------------------------------------|---------------------------------|
| Startup race       | App might start before proxy is ready | Sidecar ready before app starts |
| Shutdown data loss | Log exporter might die before app     | Sidecar dies after app          |
| Job completion     | Sidecar prevents Job from completing  | Exits automatically with Job    |

## Common use cases

- **Service mesh proxies:** Envoy, Istio-proxy handling network traffic
- **Log collection:** Fluent Bit tailing logs from shared volumes
- **Secret watchers:** Monitoring vault and reloading app on changes
- **Database proxies:** Cloud SQL Proxy providing secure tunnels

## Lifecycle

**Startup:**

1. Kubernetes starts `initContainers` in order
2. When reaching the sidecar, waits until it's ready
3. Moves to next init container or main `containers`

**Termination:**

1. `SIGTERM` sent to main containers first
2. Sidecars continue running during main container shutdown
3. Sidecars receive `SIGTERM` only after main containers exit

## Comparison

| Feature        | Standard container (as sidecar) | Native sidecar container |
|----------------|---------------------------------|--------------------------|
| Section        | `containers`                    | `initContainers`         |
| Startup order  | Parallel with main app          | Before main app          |
| Ready state    | Doesn't block others            | Blocks until ready       |
| Shutdown order | Random/Parallel                 | After main app exits     |
| Jobs           | Prevents Job from finishing     | Allows Job to finish     |
