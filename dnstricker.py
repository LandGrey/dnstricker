#!/usr/bin/env python
# coding: utf-8
# Build By LandGrey

import time
import struct
try:
    import SocketServer
except:
    import socketserver as SocketServer

def current_time():
    return time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime())


class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        while True:
            try:
                d = ord(data[i])
            except:
                d = data[i]
            if d == 0:
                break
            if d < 32:
                self.name += '.'
            else:
                self.name += chr(d)
            i += 1
        self.querybytes = data[0:i + 1]
        self.type, self.classify = struct.unpack('>HH', data[i + 1:i + 5])
        self.len = i + 5

    def getbytes(self):
        return self.querybytes + struct.pack('>HH', self.type, self.classify)


class SinDNSAnswer:
    def __init__(self, ip):
        self.type = 1
        self.classify = 1
        self.name = 49164
        self.datalength = 4
        self.timetolive = 190
        self.ip = ip

    def getbytes(self):
        res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
        s = self.ip.split('.')
        res += struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        return res


class SinDNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
        self.query = SinDNSQuery(data[12:])

    def getname(self):
        return self.query.name

    def setip(self, ip):
        self.answer = SinDNSAnswer(ip)
        self.answers = 1
        self.flags = 33152

    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        res = res + self.query.getbytes()
        if self.answers != 0:
            res += self.answer.getbytes()
        return res


class DnsRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        global ip_address
        data = self.request[0].strip()
        dns = SinDNSFrame(data)
        conn = self.request[1]
        query_name = dns.getname()

        # A record
        if dns.query.type == 1:
            response = ip_address if query_name.endswith(dns_domain) else None
            if response:
                dns.setip(response)
                log_format = {'client_ip': self.client_address[0], 'client_port': self.client_address[1],
                              'query': query_name, 'record-type': 'A', 'response': response}
                conn.sendto(dns.getbytes(), self.client_address)
                print('{} {}'.format(current_time(), log_format))
            else:
                dns.setip(default_ip)
                conn.sendto(dns.getbytes(), self.client_address)

        # AAAA record
        elif dns.query.type == 28:
            response = ip_address if query_name.endswith(dns_domain) else None
            if response:
                dns.setip(response)
                conn.sendto(dns.getbytes(), self.client_address)
                log_format = {'client_ip': self.client_address[0], 'client_port': self.client_address[1],
                              'query': query_name, 'record-type': 'AAAA', 'response': response}
                print('{} {}'.format(current_time(), log_format))
            else:
                dns.setip(default_ip)
                conn.sendto(dns.getbytes(), self.client_address)
        else:
            dns.setip(default_ip)
            conn.sendto(dns.getbytes(), self.client_address)


class SimpleDnsServer:
    def __init__(self, port=53):
        self.port = port

    def start(self):
        host, port = "0.0.0.0", self.port
        dns_udp_server = SocketServer.UDPServer((host, port), DnsRequestHandler)
        dns_udp_server.serve_forever()


if __name__ == "__main__":
    dns_domain = 'test.com'
    ip_address = '2.2.2.2'
    default_ip = '192.168.1.1'
    dns_server = SimpleDnsServer()
    print("{} Dnslog server start".format(current_time()))
    try:
        dns_server.start()
    except KeyboardInterrupt:
        print('{} User quit.'.format(current_time()))
