# Zero copy

Zero copy allows moving data from one place to another (file on disk to network
card) without the CPU copying that data into application memory.

Tells the OS: "I don't need to see or touch this data; just move it from Point
A to Point B."

## The standard way

Web server sending a file to a client:

1. **Disk to Kernel:** OS reads file into Kernel Buffer (RAM owned by OS)
2. **Kernel to App (Copy #1):** OS copies data into Application's memory buffer
3. **App to Kernel (Copy #2):** Application calls `send()`, copying data back
   into Socket Buffer (RAM owned by OS)
4. **Kernel to Network Card:** OS sends from Socket Buffer to Network Card

Steps 2 and 3 are wasteful if the app isn't modifying the file.

## The zero copy way

1. **Disk to Kernel:** OS reads file into Kernel Buffer
2. **Kernel to Network Card:** Application tells OS to send data directly from
   Kernel Buffer to Network Card

Data never enters Application memory. CPU doesn't waste time copying. Copy
count drops to zero.

## Linux implementations

**`sendfile()`:** The most famous zero copy call. "Take file descriptor A (the
file) and copy it to file descriptor B (the socket)." How Nginx and Netflix
serve static files quickly.

**`mmap()`:** Maps a file directly into memory space. Reading a variable in
code actually reads the kernel's file cache directly. Avoids the read copy.

**`splice()`:** Moves data between two file descriptors (pipe and socket)
entirely within the kernel, without passing through user space.

## Connection to io_uring

io_uring supports zero copy through registered buffers:

- Pre-register buffers to lock memory pages in place
- Kernel accesses them directly via DMA without mapping/unmapping
- Creates zero copy path for the operation itself

## Summary

| Approach  | Data flow                 | CPU usage |
|-----------|---------------------------|-----------|
| Standard  | Kernel -> User -> Kernel  | High      |
| Zero copy | CPU manages pointers only | Low       |

**Best use case:** Sending large files (video streaming, static web servers)
where the application acts as a dumb pipe and doesn't modify the data.

## Related

- [io_uring](io-uring.md) - Supports registered buffers for zero copy
- [Shared memory](shared-memory.md) - Related IPC optimization
