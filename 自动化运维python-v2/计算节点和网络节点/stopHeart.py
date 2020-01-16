from __future__ import with_statement
import ConfigParser
import sys
import os

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
云管理员可以通过python stopHeart START启动心跳服务
通过python stopHeart STOP暂停心跳服务，这样的暂停不会被监控节点判断为节点故障
'''
if sys.argv[1]=='START':
    os.system('python Client1993.py &')
if sys.argv[1]=='STOP':
    os.system('ps -ef | grep Client1993.py | grep -v grep | cut -c 9-15 | xargs kill -s 9')
    config.set('info','SEND_INFO','STOP')
    config.write(open("HAconfig.cfg","w"))
    os.system('python Client1993.py &')
