#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dnslog.settings")
import django
django.setup()
import re
import time
import struct
import SocketServer
from logview.models import *
from dnslog import settings


dns_domain = settings.DNS_DOMAIN
ip_address = settings.SERVER_IP
default_ip = '127.0.0.1'


def current_time():
    return time.strftime('[%Y.%m.%d %H:%M:%S]', time.localtime())


class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        while True:
            d = ord(data[i])
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
    global ip_address, dns_domain, default_ip

    def handle(self):
        data = self.request[0].strip()
        dns = SinDNSFrame(data)
        conn = self.request[1]
        query_host = dns.getname()

        # A record
        if dns.query.type == 1:
            response = ip_address if query_host.endswith(dns_domain) else None
            if response:
                dns.setip(response)
                log_format = {'client_ip': self.client_address[0], 'client_port': self.client_address[1],
                              'query_host': query_host, 'record_type': 'A'}
                conn.sendto(dns.getbytes(), self.client_address)
                print('{} {}'.format(current_time(), log_format))
                user_domamin = re.search(r'\.?([^\.]+)\.%s' % settings.DNS_DOMAIN, query_host)
                if user_domamin:
                    user = User.objects.filter(udomain__exact=user_domamin.group(1))
                    if user:
                        dnslog = DNSLog(user=user[0], client_ip=self.client_address[0],
                                        client_port=self.client_address[1], query_host=query_host, record_type='A')
                        dnslog.save()
            else:
                dns.setip(default_ip)
                conn.sendto(dns.getbytes(), self.client_address)

        # AAAA record
        elif dns.query.type == 28:
            response = ip_address if query_host.endswith(dns_domain) else None
            if response:
                dns.setip(response)
                conn.sendto(dns.getbytes(), self.client_address)
                log_format = {'client_ip': self.client_address[0], 'client_port': self.client_address[1],
                              'query_host': query_host, 'record_type': 'AAAA'}
                print('{} {}'.format(current_time(), log_format))
                user_domamin = re.search(r'\.?([^\.]+)\.%s' % settings.DNS_DOMAIN, query_host)
                if user_domamin:
                    user = User.objects.filter(udomain__exact=user_domamin.group(1))
                    if user:
                        dnslog = DNSLog(user=user[0], client_ip=self.client_address[0],
                                        client_port=self.client_address[1], query_host=query_host, record_type='AAAA')
                        dnslog.save()
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
        dns_udp_server = SocketServer.UDPServer(("0.0.0.0", self.port), DnsRequestHandler)
        dns_udp_server.serve_forever()


def start():
    print("{} Dnslog server start".format(current_time()))
    try:
        dns_server = SimpleDnsServer()
        dns_server.start()
    except:
        pass
