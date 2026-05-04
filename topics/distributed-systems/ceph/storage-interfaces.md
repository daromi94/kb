# Storage interfaces

Ceph provides three distinct storage interfaces running on top of the same
underlying RADOS cluster. This allows a single infrastructure to handle diverse
workloads simultaneously.

## Block storage (RBD)

The **RADOS Block Device** provides virtual disks attachable to bare-metal
servers, virtual machines, or containers.

Ceph stripes a block device image across multiple objects in the RADOS cluster.
To the operating system, it appears as a standard SCSI or local disk.

**Features:**

- Snapshots and cloning (copy-on-write)
- Thin provisioning (consumes space only when written)
- Optimized for low-latency random I/O

**Use cases:** Root disks for VMs (OpenStack, KVM/Proxmox), Persistent Volumes
for Kubernetes.

## Object storage (RGW)

The **RADOS Gateway** provides a RESTful interface compatible with Amazon S3 and
OpenStack Swift APIs.

It translates S3/Swift API calls into RADOS operations. Data is stored as
objects with associated metadata.

**Features:**

- Multisite replication for disaster recovery
- Bucket policies and object versioning
- No directory hierarchy bottlenecks

**Use cases:** Media files, long-term backups, data lakes, web application
assets.

## File storage (CephFS)

**CephFS** is a POSIX-compliant file system providing a shared, distributed
directory tree.

It uses Metadata Servers (MDS) to manage the file hierarchy while actual file
contents are stored as objects in RADOS.

**Features:**

- Multiple clients mount simultaneously (like NFS but distributed)
- Scalable metadata via multiple MDS daemons
- Directory quotas

**Use cases:** Shared home directories, HPC scratch space, shared storage for
containerized applications.

## Comparison

| Feature         | Block (RBD)          | Object (RGW)         | File (CephFS)        |
|-----------------|----------------------|----------------------|----------------------|
| Access method   | Kernel module/librbd | REST API (S3/Swift)  | POSIX mount/NFS/FUSE |
| Unit of storage | Block (virtual disk) | Object (file + meta) | File/directory       |
| Shared access   | No (single host)     | Yes (global)         | Yes (multiple hosts) |
| Performance     | Low latency          | High throughput      | Balanced             |

## Related

- [RADOS architecture](rados.md) - The underlying storage layer
- [CephFS vs NFS](cephfs-vs-nfs.md) - When to use each

---

Return to [Ceph](_index.md)
