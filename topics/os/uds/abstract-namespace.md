# Abstract Namespace

A Linux-specific feature that solves the UDS cleanup problem.

## The Problem with Normal UDS

Normal Unix sockets create a file on disk:

```c
struct sockaddr_un addr;
addr.sun_family = AF_UNIX;
strcpy(addr.sun_path, "/tmp/app.sock");
bind(fd, &addr, sizeof(addr));  // Creates /tmp/app.sock
```

**Crash scenario:**
1. Server binds to `/tmp/app.sock`
2. Server crashes without calling `unlink()`
3. File remains on disk
4. Server restarts, `bind()` fails with `EADDRINUSE`

**Common workaround:** Always `unlink()` before `bind()`. But this is error-prone
and creates race conditions.

## The Abstract Namespace Solution

If the first byte of `sun_path` is a null byte (`\0`), the socket exists only
in kernel memory:

```c
struct sockaddr_un addr;
addr.sun_family = AF_UNIX;
addr.sun_path[0] = '\0';
strcpy(addr.sun_path + 1, "app.sock");
bind(fd, &addr, sizeof(addr));  // No file created
```

**Properties:**
- No filesystem presence (no file to delete)
- Automatically disappears when socket closes
- No cleanup needed after crashes
- No permission issues from stale files

## Visibility

Abstract sockets appear in `netstat` and `ss` with an `@` prefix:

```bash
$ ss -x | grep abstract
u_str  LISTEN  @/tmp/dbus-XYZ123
```

## Real-World Uses

**D-Bus:**
The system and session message buses commonly use abstract sockets to avoid
filesystem cleanup issues.

**systemd:**
Uses abstract sockets for various internal communication channels.

## Trade-offs

| Aspect      | Filesystem Socket          | Abstract Socket          |
| ----------- | -------------------------- | ------------------------ |
| Cleanup     | Manual `unlink()` required | Automatic                |
| Permissions | File chmod/chown           | None (namespace-wide)    |
| Persistence | Survives process death     | Dies with last reference |
| Portability | POSIX (all Unix)           | **Linux only**           |
| Visibility  | `ls` shows file            | Only in ss/netstat       |

**Security note:** Abstract sockets cannot use filesystem permissions. Any
process can connect if it knows the name. Use `SO_PEERCRED` for access control.

## Related

- [Unix domain sockets](unix-domain-sockets.md) - UDS fundamentals
- [UDS lifecycle](uds-lifecycle.md) - The unlink/bind pattern
- [SO_PEERCRED](so-peercred.md) - Authentication for abstract sockets
