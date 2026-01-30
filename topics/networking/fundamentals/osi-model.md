# OSI Model

The **OSI (Open Systems Interconnection) Model** is a conceptual framework that
standardizes communication functions into seven abstract layers. Developed by
ISO in the 1980s, it acts as a universal language for networking.

## Why Communication Models Matter

In the 1970s-80s, every manufacturer (IBM, DEC, Apple) had proprietary ways of
sending data. An IBM computer could only talk to another IBM. Communication
models solve this "Tower of Babel" problem:

| Benefit                | Description                                        |
| ---------------------- | -------------------------------------------------- |
| Interoperability       | Different hardware/software can communicate        |
| Modularity             | Change one layer without rewriting the system      |
| Troubleshooting        | Isolate problems to a specific layer               |
| Specialization         | Companies focus on one layer (routers, encryption) |
| Managing Complexity    | Break networking into manageable pieces            |

## The Seven Layers

Mnemonic: **"All People Seem To Need Data Processing"** (top to bottom).

### Layer 7: Application

The layer closest to the user, providing network services to applications.

- **Protocols:** HTTP, DNS, SMTP, FTP, DHCP
- **Role:** Identifies communication partners, determines resource availability
- **Note:** This is not the app itself (Chrome), but the protocol the app uses
  (HTTP)

**Security:** Web Application Firewalls (WAFs) operate here to block SQL
injection and XSS attacks that lower layers cannot detect.

### Layer 6: Presentation

The "syntax layer" or "translator." Ensures data sent by one system can be read
by another.

**Three functions:**

- **Translation:** Converts between character sets (ASCII/EBCDIC/Unicode)
- **Compression:** Shrinks data (lossy: JPEG, MPEG; lossless: ZIP, GIF)
- **Encryption:** SSL/TLS converts plaintext to ciphertext

**Standards:** JPEG, PNG, MPEG, QuickTime, ASCII, UTF-8

### Layer 5: Session

The "coordinator" managing dialogue between computers.

- **Session Control:** Establishes, maintains, and terminates connections
- **Dialogue Control:** Determines who talks when (simplex, half-duplex,
  full-duplex)
- **Synchronization:** Adds checkpoints so failed transfers resume from last
  checkpoint instead of restarting

**Protocols:** NetBIOS, RPC, PPTP, NFS

### Layer 4: Transport

The "reliability and logistics hub." Gets data to the specific application on a
machine.

- **Port Numbers:** Ensures data for your browser (port 443) doesn't go to your
  email client
- **Segmentation:** Breaks large files into segments, reassembles in order
- **Flow Control:** Slows fast senders when receivers are overwhelmed
- **Error Control:** Manages retransmission of lost/corrupted segments

**PDU:** Segments

#### TCP vs UDP

| Feature    | TCP ("The Reliable One")          | UDP ("The Fast One")           |
| ---------- | --------------------------------- | ------------------------------ |
| Connection | Connection-oriented (handshake)   | Connectionless (no handshake)  |
| Reliability| Guaranteed; resends lost data     | No guarantee; data may be lost |
| Order      | Delivers in exact order sent      | Data can arrive in any order   |
| Use Case   | Web, email, file transfers        | Streaming, gaming, DNS, VoIP   |

#### TCP 3-Way Handshake

```
Client                    Server
   |                         |
   |-------- SYN ----------->|  "I want to talk"
   |                         |
   |<------ SYN-ACK ---------|  "Got it, I also want to talk"
   |                         |
   |-------- ACK ----------->|  "Got it. Let's start."
   |                         |
```

### Layer 3: Network

The "traffic controller." Moves data between different networks.

- **Logical Addressing:** IP addresses (IPv4: `192.168.1.1`, IPv6: `2607:f8b0::`)
- **Routing:** Chooses the best path across interconnected networks
- **Fragmentation:** Breaks oversized packets, reassembles at destination

**Protocols:** IP (IPv4/IPv6), ICMP
**PDU:** Packets
**Hardware:** Routers

**Developer relevance:** Subnets, ICMP (ping), public vs private IPs, cloud
networking.

### Layer 2: Data Link

Provides reliable communication between devices on the **same local network**.

**Sub-layers:**

- **LLC (Logical Link Control):** Identifies network layer protocol, handles
  flow/error control
- **MAC (Media Access Control):** Physical addressing, collision avoidance

**Functions:**

- **Physical Addressing:** 48-bit MAC addresses (`00:1A:2B:3C:4D:5E`)
- **Framing:** Marks message boundaries
- **Error Detection:** Frame Check Sequence (FCS) detects corruption

**PDU:** Frames
**Hardware:** Switches (maintain MAC address tables)

### Layer 1: Physical

The foundation dealing with actual physical media and raw bit transmission.

- **Bit Representation:** How 1s and 0s are encoded (voltage, light pulses)
- **Transmission Rate:** Bits per second (bps)
- **Synchronization:** Sender and receiver clocked at same speed
- **Topologies:** Star, mesh, ring configurations

**Guided Media (Cables):**

- Copper (Cat5e, Cat6) - electrical pulses
- Coaxial - cable internet/TV
- Fiber optic - light pulses, long distance

**Unguided Media (Wireless):**

- Radio waves (Wi-Fi, Bluetooth)
- Microwaves (satellite, tower-to-tower)

**PDU:** Bits
**Hardware:** Hubs, repeaters, cables, NICs

## Layer Comparison

| Layer | Name         | PDU      | Key Function              | Hardware      |
| ----- | ------------ | -------- | ------------------------- | ------------- |
| 7     | Application  | Data     | User interface            | -             |
| 6     | Presentation | Data     | Format/encrypt            | -             |
| 5     | Session      | Data     | Manage dialogue           | -             |
| 4     | Transport    | Segment  | Port addressing           | -             |
| 3     | Network      | Packet   | Routing                   | Routers       |
| 2     | Data Link    | Frame    | Local delivery            | Switches      |
| 1     | Physical     | Bits     | Signal transmission       | Hubs, cables  |

## OSI vs TCP/IP

The modern internet uses the **TCP/IP model** which consolidates OSI into 4-5
layers (Application, Transport, Internet, Link). However, OSI remains the
industry standard for troubleshooting, teaching, and security analysis.

## Related

- [Encapsulation](encapsulation.md) - How data travels through layers
- [Addressing](addressing.md) - IP vs MAC and host-to-host communication
