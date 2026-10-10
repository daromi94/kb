# Sockets

A socket is an operating-system abstraction that provides an endpoint for communication between processes.

In Linux, sockets are the primary programming interface for communicating over TCP/IP networks, but they also support communication between processes running on the same machine.

The fundamental idea is:

> An application does not interact directly with TCP, UDP, IP, or a network interface. Instead, it operates on a socket, and the Linux kernel handles the underlying communication.

This abstraction is defined by the BSD sockets API, implemented by Linux, and documented in socket(7) and socket(2).

## 1. Why do sockets exist?

Consider two processes running on different machines.

```text
Machine A                           Machine B

+-------------------+              +-------------------+
|     Process A     |              |     Process B     |
|                   |              |                   |
|    Application    |              |    Application    |
+-------------------+              +-------------------+
         |                                   |
         v                                   v
+-------------------+              +-------------------+
|   Linux Kernel    |              |   Linux Kernel    |
|                   |              |                   |
|    TCP / UDP      |              |    TCP / UDP      |
|        IP         |              |        IP         |
|     Ethernet      |              |     Ethernet      |
+-------------------+              +-------------------+
         |                                   |
         +------------ Network --------------+
```

To exchange data, the processes need some way to ask their respective kernels to transmit and receive information.

An application could theoretically implement an entire networking stack, manage packet transmission, handle retransmissions, and deal with network hardware.

However, that would introduce enormous complexity.

Instead, Linux provides sockets.

```text
Application
    |
    | socket API
    |
    v
+-----------------------+
|     Linux Kernel      |
|                       |
|  Socket abstraction   |
|          |            |
|     TCP / UDP         |
|          |            |
|          IP           |
|          |            |
|    Network device     |
+-----------------------+
```

Sockets separate two responsibilities:

- Application: Decides what data to communicate and with whom.
- Kernel: Implements the relevant protocol, manages communication state, and transfers data.

Importantly, a socket is not necessarily a TCP connection. A socket can exist without any connection being established.

## 2. A socket is a file descriptor

One of the most important Linux concepts is that sockets are exposed through file descriptors.

Consider:

```c
int fd = socket(AF_INET, SOCK_STREAM, 0);
```

This creates a socket and returns a file descriptor.

For example:

```c
fd = 3;
```

The number `3` is not the socket itself.

It is an index into the process's file descriptor table.

Simplified Linux socket representation

Conceptual representation for a typical Linux networking socket. Kernel structures contain additional references and protocol-specific details.

Internally, Linux uses several structures:

| Structure       | Responsibility                                                     |
| --------------- | ------------------------------------------------------------------ |
| File descriptor | Integer used by a process to reference an open resource            |
| `struct file`   | Kernel open-file representation                                    |
| `struct socket` | Generic socket abstraction and protocol operations                 |
| `struct sock`   | Internal networking state, including protocol-specific information |

The relationships between `struct socket` and `struct sock` are described in the Linux kernel networking API documentation. The implementation connecting sockets and file descriptors appears in Linux net/socket.c.

### Why is this significant?

Because Linux exposes sockets as file descriptors, applications can operate on them using familiar system calls:

```c
read(fd, buffer, size);
write(fd, buffer, size);
close(fd);
```

Sockets also support specialized operations:

```c
send(fd, buffer, size, 0);
recv(fd, buffer, size, 0);
```

Unlike a regular file, a socket is connected to communication machinery managed by the kernel, not ordinary filesystem storage.

The same file-descriptor abstraction also allows applications to use `poll`, `epoll`, and other I/O mechanisms.

## 3. Creating a socket

The socket system call has three arguments:

```c
int socket(int domain, int type, int protocol);
```

Each one specifies an independent aspect of communication.

### Domain: Where does communication happen?

| Domain       | Meaning                                    |
| ------------ | ------------------------------------------ |
| `AF_INET`    | IPv4 networking                            |
| `AF_INET6`   | IPv6 networking                            |
| `AF_UNIX`    | Communication between local processes      |
| `AF_NETLINK` | Communication with Linux kernel subsystems |
| `AF_PACKET`  | Low-level access to network packets        |

For example, `AF_UNIX` sockets can be used for local IPC without sending traffic through an external network.

### Type: What communication semantics are required?

| Type             | Meaning                                                         |
| ---------------- | --------------------------------------------------------------- |
| `SOCK_STREAM`    | Ordered byte stream; typically TCP for IP sockets               |
| `SOCK_DGRAM`     | Message-oriented datagrams; typically UDP for IP sockets        |
| `SOCK_SEQPACKET` | Connection-oriented communication preserving message boundaries |
| `SOCK_RAW`       | Lower-level protocol access                                     |

### Protocol: Which protocol implementation?

For common combinations, `0` tells the kernel to select the default protocol.

Examples:

