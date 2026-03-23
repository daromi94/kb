# Backlog

## Observability

### OpenTelemetry

- [ ] OTel Collector — pipelines, processors, exporters
- [ ] OTel SDK instrumentation (auto vs manual)
- [ ] OTel semantic conventions
- [ ] OpenTelemetry proto structure
- [ ] Context propagation and W3C trace context

### Metrics

- [ ] Prometheus
- [ ] Mimir

### Tracing

- [ ] Tempo
- [ ] Jaeger
- [ ] Distributed tracing patterns (span modeling, sampling)
- [ ] Sampling strategies (head vs tail)

### Logging

- [ ] Loki
- [ ] SLF4J
- [ ] Log4j2
- [ ] Structured logging patterns
- [ ] Log correlation with traces

### Dashboards and alerting

- [ ] Grafana
- [ ] Alertmanager
- [ ] SLOs, SLIs, and error budgets
- [ ] Runbooks and on-call patterns

### Other

- [ ] Profiling with Pyroscope
- [ ] Kafka as telemetry transport

## Networking

### Protocols

- [ ] IP (IPv4, IPv6, routing, ICMP)
- [ ] UDP
- [ ] DNS
- [ ] TLS and mTLS
- [ ] HTTP/2
- [ ] QUIC and HTTP/3
- [ ] gRPC performance and optimization
    - [Performance best practices](https://grpc.io/docs/guides/performance/)
    - [Optimizing gRPC part 1](https://grpc.io/blog/optimizing-grpc-part-1/)
    - [Optimizing gRPC part 2](https://grpc.io/blog/optimizing-grpc-part-2/)
- [ ] gRPC load balancing
    - [Load balancing in gRPC](https://grpc.io/blog/grpc-load-balancing/)
- [ ] gRPC on HTTP/2 deep dive
    - [gRPC on HTTP/2](https://grpc.io/blog/grpc-on-http2/)
- [ ] BGP and OSPF

### Cloud networking

- [ ] VPCs and subnets
- [ ] Security groups and firewalls
- [ ] NAT gateways
- [ ] Network policies
- [ ] Load balancing (L4 vs L7)
- [ ] Service mesh
- [ ] Overlay networks (VXLAN, GRE, WireGuard)

### Linux networking

- [ ] iptables, netfilter, and nftables
- [ ] Network namespaces (container networking)
- [ ] Traffic control and QoS
- [ ] Socket families (AF_NETLINK, AF_PACKET)
- [ ] MTU and path MTU discovery

### Tooling

- [ ] tcpdump and packet analysis
- [ ] Connection pooling

## Infrastructure

### Kubernetes

- [ ] Kubernetes Services
- [ ] Kubernetes ConfigMaps
- [ ] Kubernetes Secrets
- [ ] Kubernetes RBAC and admission controllers
- [ ] Kubernetes Custom Resource Definitions and operators
- [ ] Kubernetes Horizontal Pod Autoscaler
- [ ] Kubernetes Vertical Pod Autoscaler
- [ ] Kubernetes resource quotas and LimitRanges
- [ ] Kubernetes descheduler

### Platform tooling

- [ ] Helm
- [ ] ArgoCD and GitOps
- [ ] Terraform
- [ ] Cilium
- [ ] eBPF
- [ ] Elasticsearch
- [ ] NX

## Distributed Systems

### Systems

- [ ] Apache Ignite
- [ ] ZooKeeper
- [ ] etcd
- [ ] Redis internals
- [ ] Lucene internals

### Deep dives

- [ ] Cassandra internals (deeper)
- [ ] HBase internals (deeper)
- [ ] Pekko internals (deeper)

### Patterns

- [ ] Saga pattern
- [ ] Circuit breaker
- [ ] Bulkhead
- [ ] Backpressure
- [ ] Retry and timeout strategies
- [ ] Sidecar pattern
- [ ] Ambassador pattern
- [ ] Strangler fig pattern
- [ ] Outbox pattern
- [ ] Consensus algorithms
    - [Mathematics of Consensus — Accidental Lecture](https://tigerbeetle.com/blog/2025-11-22-mathematics-of-consensus/)
    - [Notes on Paxos](https://matklad.github.io/2020/11/01/notes-on-paxos.html)
- [ ] Two-phase commit
- [ ] Idempotency
- [ ] Cache patterns (aside, through, behind)

## Serialization

- [ ] FlatBuffers
- [ ] Avro
- [ ] Cap'n Proto
- [ ] MessagePack
- [ ] Thrift

## Languages / Java

### Build

- [ ] Gradle basics
- [ ] Multi-module projects
- [ ] Multi-project builds

### Debugging

- [ ] Remote debugging

## Computer Science

- [ ] Recursion patterns
    - [Recursion in Practice: Iteration and Subproblems](https://newsletter.francofernando.com/p/recursion-in-practice-iteration-and)
- [ ] SIMD and vectorization
    - [Roadmap: Vectorization (Cornell)](https://cvw.cac.cornell.edu/vector)
    - [Designing a SIMD Algorithm from Scratch](https://mcyoung.xyz/2023/11/27/simd-base64/)

## Languages / Go

- [ ] Go performance optimization
    - [Go Optimization Guide](https://goperf.dev/)

## Practices

- [ ] Test-driven development
