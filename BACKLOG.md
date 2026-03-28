# Backlog

## Observability

### Concepts

- [ ] OTel SDK instrumentation (auto vs manual)
- [ ] OTel semantic conventions
- [ ] OTel proto structure
- [ ] Context propagation and W3C trace context
- [ ] Distributed tracing patterns (span modeling, sampling)
- [ ] Sampling strategies (head vs tail)
- [ ] Structured logging patterns
- [ ] Log correlation with traces
- [ ] SLOs, SLIs, and error budgets
- [ ] Runbooks and on-call patterns
- [ ] Kafka as telemetry transport

### Tools

- [ ] OTel Collector
- [ ] Prometheus
- [ ] Mimir
- [ ] Tempo
- [ ] Jaeger
- [ ] Loki
- [ ] SLF4J
- [ ] Log4j2
- [ ] Grafana
- [ ] Alertmanager
- [ ] Pyroscope

## Networking

### Concepts

- [ ] IP (IPv4, IPv6, routing, ICMP)
- [ ] UDP
- [ ] DNS
- [ ] TLS and mTLS
- [ ] HTTP/2
- [ ] QUIC and HTTP/3
- [ ] BGP and OSPF
- [ ] VPCs and subnets
- [ ] Security groups and firewalls
- [ ] NAT gateways
- [ ] Network policies
- [ ] Load balancing (L4 vs L7)
- [ ] Service mesh
- [ ] Overlay networks (VXLAN, GRE, WireGuard)
- [ ] Network namespaces (container networking)
- [ ] Traffic control and QoS
- [ ] Socket families (AF_NETLINK, AF_PACKET)
- [ ] MTU and path MTU discovery
- [ ] Connection pooling
- [ ] gRPC performance and optimization
- [ ] gRPC load balancing
- [ ] gRPC on HTTP/2 deep dive

### Tools

- [ ] iptables, netfilter, and nftables
- [ ] tcpdump and packet analysis

### Posts

- [ ] [Performance best practices](https://grpc.io/docs/guides/performance/)
- [ ] [Optimizing gRPC part 1](https://grpc.io/blog/optimizing-grpc-part-1/)
- [ ] [Optimizing gRPC part 2](https://grpc.io/blog/optimizing-grpc-part-2/)
- [ ] [Load balancing in gRPC](https://grpc.io/blog/grpc-load-balancing/)
- [ ] [gRPC on HTTP/2](https://grpc.io/blog/grpc-on-http2/)

## Infrastructure

### Kubernetes

- [ ] Services
- [ ] ConfigMaps
- [ ] Secrets
- [ ] RBAC and admission controllers
- [ ] Custom Resource Definitions and operators
- [ ] Horizontal Pod Autoscaler
- [ ] Vertical Pod Autoscaler
- [ ] Resource quotas and LimitRanges
- [ ] Descheduler

### Concepts

- [ ] GitOps

### Tools

- [ ] Helm
- [ ] ArgoCD
- [ ] Terraform
- [ ] Cilium
- [ ] eBPF
- [ ] Elasticsearch
- [ ] NX

## Distributed Systems

### Concepts

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
- [ ] Two-phase commit
- [ ] Idempotency
- [ ] Cache patterns (aside, through, behind)

### Tools

- [ ] Apache Ignite
- [ ] ZooKeeper
- [ ] etcd
- [ ] Redis
- [ ] Lucene
- [ ] Cassandra (deeper)
- [ ] HBase (deeper)
- [ ] Pekko (deeper)

### Books

- [ ] Designing Data-Intensive Applications — Martin Kleppmann
- [ ] System Design Interview — Alex Xu
- [ ] Release It! — Michael Nygard

### Posts

- [ ] Jepsen analyses — Kyle Kingsbury
- [ ] [Mathematics of Consensus](https://tigerbeetle.com/blog/2025-11-22-mathematics-of-consensus/)
- [ ] [Notes on Paxos](https://matklad.github.io/2020/11/01/notes-on-paxos.html)

## Serialization

### Tools

- [ ] FlatBuffers
- [ ] Avro
- [ ] Cap'n Proto
- [ ] MessagePack
- [ ] Thrift

## Languages / Java

### Concepts

- [ ] Remote debugging

### Tools

- [ ] Gradle basics
- [ ] Multi-module projects
- [ ] Multi-project builds

## Computer Science

### Concepts

- [ ] Hoare logic
- [ ] TLA+
- [ ] Recursion patterns
- [ ] SIMD and vectorization

### Books

- [ ] Types and Programming Languages — Benjamin Pierce
- [ ] Specifying Systems — Leslie Lamport
- [ ] Database Internals — Alex Petrov

### Posts

- [ ] [The absolute beginners guide to databasemaxxing](https://pthorpe92.dev/databasemaxxing/)
- [ ] [Recursion in Practice](https://newsletter.francofernando.com/p/recursion-in-practice-iteration-and)
- [ ] [Roadmap: Vectorization](https://cvw.cac.cornell.edu/vector)
- [ ] [Designing a SIMD Algorithm from Scratch](https://mcyoung.xyz/2023/11/27/simd-base64/)

## Languages / Go

### Concepts

- [ ] Go performance optimization

### Posts

- [ ] [Go Optimization Guide](https://goperf.dev/)

## Career

### Books

- [ ] Radical Candor — Kim Scott
- [ ] Crucial Conversations — Kerry Patterson

## Practices

### Concepts

- [ ] Design by Contract
- [ ] Error handling paradigms
- [ ] Parse, don't validate
- [ ] Test-driven development
- [ ] Architecture decision records
    - [Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)

### Books

- [ ] Code Complete — Steve McConnell
- [ ] Object-Oriented Software Construction — Bertrand Meyer
- [ ] The Pragmatic Programmer — Andrew Hunt, David Thomas
- [ ] Fundamentals of Software Architecture — Mark Richards, Neal Ford