```c
// IPv4 TCP socket
socket(AF_INET, SOCK_STREAM, 0);

// IPv4 UDP socket
socket(AF_INET, SOCK_DGRAM, 0);

// Local Unix stream socket
socket(AF_UNIX, SOCK_STREAM, 0);
```

Notice that socket families and socket types are separate concepts.

For example, a Unix domain socket can also be `SOCK_STREAM`, even though it does not use TCP.

## 4. How TCP sockets work

Consider a TCP server accepting requests from clients.

There are two distinct roles: a listening socket and connected sockets.

### Server lifecycle

```text
socket()
   |
   v
bind()
   |
   v
listen()
   |
   v
accept()
   |
   v
recv() / send()
   |
   v
close()
```

The calls have different responsibilities:

| Call       | Responsibility                            |
| ---------- | ----------------------------------------- |
| `socket()` | Create the endpoint                       |
| `bind()`   | Associate it with a local address         |
| `listen()` | Enable acceptance of incoming connections |
| `accept()` | Obtain a new connected socket             |
| `recv()`   | Receive application data                  |
| `send()`   | Submit application data for transmission  |
| `close()`  | Close the file descriptor                 |

These operations are specified in the Linux manual pages for listen(2) and accept(2).

### The key distinction: listening socket vs connected socket

Suppose a server listens on:

```text
10.0.0.10:8080
```

Two clients connect:

```text
Client A: 10.0.0.2:53000
Client B: 10.0.0.3:55000
```

The server has three sockets:

1. One listening socket bound to port 8080.
2. One connected socket for Client A.
3. One connected socket for Client B.

A listening socket is not used to exchange the application data of individual accepted TCP connections.

Each successful `accept()` returns a new file descriptor representing a connected socket. The original listening socket remains available to accept more connections.

This is a foundational principle behind concurrent TCP servers.

### How can multiple sockets share port 8080?

Because a TCP connection is distinguished by a combination of values commonly called the four-tuple:

```text
(Source IP, Source Port, Destination IP, Destination Port)
```

For example:

```text
Connection A:
(10.0.0.2, 53000, 10.0.0.10, 8080)

Connection B:
(10.0.0.3, 55000, 10.0.0.10, 8080)
```

Both connections use the same server port but have different endpoint combinations.

For a conventional TCP connection, those values, together with the protocol and relevant network namespace, let Linux distinguish its networking state.

### When does the TCP handshake occur?

Typically, the client calls `connect()` and the kernel performs the TCP handshake:

```text
Client                                Server

   SYN --------------------------------->
       <------------------------- SYN-ACK
   ACK --------------------------------->

         TCP connection established
```

Linux can complete handshakes and queue established connections before the server application calls `accept()`.

The `listen()` backlog specifies a limit on the established connections waiting to be accepted, subject to kernel limits. Incomplete handshakes have separate handling.

## 5. How data moves through a socket

Consider a process sending 4 KB to a remote server over TCP.

```c
send(fd, buffer, 4096, 0);
```

Conceptually, the data follows this path:

```text
SENDING MACHINE

User space
+----------------------+
| Application          |
|                      |
| send(fd, buf, 4096)  |
+----------------------+
           |
           | System call
           v
Kernel space
+----------------------+
| Socket layer         |
| TCP send buffering   |
+----------------------+
           |
           v
+----------------------+
| TCP                  |
| Segmentation         |
| Retransmission       |
| Congestion control   |
+----------------------+
           |
           v
+----------------------+
| IP / Routing         |
+----------------------+
           |
           v
+----------------------+
| NIC / Driver         |
+----------------------+
           |
           v
        Network
```

On the receiving machine:

```text
        Network
           |
           v
+----------------------+
| NIC / Driver         |
+----------------------+
           |
           v
+----------------------+
| IP processing        |
| TCP processing       |
+----------------------+
           |
           v
+----------------------+
| Socket receive data  |
| and protocol state   |
+----------------------+
           |
           | recv()
           v
+----------------------+
| Application          |
+----------------------+
```

This is deliberately simplified: real Linux packet processing also involves routing decisions, packet queues, NIC offloads, NAPI, socket lookup, and other mechanisms.

### What does the socket actually store?

A TCP socket's kernel state includes information such as:

- Local and remote addresses.
- TCP connection state.
- Send and receive buffering.
- Sequence numbers and acknowledgment state.
- Flow-control and congestion-control information.
- Timers and error information.

Linux also uses `struct sk_buff` to represent packets internally. An `sk_buff` primarily stores packet metadata and references to associated data buffers, rather than containing all packet data directly.

### A crucial detail about send()

Suppose:

```c
send(fd, data, 4096, 0);
```

returns:

```text
4096
```

Does that mean the remote application received all 4,096 bytes?

No.

It means that the local socket operation accepted 4,096 bytes for transmission.

The kernel may still need to transmit them, wait for acknowledgments, or retransmit lost segments.

