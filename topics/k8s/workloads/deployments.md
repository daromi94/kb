# Deployments

A Deployment is the standard way to manage stateless applications in Kubernetes.
It provides a declarative abstraction on top of ReplicaSets for updating,
scaling, and maintaining Pods.

## Why Use a Deployment

Creating individual Pods directly is rarely appropriate for production.
Deployments provide:

- **Self-healing:** If a node dies or container crashes, the Deployment detects
  the state drift and spins up replacement Pods automatically
- **Scaling:** Adjust replica count with a single command or manifest change
- **Zero-downtime updates:** Rolling updates replace old Pods incrementally
- **Rollbacks:** Revert to a previous revision instantly if a deployment fails

## The Hierarchy

A Deployment doesn't manage Pods directly. It manages a ReplicaSet, which in
turn manages the Pods:

```
+-------------+
| Deployment  |  Defines strategy and Pod template
+------+------+
       |
       v
+-------------+
| ReplicaSet  |  Ensures exact replica count
+------+------+
       |
       v
+-------------+
|    Pods     |  Running containers
+-------------+
```

## Manifest Structure

Labels and selectors are the glue that allows a Deployment to find its Pods:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25.1
          ports:
            - containerPort: 80
```

## Update Strategies

When the Pod template changes (e.g., new image), the Deployment controller
applies one of two strategies:

| Strategy      | Behavior                                            |
|---------------|-----------------------------------------------------|
| RollingUpdate | Gradually replaces Pods; zero downtime (default)    |
| Recreate      | Terminates all Pods first, then starts new versions |

**Recreate** is useful when an application cannot tolerate two versions running
simultaneously, such as when holding database schema locks.

## Related

- [ReplicaSets](replicasets.md) - How Deployments track versions via ReplicaSets
- [StatefulSets](statefulsets.md) - For applications requiring stable identity
