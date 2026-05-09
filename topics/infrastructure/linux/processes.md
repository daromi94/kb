# Processes

A process is a program in execution — code loaded into memory,
assigned resources, and given CPU time. In the kernel it exists
as a task_struct — the data structure that holds the process's
state, memory mappings, open file descriptors, scheduling info,
and credentials.

## Creation

New processes are created via the `fork()` or `clone()` system
calls. The kernel duplicates the parent's page tables using
**copy-on-write**: physical memory pages are shared read-only
between parent and child. A page is copied only when one process
writes to it. File descriptor tables are also copied, giving the
child its own set of descriptors pointing to the same open files.

The child typically calls `exec()` to replace its memory image
with a new program.

## States

The kernel tracks each process in one of several states:

| State      | Flag | Meaning                                      |
|------------|------|----------------------------------------------|
| Running    | R    | On CPU or in the run queue                   |
| Sleeping   | S    | Waiting for an event, can be interrupted     |
| Disk sleep | D    | Waiting for I/O, cannot be interrupted       |
| Stopped    | T    | Suspended by signal                          |
| Zombie     | Z    | Exited but parent has not read its exit code |

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

## Observing processes

| Tool           | Purpose                                       |
|----------------|-----------------------------------------------|
| `ps aux`       | Snapshot of all processes                     |
| `top` / `htop` | Real-time process activity and resource usage |
| `pstree`       | Parent-child hierarchy                        |
| `/proc/<pid>/` | Kernel-exposed per-process state              |

`/proc` is a pseudo-filesystem with no on-disk storage. The
kernel generates its contents dynamically, exposing internal data
structures as files.

---

Return to [Linux](_index.md)
