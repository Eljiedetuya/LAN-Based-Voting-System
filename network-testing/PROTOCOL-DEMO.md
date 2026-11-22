# Controlled networking demonstrations

Use only the school-owned or explicitly authorized isolated test LAN. Do not inspect real student ballots or credentials.

- **TCP:** Open a synthetic test page. In Wireshark, use a display filter such as `tcp.port == 443` to view connection metadata. HTTPS encrypts payloads.
- **DHCP:** On a test client, run `ipconfig /all` (Windows) or `ip addr` and inspect DHCP lease details from the router. Do not log device MAC addresses in the voting DB.
- **ARP:** Inspect `arp -a` and, where permitted, filter `arp` in Wireshark. On routed networks the MAC may be the gateway's.
- **DNS:** If local DNS is configured, run `nslookup voting.school.test` using the local resolver. Otherwise use server IP with properly configured HTTPS.
- **ICMP:** Use `ping <server-lan-ip>` to test reachability (firewall rules may block replies even if web service works).
- **UDP:** Run the separate discovery.py script on a designated demo computer; its response is not authentication and is NOT used for voting.
- **Wireshark:** Capture on demo devices, not indiscriminately on student devices. Stop and delete temporary captures according to school policy.

## UDP discovery demonstration

On server: `python network-testing/udp_discovery/discovery.py listen --host <server-lan-ip> --website https://voting.school.test`

On another LAN computer: `python network-testing/udp_discovery/discovery.py find`

Broadcast may not work across VLANs, client isolation, or some routers. Keep the UDP responder disabled during normal voting.
