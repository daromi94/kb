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

## Capabilities

io_uring has evolved into a general-purpose async execution mechanism:

- **Network I/O:** send, recv, accept, connect
- **File I/O:** read, write, fsync, fallocate
- **Time:** Asynchronous timeouts and timers
- **Chaining:** Link requests (read file, then send to socket). If read fails,
  send is automatically cancelled.

---

Return to [Async I/O](_index.md)
