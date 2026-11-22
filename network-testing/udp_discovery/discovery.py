"""Optional classroom UDP discovery demo, independent of voting.

Run with: python discovery.py listen --host 192.168.x.x --port 39731
On another authorized LAN device: python discovery.py find --port 39731
The responder only advertises a locally configured URL. Treat it as untrusted.
"""
import argparse
import socket

MAGIC = b'CAMPUSVOTE_DISCOVER_V1'
PORT = 39731

def listen(host, port, website):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        sock.settimeout(1)
        print(f'UDP discovery demonstration on {host}:{port} (Ctrl+C to stop)')
        while True:
            try:
                message, address = sock.recvfrom(256)
            except socket.timeout:
                continue
            if message == MAGIC:
                sock.sendto(('CAMPUSVOTE_V1 ' + website).encode('ascii'), address)

def find(port, timeout):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        sock.sendto(MAGIC, ('255.255.255.255', port))
        print('Discovery replies are informational; verify HTTPS identity manually.')
        try:
            while True:
                data, address = sock.recvfrom(256)
                if data.startswith(b'CAMPUSVOTE_V1 '):
                    print(address[0], data.decode('ascii', errors='replace'))
        except socket.timeout:
            pass

def main():
    parser = argparse.ArgumentParser(description='Authorized classroom-only LAN discovery demo')
    parser.add_argument('mode', choices=['listen','find'])
    parser.add_argument('--host', default='127.0.0.1', help='Listener bind address')
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--website', default='https://voting.school.test')
    parser.add_argument('--timeout', type=float, default=3)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Port must be 1024-65535')
    try:
        if args.mode == 'listen': listen(args.host, args.port, args.website)
        else: find(args.port, args.timeout)
    except KeyboardInterrupt:
        print('Stopped')

if __name__ == '__main__': main()