A successful `send()` does not guarantee that the remote application has received or processed the data.

## 6. TCP sockets are streams, not messages

This is one of the most common socket programming mistakes.

Suppose the sender performs two calls:

```c
send(fd, "HELLO", 5, 0);
send(fd, "WORLD", 5, 0);
```

It is incorrect to assume that the receiver will get exactly two corresponding reads.

The receiver might observe:

```text
recv() -> "HELLOWORLD"
```

Or:

```text
recv() -> "HEL"
recv() -> "LOW"
recv() -> "ORLD"
```

Or other partitions preserving the byte order.

TCP provides an ordered byte stream, not application message boundaries.

The application must define its own framing if it needs distinct messages, for example by using length prefixes or delimiters.

This behavior is documented in tcp(7).

## 7. UDP sockets are different

A UDP socket can send datagrams without establishing a TCP-style connection.

A typical UDP server does:

```text
socket()
   |
   v
bind()
   |
   v
recvfrom()
   |
   v
sendto()
```

UDP preserves datagram boundaries.

For example, if an application sends two datagrams:

```text
Datagram 1: HELLO
Datagram 2: WORLD
```

The receiver observes each successfully delivered datagram as an individual message, assuming an adequate receive buffer. They may be lost or arrive out of order, but they are not merged into one byte stream as TCP data would be.

| Property                  | TCP socket                           | UDP socket            |
| ------------------------- | ------------------------------------ | --------------------- |
| Connection setup          | Yes                                  | Not required          |
| Data abstraction          | Byte stream                          | Datagrams             |
| Reliable ordered delivery | Yes, while connection remains viable | No                    |
| Message boundaries        | Not preserved                        | Preserved             |
| Common API                | `send` / `recv`                      | `sendto` / `recvfrom` |

UDP sockets can also call `connect()`. For UDP, that primarily associates a default peer and filters incoming traffic; it does not establish a TCP-like reliable connection.

## 8. Blocking and non-blocking sockets

Sockets are closely related to Linux thread scheduling and asynchronous I/O.

Consider a blocking socket:

```c
char buffer[1024];

ssize_t n = recv(fd, buffer, sizeof(buffer), 0);
```

If no data is available, the calling thread can sleep until data arrives, an error occurs, or another wake-up condition applies.

The kernel does not normally consume a CPU core continuously while waiting for that data.

With non-blocking mode:

```c
fcntl(fd, F_SETFL, flags | O_NONBLOCK);
```

If no data is available, `recv()` returns `-1` and sets `errno` to `EAGAIN` or `EWOULDBLOCK`, instead of waiting.

This leads directly to event-driven networking.

```text
One application thread
          |
          v
       epoll_wait()
          |
          v
  +----------------+
  | Ready sockets  |
  +----------------+
     |     |     |
     v     v     v
    FD 5  FD 8  FD 12
     |     |     |
     +-----+-----+
           |
           v
     Process I/O
```

Linux `epoll` can monitor many file descriptors and notify an application when operations are likely to make progress.

This is a foundation of high-concurrency networking servers, though an application must still handle partial reads, partial writes, and `EAGAIN`.

## 9. Sockets are also used for local IPC

Sockets do not necessarily require physical network communication.

Unix domain sockets (`AF_UNIX`) provide local communication between processes.

For example:

```c
socket(AF_UNIX, SOCK_STREAM, 0);
```

A local socket might be associated with a filesystem pathname such as:

```text
/run/my-service.sock
```

The communication remains within the operating system instead of requiring an external Ethernet interface.

Unix domain sockets additionally support capabilities such as passing file descriptors between processes using ancillary messages.

## 10. Inspecting sockets on Linux

The `ss` command provides visibility into the socket state maintained by the kernel.

```bash
# Show listening TCP sockets
ss -ltnp

# Show established TCP connections
ss -tnp state established

# Show UDP sockets
ss -uanp

# Show TCP connection details, including kernel metrics
ss -tinm
```

For example, a listening socket might appear as:

```text
State   Local Address:Port     Peer Address:Port
LISTEN  0.0.0.0:8080           0.0.0.0:*
```

While an established connection might appear as:

```text
ESTAB   10.0.0.10:8080         10.0.0.2:53000
```

For a process with PID 1234, socket file descriptors can also be inspected through:

```bash
ls -l /proc/1234/fd
```

A socket descriptor may appear as:

```text
3 -> socket:[123456]
```

The number in brackets identifies the socket inode, not its TCP port.

## 11. Essential mental model

The most useful way to think about Linux sockets is to separate three concepts:

```text
File descriptor

How the process references the socket

Kernel socket

Communication endpoint, operations, state, and buffers

Transport and networking protocols

TCP, UDP, IP, routing, and network device processing
```

A socket is not a packet, a network interface, a port, or necessarily a connection. It is the abstraction through which applications access communication services implemented by the kernel.
