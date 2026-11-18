# LAN network testing (authorized demonstration only)

- `ipconfig` on Windows: find the server IPv4 address, subnet mask, and default gateway.
- `ping <SERVER_IP>` from another device: basic connectivity test (firewalls may block ICMP).
- `arp -a`: inspect local ARP cache, where applicable.
- `nslookup <LOCAL_HOSTNAME>`: check local DNS if configured.
- Wireshark: capture only authorized test-device traffic; do not record real voter credentials or ballots.
- Optional Cisco Packet Tracer: draw router/AP, one server, students, and monitor topology.

Do not enable UDP discovery until the ballot application is independently working.
