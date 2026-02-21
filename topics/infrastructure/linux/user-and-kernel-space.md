# User and kernel space

The CPU enforces two privilege levels that separate user programs
from the kernel. On x86, Ring 0 (kernel mode) has full hardware
access while Ring 3 (user mode) is restricted. Linux uses only
these two rings.

## System calls

A user-space program cannot touch hardware directly. To perform
a privileged operation — writing a file, sending a packet,
allocating memory — it must issue a **system call**. The syscall
triggers a trap that transitions the CPU from Ring 3 to Ring 0,
handing control to the kernel. The kernel performs the operation
on the process's behalf, then returns to user mode.

## Observing the boundary

`strace` intercepts system calls made by a process, showing every
crossing from user space into the kernel:

```
strace -c ls # summary of syscalls used by ls
```

## Related

- [Processes](processes.md) - The kernel-side construct that
  represents a running program

---

Return to [Linux](_index.md)
