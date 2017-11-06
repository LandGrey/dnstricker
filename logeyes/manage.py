#!/usr/bin/env python
import multiprocessing
import os
import sys

from dns import dnsloger

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dnslog.settings")
    from django.core.management import execute_from_command_line
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        p = multiprocessing.Process(target=dnsloger.start)
        p.daemon = True
        p.start()
    execute_from_command_line(sys.argv)
