# Addressing

Network communication requires two addressing systems: **IP addresses** for
global routing and **MAC addresses** for local delivery. Understanding their
relationship is fundamental to networking.

## IP vs MAC

| Feature    | MAC Address                 | IP Address                      |
| ---------- | --------------------------- | ------------------------------- |
| Identity   | Who the device is           | Where the device is currently   |
| Layer      | Layer 2 (Data Link)         | Layer 3 (Network)               |
| Structure  | Flat (random)               | Hierarchical (organized)        |
| Usage      | Local delivery (same LAN)   | Global routing (across networks)|
| Permanence | Hard-coded in hardware      | Dynamic, changes with location  |

**Why both are needed:** MAC addresses are "flat" - they contain no location
information. If we routed by MAC alone, every router on Earth would need to know
the location of every network card (billions). IP addresses are "hierarchical" -
`192.168.1.5` tells routers "network `192.168.1`, device `.5`." Routers only
need to know how to reach the network, not every device.

**Mobility:** When you move your laptop from home to a coffee shop:
- MAC address stays the same (you're the same device)
- IP address changes (you're at a new location)

## Host-to-Host Communication

When Host A wants to communicate with Host B:

### Step 1: Local or Remote?

Host A compares Host B's IP with its own using the **subnet mask**.

- **Local (same subnet):** Send directly to Host B's MAC address
- **Remote (different subnet):** Send to the default gateway (router)

### Step 2: ARP (Address Resolution Protocol)

Hardware only understands MAC addresses. If Host A knows the IP but not the MAC,
it uses ARP:

```
Host A                                 All Hosts on LAN
   |                                        |
   |-- "Who has 192.168.1.50? Tell me." --->| (broadcast)
   |                                        |
   |<--- "That's me! MAC: AA:BB:CC..." -----| Host B responds
```

ARP broadcasts to `FF:FF:FF:FF:FF:FF` (all devices). Only the matching host
replies.

### Step 3: The Journey

For remote destinations, the packet traverses multiple routers. Each router:
- Strips the old Layer 2 frame
- Wraps in a new frame for the next hop
- Source and destination IPs **never change**

## Local vs Remote Communication

| Feature         | Local (Same Subnet)           | Remote (Different Subnet)      |
| --------------- | ----------------------------- | ------------------------------ |
| Device Used     | Switch                        | Router/Gateway                 |
| Dest MAC        | Target host's MAC             | Router's interface MAC         |
| IP Handling     | Direct delivery               | Multi-hop routing              |

## Broadcast vs Unicast

### Unicast (Point-to-Point)

With modern **switches**, unicast traffic is delivered only to the destination
port. The switch maintains a MAC address table and sends frames only where
needed. Other computers never see the message.

### Broadcast (Everyone)

Some scenarios require all devices to receive the message:

- **ARP requests:** Destination MAC set to `FF:FF:FF:FF:FF:FF`
- **DHCP discovery:** New device asking for an IP address

The switch sends broadcasts to all ports. Every device receives it, but only the
relevant one responds.

### Legacy: Hubs

Old **hubs** (Layer 1 devices) copied all signals to all ports. Every NIC
received every frame but only accepted frames addressed to its MAC.

### Wireless Networks

Wi-Fi is a shared medium. Radio waves physically reach all devices in range.
Each device's NIC checks the destination MAC and drops frames not addressed to
it. This is why encryption (WPA2/3) is critical - the signal reaches everyone.

## Promiscuous Mode

The "only accept your own frames" rule is a software choice. Putting a NIC into
**promiscuous mode** tells it to accept all frames regardless of destination
MAC.

On unencrypted networks or legacy hubs, this enables packet sniffing. This is
why Layer 6 encryption (HTTPS) matters - even if someone captures your traffic,
they can't read it.

## Common Failures

| Problem           | Cause                                          |
| ----------------- | ---------------------------------------------- |
| No Route to Host  | Router doesn't know path to destination IP     |
| Address Conflict  | Two hosts have the same IP address             |
| ICMP Blocked      | Firewall blocks ping but allows other traffic  |
| ARP Cache Stale   | Old MAC-to-IP mapping causes misdelivery       |

## Related

- [OSI Model](osi-model.md) - The layer model for networking
- [Encapsulation](encapsulation.md) - How addresses are added to frames/packets
