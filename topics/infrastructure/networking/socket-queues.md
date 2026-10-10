# Socket queues

Every established TCP socket in Linux has kernel-managed buffering that allows an application and the network to operate at different speeds.

There are two fundamental directions:

- Receive side (RX): Holds incoming data until the application consumes it with `recv()` or `read()`.
- Send side (TX): Holds outgoing data while TCP manages transmission, acknowledgments, and retransmissions.

The key principle is:

> Socket buffering decouples application execution from network transmission. Applications do not need to read or write at exactly the rate the network delivers data.

These buffers also play a central role in flow control, backpressure, blocking I/O, memory consumption, and TCP performance.

The explanation focuses on TCP sockets, because UDP has different queueing semantics.

## 1. The big picture

Consider two processes communicating over TCP.

```text
              MACHINE A                         MACHINE B

            Application                       Application
                 |                                 ^
                 | send()                          | recv()
                 v                                 |
       +-------------------+             +-------------------+
       | TCP Send Buffer   |             | TCP Receive Buffer|
       |                   |             |                   |
       | Outgoing data     |             | Incoming data     |
       +---------+---------+             +---------+---------+
                 |                                 ^
                 v                                 |
       +-------------------+             +-------------------+
       | TCP / IP Stack    |             | TCP / IP Stack    |
       +---------+---------+             +---------+---------+
                 |                                 ^
                 v                                 |
       +-------------------+             +-------------------+
       | NIC TX Ring       |             | NIC RX Ring       |
       +---------+---------+             +---------+---------+
                 |                                 ^
                 v                                 |
                NIC --------- Network ----------- NIC
```

Notice that there are multiple buffering layers:

1. Application buffers in user space.
2. TCP socket buffers in kernel space.
3. Packet queues in the Linux networking stack.
4. NIC descriptor rings and associated DMA buffers.

These are not the same queues.

A NIC RX ring holds descriptors for receiving packets from hardware. A TCP receive queue holds data associated with a particular TCP connection that the kernel can eventually deliver to the application.

This distinction matters when diagnosing network performance.

## 2. The receive queue (RX)

The receive side buffers incoming data that the application has not yet consumed.

Suppose a server receives 12 KB over a TCP connection while its application is temporarily busy.

```text
                  NETWORK
                     |
                     | 12 KB received
                     v
              +-------------+
              |     NIC     |
              +------+------+
                     |
                     v
              +-------------+
              | TCP Stack   |
              +------+------+
                     |
                     v
        +--------------------------+
        | TCP Receive Buffer       |
        |                          |
        | [4 KB][4 KB][4 KB]       |
        |                          |
        | 12 KB awaiting recv()    |
        +------------+-------------+
                     |
                     | Application not reading
                     X
                     |
                 Application
```

The data can remain in the kernel even though the application is not currently executing `recv()`.

That is an important property of sockets: the application does not have to be actively reading when the packets arrive.

### What happens when recv() is called?

Suppose the application calls:

```c
char buffer[8192];

ssize_t n = recv(fd, buffer, sizeof(buffer), 0);
```

Assume 12 KB of readable data is available, and this particular call returns 8,192 bytes.

```text
BEFORE recv()

TCP Receive Buffer
+--------------------------+
| 4 KB | 4 KB | 4 KB       |
+--------------------------+
        12 KB available


            |
            | recv(fd, buf, 8192, 0)
            v


AFTER recv()

TCP Receive Buffer         Application Memory
+----------------+         +------------------+
|     4 KB       |         |      8 KB        |
+----------------+         +------------------+

4 KB remaining             8 KB consumed
```

In the conventional receive path, `recv()` copies available bytes from kernel-managed TCP data into the supplied user-space buffer.

However, TCP does not guarantee that this call returns exactly 8 KB. By default, `recv()` may return fewer bytes if that is what is available when the operation completes.

### Is the receive queue a FIFO?

Conceptually, yes, for application-visible TCP data.

TCP delivers an ordered byte stream:

```text
Data sent by peer

A B C D E F G H
        |
        v
TCP Receive Stream

A B C D E F G H
        |
        v
Application reads

A B C D ...
```

However, Linux's internal structures are more sophisticated than a single FIFO byte array.

In particular, network packets may arrive out of order.

## 3. What happens when packets arrive out of order?

Suppose TCP expects these segments:

```text
Segment A: bytes 0-999
Segment B: bytes 1000-1999
Segment C: bytes 2000-2999
```

But the network delivers them in this order:

```text
Arrival order

A
|
v
C
|
v
B
```

TCP cannot normally deliver segment C's bytes to the application before segment B's missing bytes.

Linux maintains internal state for this situation.

