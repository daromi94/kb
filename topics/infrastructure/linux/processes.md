# Processes

A process is a kernel construct. It exists as a task_struct in
kernel memory — the data structure that holds the process's state,
memory mappings, open file descriptors, scheduling info, and
credentials.

## Creation

New processes are created via the `fork()` or `clone()` system
calls. The kernel duplicates the parent's page tables using
**copy-on-write**: physical memory pages are shared read-only
between parent and child. A page is copied only when one process
writes to it. File descriptor tables are also copied, giving the
child its own set of descriptors pointing to the same open files.

## Virtual address space

Each process gets its own virtual address space. The Memory
Management Unit (MMU) translates virtual addresses to physical
RAM using the process's page tables. This hardware-enforced
isolation means Process A cannot read or write Process B's
memory.

## Scheduling

The kernel uses preemptive multitasking to share CPU cores among
all runnable processes. The EEVDF (Earliest Eligible Virtual
Deadline First) scheduler assigns time slices and switches the
CPU state between processes thousands of times per second. From
the user's perspective, hundreds of processes appear to run
simultaneously.

## The /proc filesystem

`/proc` is a pseudo-filesystem with no on-disk storage. The
kernel generates its contents dynamically, exposing internal data
structures as files. Each process gets a `/proc/<pid>/` directory
containing its memory maps, open file descriptors, status, and
more.

```
ps aux      # reads from /proc to list all processes
ls /proc/1/ # inspect init's kernel-exposed state
```

## Related

- [User and kernel space](user-and-kernel-space.md) - The
  privilege boundary processes operate within

---

Return to [Linux](_index.md)
