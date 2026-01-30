# Encapsulation

The "sandwich" process describes how data travels through the OSI model. The
sender **encapsulates** data (wraps it in layers), and the receiver
**decapsulates** it (unwraps it).

## Sending: Encapsulation (Down the Stack)

Each layer adds its own header with instructions.

```
+----------------------------------------------------------+
| Layer 7-5  |  HTTP POST + session + encryption = DATA    |
+----------------------------------------------------------+
                              |
                              v
+----------------------------------------------------------+
| Layer 4    |  TCP Header  |           DATA               |
|            |  (ports)     |                              |  = SEGMENT
+----------------------------------------------------------+
                              |
                              v
+----------------------------------------------------------+
| Layer 3    |  IP Header   |         SEGMENT              |
|            |  (IPs)       |                              |  = PACKET
+----------------------------------------------------------+
                              |
                              v
+----------------------------------------------------------+
| Layer 2    | Eth Header |       PACKET        | Trailer  |
|            | (MACs)     |                     | (FCS)    |  = FRAME
+----------------------------------------------------------+
                              |
                              v
+----------------------------------------------------------+
| Layer 1    |  01101001011010010110... (electrical/light) |  = BITS
+----------------------------------------------------------+
```

1. **Layers 7-5:** Application creates HTTP message, encrypts it, manages
   session. Output: **Data**
2. **Layer 4:** Adds TCP header with source/destination ports. Output:
   **Segment**
3. **Layer 3:** Adds IP header with source/destination IPs. Output: **Packet**
4. **Layer 2:** Adds Ethernet header (MACs) and trailer (checksum). Output:
   **Frame**
5. **Layer 1:** Converts to electrical pulses or light. Output: **Bits**

## In Transit: Routers

Data doesn't travel directly to the destination. At each router:

1. Router strips Layer 2 frame (the "local hop" is complete)
2. Examines Layer 3 packet for destination IP
3. Wraps packet in a **new** Layer 2 frame for the next hop
4. Source and destination IP addresses (Layer 3) **never change** during the
   journey

```
+----------+          +----------+          +----------+
|  Host A  |--------->| Router 1 |--------->| Router 2 |--------->...
+----------+          +----------+          +----------+
     |                     |                     |
     |  L2: MAC of R1      |  L2: MAC of R2      |  L2: MAC of next
     |  L3: IP of Dest     |  L3: IP of Dest     |  L3: IP of Dest
     |                     |                     |  (L3 unchanged)
```

## Receiving: Decapsulation (Up the Stack)

Each layer strips its header to reveal the payload inside.

1. **Layer 1:** NIC receives pulses, converts to **Bits**
2. **Layer 2:** Checks destination MAC. "Is this my MAC? Yes." Strips frame,
   passes **Packet** up
3. **Layer 3:** Checks destination IP. "Is this my IP? Yes." Strips IP header,
   passes **Segment** up
4. **Layer 4:** Checks port (e.g., 443). Routes to web server software.
   Reassembles segments in order
5. **Layers 5-7:** Decrypts, processes HTTP request

## What Each Layer Checks

| Layer | Sender Action    | Receiver Check         | PDU     |
| ----- | ---------------- | ---------------------- | ------- |
| L4    | Add port 443     | Is this for port 443?  | Segment |
| L3    | Add dest IP      | Is this my IP?         | Packet  |
| L2    | Add router MAC   | Is this my MAC?        | Frame   |
| L1    | Send as light    | Receive light          | Bits    |

## Debugging with Layers

If the receiver never gets the frame (Layer 2), check:
- Layer 1: Was the signal received? (cable, NIC)
- Layer 2: Was the MAC address correct?

If the receiver gets the packet but the application doesn't respond, check:
- Layer 4: Is there a port mismatch?
- Firewall: Is the port blocked?

## Related

- [OSI Model](osi-model.md) - The seven-layer framework
- [Addressing](addressing.md) - How IP and MAC work together