```text
               TCP RECEIVE PROCESSING
                         |
                         v
                 Incoming segment
                         |
                         v
               Is it in sequence?
                   /         \
                 Yes          No
                  |            |
                  v            v
         +---------------+  +------------------+
         | Receive Queue |  | Out-of-Order     |
         |               |  | Queue            |
         | Readable data |  |                  |
         +---------------+  | Missing earlier  |
                            | bytes            |
                            +------------------+
```

After B arrives, the contiguous byte sequence can be made available to the application.

Linux exposes relevant internal structures such as:

- `sk_receive_queue`: Queue for received socket data.
- `out_of_order_queue`: TCP's structure for segments that arrive ahead of missing data.
- `sk_backlog`: Additional per-socket backlog used in certain concurrency and socket-locking situations.

These are kernel implementation details, not three independently configurable application queues. Recent Linux implementations use an RB-tree for the TCP out-of-order queue.

## 4. What happens when the receive buffer fills?

This is where socket buffering becomes particularly interesting.

Suppose the receiving application processes incoming data slowly.

```text
        Sender                       Receiver

     send() continuously
           |                            |
           v                            v
       +-------+                +----------------+
       | TCP   |  ----------->  | Receive Buffer |
       +-------+                |                |
                                | ############## |
                                | ############## |
                                |      FULL      |
                                +-------+--------+
                                        |
                                        v
                                  Slow application
```

Eventually, the receiver cannot continue accepting data at the previous rate.

TCP solves this using receive-window-based flow control.

### TCP receive window

The receiver advertises how much additional data it is currently prepared to accept.

For example, consider a simplified 64 KB receive capacity.

```text
              RECEIVER CAPACITY: 64 KB

   +------------------------------------------+
   |        48 KB       |       16 KB         |
   |    Buffered data   |   Available space   |
   +------------------------------------------+

                        |
                        v

             Advertised window: ~16 KB
```

The sender uses the advertised window to restrict how much unacknowledged data may occupy the receiver's available sequence space.

This is simplified: real Linux window advertisement also accounts for internal memory overhead, window scaling, and algorithms that avoid advertising inefficiently small windows.

As the receive buffer fills, the advertised window can shrink.

When the receiver has no additional room, it can advertise a zero window.

```text
       RECEIVER                      SENDER

   Receive buffer full
            |
            v
   Advertise window = 0  ----------> Stop sending
                                     new data
            |
      Application recv()
            |
            v
      Space becomes
      available
            |
            v
   Advertise larger window --------> Resume sending
                                     permitted data
```

The sender can still retransmit data when needed and periodically probe a zero window.

This is a form of transport-level backpressure.

One particularly important detail: a TCP acknowledgment does not mean the receiving application has read the data. The receiver can acknowledge bytes already accepted into its TCP state while the application has not yet consumed them.

## 5. The send queue (TX)

Now consider the opposite direction.

The send side manages data submitted by an application that TCP has not yet finished handling.

Suppose:

```c
send(fd, data, 65536, 0);
```

The application submits 64 KB for transmission.

In the ordinary copying path, Linux copies the accepted bytes into kernel-managed storage and tracks them as part of the TCP socket's outgoing data.

```text
   APPLICATION
       |
       | send(fd, data, 65536, 0)
       v
+--------------+
| TCP Send     |
| Buffer       |
|              |
|   64 KB      |
+------+-------+
       |
       | TCP transmission
       v
+--------------+
| IP / NIC     |
+------+-------+
       |
       v
    NETWORK
```

There is a crucial difference between send and receive buffering:

Data on the send side can remain accounted to the socket even after it has been transmitted.

Why?

Because TCP must retain enough information to retransmit unacknowledged data if necessary.

### The send side has multiple logical states

Consider a simplified example involving 100 KB of data.

```text
               TCP OUTGOING DATA: 100 KB

  +----------------+----------------+----------------+
  |     40 KB      |     30 KB      |     30 KB      |
  |                |                |                |
  | Acknowledged   | Transmitted    | Not yet        |
  |                | Unacknowledged | transmitted    |
  +----------------+----------------+----------------+
          |                |                |
          v                v                v
     Can release       Retain for        Waiting for
     TCP send state    retransmission    permission/
                                         opportunity
                                         to transmit
```

The 40 KB already acknowledged can be released from the corresponding send-side tracking.

The remaining 60 KB still requires TCP state and potentially buffering.

Linux has internal structures for this, including a write queue for data awaiting transmission and a retransmission queue for sent data awaiting acknowledgment. The latter is implemented using an RB-tree in current Linux TCP code.

This distinction is important:

- Unsent data: Has been accepted from the application but has not yet been transmitted.
- Unacknowledged data: Has been transmitted, but TCP has not received the corresponding acknowledgment.

Both can contribute to send-side resource usage, although their accounting and lifecycles differ.

## 6. What happens when the send buffer fills?

Suppose an application generates data at 100 MB/s, but TCP can only make progress at 20 MB/s.

