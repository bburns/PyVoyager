
"""
Simple logging module - writes to config.logfile and echoes to stdout.

Usage:
    import log
    log.start()
    log.log('x',x)
"""


import sys
import datetime

import config


def start():
    "start a new logfile and print the date/time"
    f = open(config.logfile,'wb')
    f.write('')
    f.close()
    time('started')
    log('----------------------------------------')


def time(prefix=''):
    "log the current date/time, with optional prefix string"
    dt = datetime.datetime.now()
    sdt = dt.strftime("%Y-%m-%d %I:%M%p").lower()
    if prefix: prefix = prefix + ' '
    s = prefix + sdt
    log(s)


def log(*args):
    "add a line to the logfile - treat like print statement. echoes to stdout also."
    #. how handle , after print stmt? separate fn
    f = open(config.logfile,'ab')
    sargs = [str(a) for a in args]
    s = ' '.join(sargs)
    f.write(s + '\n')
    f.close()
    print s # echo to stdout


def stop():
    log('----------------------------------------')
    time('stopped')


if __name__ == '__main__':
    start()
    log('testing',1,2,3)
    log('x',1.234)


