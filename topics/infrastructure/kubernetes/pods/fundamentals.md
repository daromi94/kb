# Pod fundamentals

A Pod is the smallest deployable unit in Kubernetes. You never run containers
directly; instead, you wrap them in a Pod that provides an execution
environment.

## Shared resources

All containers in a Pod share:

| Resource  | Behavior                                                    |
|-----------|-------------------------------------------------------------|
| Network   | Same IP address and port space; communicate via `localhost` |
| Storage   | Can mount shared volumes for reading/writing the same files |
| Lifecycle | Started, stopped, and scaled together on the same node      |

## One container per Pod

The most common pattern is one container per Pod. Kubernetes manages the Pod
rather than the container directly.

### Sidecar pattern

When two containers must work closely together, place them in the same Pod:

- **Main container:** Your application
- **Sidecar container:** A helper that handles logs, encryption (service mesh
  proxy), or configuration sync

## Ephemeral by design

Pods are disposable:

- They aren't healed. If a Pod fails, Kubernetes kills it and creates a new one
  (usually via a Deployment)
- Each Pod gets a unique cluster IP, but this changes when the Pod is recreated

## Why Pods exist

Kubernetes added this layer above containers for:

1. **Management:** Treating a group of containers as a single unit of service
2. **Scheduling:** Ensuring tightly coupled containers land on the same machine
3. **Extensibility:** Infrastructure containers (like `pause`) set up networking
   before the app starts

## Minimal Pod manifest

While you typically use a Deployment, here is a raw Pod definition:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.25
      ports:
        - containerPort: 80
```

## Pod vs container

| Feature    | Container                      | Pod                                        |
|------------|--------------------------------|--------------------------------------------|
| Unit       | A single process image         | The smallest unit K8s can schedule         |
| IP address | Usually unique per container   | One IP shared by all containers in the Pod |
| Storage    | Ephemeral (lost on restart)    | Can share Volumes between containers       |
| localhost  | Refers to the container itself | Refers to all containers in the Pod        |