```text
     APPLICATION             TCP SEND SIDE           NETWORK

       100 MB/s
          |
          v
   +--------------+
   | send()       |
   +------+-------+
          |
          v
   +--------------+
   | Send Buffer  |
   |              |
   | ##########   | ---------> 20 MB/s
   | ##########   |
   | ##########   |
   +--------------+
          |
          v
    Eventually full
```

If that imbalance persists, the finite send buffer eventually reaches its capacity.

What happens next depends on whether the socket is blocking.

### Blocking socket

```c
send(fd, data, size, 0);
```

If there is insufficient space, the calling thread can block waiting for TCP to make progress and free resources.

A large send may accept some bytes and return a partial count instead of accepting the entire requested amount.

### Non-blocking socket

```c
send(fd, data, size, MSG_DONTWAIT);
```

If no data can currently be accepted, it returns `-1` with `errno` set to `EAGAIN` or `EWOULDBLOCK`.

```text
                 send()
                    |
                    v
           Send space available?
               /         \
             Yes          No
              |            |
              v            v
         Accept bytes   Blocking socket?
                            /       \
                          Yes        No
                           |          |
                           v          v
                         Wait      EAGAIN
```

This is local backpressure: the kernel prevents an application from submitting unlimited bytes into finite socket memory.

## 7. How receive and send queues interact

Now the interesting part: TCP's receive and send sides are connected through flow control.

Consider a fast producer communicating with a slow consumer.

```text
           MACHINE A                         MACHINE B

         Fast producer                     Slow consumer
              |                                 ^
              | send()                          | recv()
              v                                 |
      +-----------------+               +-----------------+
      | TCP Send Buffer |               | TCP Recv Buffer |
      |                 |               |                 |
      | Accumulating    |               | Filling up      |
      | outgoing data   |               |                 |
      +--------+--------+               +--------+--------+
               |                                 ^
               |                                 |
               +------------ TCP ----------------+
```

The system can exhibit a chain reaction:

1. The receiving application slows down. Incoming data accumulates in its TCP receive buffer.
2. The receiver advertises a smaller TCP window. The sender is permitted to transmit less additional data.
3. The sender accumulates unsent data. Its send-side resource usage increases as the producing application continues calling `send()`.
4. The sender's buffer eventually fills. Blocking writes wait, or non-blocking writes report that they cannot currently progress.
5. The producing application must slow down. Otherwise, it might merely move the backlog into its own application-level queues.

This is one of the most important examples of end-to-end backpressure in networking.

However, TCP flow control is not the only restriction on sending.

### Receive window vs congestion window

TCP has two major constraints on the amount of outstanding data:

| Constraint                 | What it protects           |
| -------------------------- | -------------------------- |
| Receive window (`rwnd`)    | Receiver capacity          |
| Congestion window (`cwnd`) | Network congestion control |

Conceptually, the sender's allowed amount of in-flight data is constrained by:

```text
In-flight limit <= min(rwnd, cwnd)
```

The actual transmission decision also depends on outstanding bytes, pacing, and other TCP algorithms.

A socket may therefore contain plenty of unsent data even when the receiver has sufficient buffer space, because congestion control is restricting transmission.

## 8. Socket buffer limits and memory accounting

Linux allows applications and administrators to configure socket-buffer limits.

Two important socket options are:

```text
SO_RCVBUF   // Receive buffer size
SO_SNDBUF   // Send buffer size
```

For example:

```c
int size = 1024 * 1024;

setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &size, sizeof(size));

setsockopt(fd, SOL_SOCKET, SO_SNDBUF, &size, sizeof(size));
```

This requests larger buffer limits, subject to system restrictions.

Important: These values do not mean Linux reserves one contiguous 1 MB array for each buffer.

Socket data is associated with kernel packet buffers and metadata, and Linux accounts for their memory consumption. Actual memory allocation can grow or shrink with usage.

Linux also doubles requested `SO_RCVBUF` and `SO_SNDBUF` values for its bookkeeping conventions, and `getsockopt()` reports the doubled value.

### TCP buffer autotuning

Linux supports automatic adjustment of TCP buffers.

Relevant parameters include:

```bash
# TCP receive buffer: min, default, max
sysctl net.ipv4.tcp_rmem

# TCP send buffer: min, default, max
sysctl net.ipv4.tcp_wmem

# Receive buffer autotuning
sysctl net.ipv4.tcp_moderate_rcvbuf
```

The exact defaults depend on the kernel and system configuration.

Explicitly setting socket buffer sizes can override automatic sizing behavior for that socket, so manually assigning a large value is not automatically a performance improvement.

## 9. Inspecting the queues with ss

Linux exposes socket queue information through `ss`.

```bash
ss -tn
```

An illustrative output:

