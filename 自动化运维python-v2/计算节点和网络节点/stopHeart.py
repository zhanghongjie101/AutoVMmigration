from __future__ import with_statement
import ConfigParser
import sys
import os

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
�ƹ���Ա����ͨ��python stopHeart START������������
ͨ��python stopHeart STOP��ͣ����������������ͣ���ᱻ��ؽڵ��ж�Ϊ�ڵ����
'''
if sys.argv[1]=='START':
    os.system('python Client1993.py &')
if sys.argv[1]=='STOP':
    os.system('ps -ef | grep Client1993.py | grep -v grep | cut -c 9-15 | xargs kill -s 9')
    config.set('info','SEND_INFO','STOP')
    config.write(open("HAconfig.cfg","w"))
    os.system('python Client1993.py &')
