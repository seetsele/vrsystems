#!/usr/bin/env python3
"""
Simple local SMTP debugging server that prints received messages.
Uses smtpd.DebuggingServer (works in many Python versions). Run before executing flows that send email.
"""
import sys
try:
    import smtpd
    import asyncore
except Exception as e:
    print('smtpd not available in this Python runtime:', e)
    sys.exit(1)

class DebugServer(smtpd.DebuggingServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print('\n--- SMTP Debug Message ---')
        print('Peer:', peer)
        print('From:', mailfrom)
        print('To:', rcpttos)
        print('Data:\n')
        print(data)
        print('--- End Message ---\n')
        return

if __name__ == '__main__':
    port = 1025
    addr = ('localhost', port)
    print(f'Starting Debug SMTP server on {addr[0]}:{addr[1]} (prints to stdout)')
    server = DebugServer(addr, None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print('SMTP debug server stopped')
