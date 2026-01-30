# SO_PEERCRED

With TCP, you know only the source IP. With UDS, the kernel knows exactly who
is on the other end.

## What It Provides

The receiving process can retrieve peer credentials via `getsockopt()`:

```c
struct ucred cred;
socklen_t len = sizeof(cred);
getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &len);

printf("PID: %d, UID: %d, GID: %d\n", cred.pid, cred.uid, cred.gid);
```

| Field | Description              |
|-------|--------------------------|
| pid   | Process ID of peer       |
| uid   | User ID of peer          |
| gid   | Primary group ID of peer |

## Zero-Trust Local Authentication

This enables authentication without passwords or tokens:

```c
if (cred.uid == 0) {
    // Caller is root, grant full access
} else if (cred.uid == allowed_uid) {
    // Caller is authorized user
} else {
    // Reject connection
}
```

**Unforgeable:** The kernel fills in these values. A process cannot lie about
its uid or pid.

## Real-World Uses

**Docker daemon:**
When you run `docker ps`, the CLI connects to `/var/run/docker.sock`. The
daemon checks if your uid has permission (root or docker group).

**sudo:**
Verifies the calling process credentials before privilege escalation.

**D-Bus:**
System bus uses peer credentials to enforce security policies on which
processes can call which methods.

**polkit:**
Authorization framework checks caller uid/pid to decide if an action (like
mounting a disk) is allowed.

## Compared to TCP Authentication

| Aspect      | TCP                          | UDS with SO_PEERCRED    |
|-------------|------------------------------|-------------------------|
| Identity    | IP address (spoofable)       | Kernel-verified UID/PID |
| Auth method | TLS certs, tokens, etc.      | None needed             |
| Forgery     | Possible with network access | Impossible              |
| Scope       | Network-wide                 | Same host only          |

## Limitations

- Linux-specific (BSD has similar but different mechanisms)
- Only provides UID, GID, PID—not full user context
- Credentials captured at connect time; if process changes uid later, stale

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [SCM_RIGHTS](scm-rights.md) - The other UDS-only feature
