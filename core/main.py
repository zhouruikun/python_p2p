#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
p2p test


Author: Zhou Kun
web: blog.zhoukuniyc.tech
last edit: 2018-11-04
"""

import sys
import p2pServer
import p2pClient

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'h':
        print('''
        Usage  main [command] [parameter]
        h : help
        start:  start program   parameter: server client
        stop: stop program
        ''')
        sys.exit(0)
    if sys.argv[1] == 'start':
        if len(sys.argv) <= 2:
            print('para err')
        print('start  ' + sys.argv[2])
        if sys.argv[2] == 'server':
            p2pServer.run_server()
        elif sys.argv[2] == 'client':
            p2pClient.run_client()
        else:
            print('''
                    Usage  main [command] [parameter]
                    h : help
                    start:  start program   parameter: server client
                    stop: stop program
                    ''')
    if sys.argv[1] == 'stop':
        print('stop')
        sys.exit(0)

