# io_uring

io_uring (Input/Output User Ring) is a high-performance asynchronous I/O
interface for the Linux kernel, introduced in version 5.1 (2019). Designed by
Jens Axboe to address bottlenecks of previous I/O models.

Instead of the traditional "syscall per operation" model, io_uring uses two
ring buffers in shared memory to submit requests and retrieve completions. This
drastically reduces system call overhead and memory copying.

## Architecture

Two circular buffers mapped into memory shared between user-space and kernel:

**Submission Queue (SQ):** Application writes I/O requests (Submission Queue
Entries, or SQEs) into this ring.

**Completion Queue (CQ):** Kernel writes results of completed operations
(Completion Queue Entries, or CQEs) into this ring.

Because these rings exist in shared memory (via `mmap`), both sides can
read/write without expensive data copying during context switches.

### The indirection layer

The Submission Queue is actually a ring of indices, not request structures:

- Application allocates an array of SQE structures
- The SQ Ring holds integers (indices) pointing to valid entries in that array
- Allows submitting requests in any order without moving large structures

## Lifecycle

### 1. Setup

Call `io_uring_setup()` to initialize. Kernel returns a file descriptor and
memory offsets needed to map the SQ and CQ rings into user space.

### 2. Submission

To perform I/O (read file, send network packet):

1. Get an empty SQE from the submission array
2. Fill the SQE with details: opcode (READ, WRITE, SEND), file descriptor,
   buffer address, etc.
3. Update the SQ tail index, pushing the request into the ring

### 3. Entering the kernel

The request is queued, but the kernel doesn't know yet. Call `io_uring_enter()`:

- Single system call can flush multiple requests from SQ to kernel (batching)
- Can also wait for completions in the same call

### 4. Completion

Kernel processes requests asynchronously (using DMA or kernel threads). When
done:

1. Kernel writes a CQE to the Completion Queue with result (bytes read) and
   `user_data` field (tag to identify the original request)
2. Kernel updates the CQ tail
3. Application reads CQE from head of Completion Queue

## Why it's fast

### Shared memory

Control structures (the rings) are zero-copy. App and kernel share the same
memory region without expensive border crossings.

**Buffer registration:** `IORING_REGISTER_BUFFERS` locks user-space memory
pages in RAM (pinning), so the kernel doesn't map/unmap them per request.
Enables true zero-copy data transfer.

### System call reduction

| Approach | 1000 file reads                           |
|----------|-------------------------------------------|
| Standard | 1000 `read()` syscalls, 1000 ctx switches |
| io_uring | 1000 SQEs, one `io_uring_enter()` call    |

### Polling mode

The most aggressive performance mode (`IORING_SETUP_SQPOLL`):

- Kernel starts a dedicated thread that continuously polls the Submission Queue
- When app adds an SQE, the kernel thread sees it immediately
- Application issues I/O without making a single system call
- Suitable for ultra-low latency, high-IOPS applications (HFT, databases)

## Code example

Using the `liburing` helper library:

```c
struct io_uring ring;
io_uring_queue_init(32, &ring, 0); // Setup ring with 32 entries

// 1. Get an SQE (Submission Queue Entry)
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);

// 2. Prepare a Read operation (equivalent to pread)
io_uring_prep_read(sqe, fd, buffer, buffer_size, offset);

// 3. Submit the request
io_uring_submit(&ring); // Calls io_uring_enter()

// 4. Wait for completion
struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);

// 5. Check result
if (cqe->res < 0) {
    fprintf(stderr, "Async read failed: %s\n", strerror(-cqe->res));
}

// 6. Mark completion as seen
io_uring_cqe_seen(&ring, cqe);
```

## Capabilities

io_uring has evolved into a general-purpose async execution mechanism:

- **Network I/O:** send, recv, accept, connect
- **File I/O:** read, write, fsync, fallocate
- **Time:** Asynchronous timeouts and timers
- **Chaining:** Link requests (read file, then send to socket). If read fails,
  send is automatically cancelled.

## Related

- [Shared memory](shared-memory.md) - The IPC technique underlying io_uring
- [Zero copy](zero-copy.md) - Avoiding CPU data copying
- [Proactor vs reactor](proactor-vs-reactor.md) - io_uring vs epoll models
