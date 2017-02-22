#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
import string, os, sys
from ConfigParser import SafeConfigParser, Error

from logger import log

if __name__ == '__main__':
    cf = SafeConfigParser()
    cf.read("alarm_process.conf")
    send_url = cf.get('module_alarm', 'send_url')
    if send_url is True:
        print True
    else:
        print False