```text
State  Recv-Q  Send-Q  Local Address:Port   Peer Address:Port
ESTAB  32768   0       10.0.0.10:8080       10.0.0.2:51000
ESTAB  0       65536   10.0.0.10:8080       10.0.0.3:52000
```

For established TCP sockets:

- Recv-Q: Bytes received that the application has not yet consumed.
- Send-Q: Outstanding TCP bytes not yet acknowledged, including data pending transmission.

The first connection has 32 KB awaiting application consumption.

The second connection has 64 KB outstanding on the send side.

Neither value is the same thing as the socket's configured buffer-memory limit.

For more detailed information:

```bash
ss -tinm
```

The `-m` option exposes socket memory accounting, including `rmem_alloc`, `rcv_buf`, `wmem_queued`, and `snd_buf`, while `-i` displays additional TCP state.

### An important exception: listening sockets

For a socket in `LISTEN` state, `ss` uses different queue semantics.

```text
State   Recv-Q  Send-Q  Local Address:Port
LISTEN  4       128     0.0.0.0:8080
```

Here:

- `Recv-Q = 4`: Established connections waiting to be accepted.
- `Send-Q = 128`: Configured maximum accept-backlog length.

These are connection counts, not buffered application data bytes.

The accept queue is separate from the receive queue of an established connection.

## 10. What about UDP?

UDP sockets also have send and receive buffering, but their behavior differs from TCP.

UDP preserves datagram boundaries.

```text
                UDP RECEIVE SIDE

   Network
      |
      +------ Datagram A -----+
      |                       |
      +------ Datagram B -----+
      |                       v
      +------ Datagram C ---> +-------------------+
                              | UDP Receive Queue |
                              |                   |
                              | [A] [B] [C]       |
                              +---------+---------+
                                        |
                                    recvfrom()
```

Each successful receive ordinarily retrieves one datagram, not an arbitrary slice of an ordered TCP byte stream.

If the UDP receive queue runs out of capacity, incoming datagrams can be dropped.

UDP has no built-in TCP-style advertised receive window that automatically forces a remote sender to slow down.

This makes application-level rate control and backpressure especially important for high-volume UDP-based protocols.

## 11. Putting all the queues together

The complete architecture is worth visualizing once more.

```text
   SENDING MACHINE

   +---------------------------------------+
   | User Space                            |
   |                                       |
   | Application                           |
   |    |                                  |
   |    | send()                           |
   +----|----------------------------------+
        |
        v
   +---------------------------------------+
   | Kernel Space                          |
   |                                       |
   | TCP Send Buffer / Queues              |
   |    |                                  |
   |    | TCP chooses data to transmit     |
   |    v                                  |
   | Network stack / TX scheduling         |
   |    |                                  |
   |    v                                  |
   | NIC TX Descriptors                    |
   +----|----------------------------------+
        |
        v
   +---------------------------------------+
   | NIC Hardware                          |
   +----|----------------------------------+
        |
        v
      NETWORK
        |
        v
   +---------------------------------------+
   | NIC Hardware                          |
   +----|----------------------------------+
        |
        v
   +---------------------------------------+
   | Kernel Space                          |
   |                                       |
   | NIC RX Descriptors                    |
   |    |                                  |
   |    v                                  |
   | NAPI / IP / TCP processing            |
   |    |                                  |
   |    v                                  |
   | TCP Receive Queues                    |
   +----|----------------------------------+
        |
        | recv()
        v
   +---------------------------------------+
   | User Space                            |
   |                                       |
   | Application                           |
   +---------------------------------------+

   RECEIVING MACHINE
```

This also explains why a packet may be delayed in several places independently:

- The sender's socket waiting for TCP to transmit it.
- The Linux egress networking queues.
- The NIC's transmit queues.
- The network itself.
- The receiver's kernel waiting for the application to read it.

Each stage has different resource limits and different mechanisms for managing overload.

## 12. Essential engineering lessons

The most important conclusions:

1. Socket queues decouple application execution from network execution. A process can receive data while not actively reading, and it can submit data before transmission completes.
2. The send buffer is not simply a queue of packets awaiting NIC transmission. TCP must also maintain information about unacknowledged data for retransmission.
3. The receive queue and TCP receive window are related but distinct. One concerns buffered application data; the other describes how much additional data the peer may send.
4. Buffering absorbs bursts but does not create throughput. Larger buffers may improve utilization under some conditions, but they cannot fix persistent overload.
5. TCP supplies transport-level backpressure, not complete application-level backpressure. An application that copies pending work into an unbounded user-space queue can still run out of memory.
6. NIC descriptor rings, socket buffers, and application queues are different layers. Diagnosing latency or packet loss requires identifying which one is accumulating work.

The deeper systems principle: Socket buffers are bounded queues between independently progressing components. TCP adds flow control and congestion control to regulate that flow, but the system still needs disciplined application-level handling of bounded capacity.
