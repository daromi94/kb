# File descriptors

A file descriptor (FD) is a non-negative integer that a process uses
to access an I/O resource. It acts as an index into a per-process
table managed by the kernel. Because Linux abstracts almost all I/O
as byte streams, the same system calls (`read()`, `write()`,
`close()`) work whether the FD refers to a file on disk, a terminal,
a pipe, or a network socket.

## Standard file descriptors

Every new process inherits three open descriptors:

| FD | Name   | Purpose         |
|----|--------|-----------------|
| 0  | stdin  | Standard input  |
| 1  | stdout | Standard output |
| 2  | stderr | Standard error  |

Shell redirection changes what a descriptor points to. `cmd > out.txt`
makes FD 1 refer to `out.txt` instead of the terminal.

## Kernel data structures

When a process reads or writes through an FD, the kernel navigates
three layers:

```
Per-process FD table --> Open file table --> Inode table
(private per process)    (system-wide)       (on-disk metadata)
```

**Per-process FD table.** Each process has its own table. FD 3 in
one process may point to a completely different file than FD 3 in
another.

**Open file table.** Shared across the system. Each entry tracks the
current file offset and access mode (read-only, write-only,
read-write). Two FDs — even in different processes — can share the
same open file table entry and therefore share the same offset.

**Inode table.** Contains on-disk metadata: permissions, size, and
the locations of data blocks. Multiple open file table entries can
reference the same inode.

## Creation

System calls that return new file descriptors:

- `open()` — opens a file on disk
- `socket()` — creates a network endpoint
- `pipe()` — creates a pair of connected FDs for IPC
- `accept()` — returns an FD for a new client connection
- `dup()` / `dup2()` — duplicates an existing FD

The kernel always assigns the lowest available integer. Once
returned, the process operates on the FD without needing the
original filename or address.

## Inheritance across fork

`fork()` copies the parent's FD table. The child gets its own set of
descriptors, but each points to the same open file table entry as the
parent. Parent and child therefore share the file offset — writes by
one advance the position for both.

## Observing file descriptors

`ls -l /proc/<pid>/fd` lists every open descriptor for a process.
Each entry is a symlink showing what the FD currently refers to
(e.g., `/dev/pts/0` for a terminal, `socket:[12345]` for a network
connection).

## Related

- [Processes](processes.md) - FDs live inside the per-process
  task_struct and are copied on fork

---

Return to [Linux](_index.md)
