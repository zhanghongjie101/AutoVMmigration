from __future__ import with_statement
import threading, time
from novaclient.v1_1 import servers
from novaclient import client
import ConfigParser
import logging
import logging.handlers

config=ConfigParser.ConfigParser()
with open('/usr/local/bin/newHA/HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
TENANT_NAME=config.get('info','TENANT_NAME')
USERNAME=config.get('info','USERNAME')
PASSWORD=config.get('info','PASSWORD')
AUTH_URL=config.get('info','AUTH_URL')
VERSION=config.get('info','VERSION')

LOG_FILE =config.get('info','NOVA_LOG_FILE')

class logVM(threading.Thread):
    def __init__(self,goOnEvent,dictionTime,dictionHost,lock):
        super(logVM,self).__init__()
        self.goOnEvent=goOnEvent
        self.dictionTime=dictionTime
        self.dictionHost=dictionHost
        self.lock=lock
    def logInfo(self):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)

        logger = logging.getLogger('nova_log')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        for sid in self.dictionTime.keys():
            server=nova.servers.get(sid)
            if server.status=='ACTIVE':
                self.lock.acquire()
                T1=time.time()
                T2=self.dictionTime[server.id]
                T=T1-T2
                source=self.dictionHost[server.id]
                dest=getattr(server,'OS-EXT-SRV-ATTR:host')
                self.dictionTime.pop(server.id)
                self.dictionHost.pop(server.id)
                self.lock.release()
                information='migrate server: %s from %s to %s used %d secends' % (server.name,source,dest,T)
                logger.info(information)
        logger.removeHandler(handler)
    def run(self):
        while self.goOnEvent.isSet():
            self.logInfo()

class monitorVM(threading.Thread):
    def __init__(self,goOnEvent,dictionTime,dictionHost,lock):
        super(monitorVM,self).__init__()
        self.goOnEvent=goOnEvent
        self.dictionTime=dictionTime
        self.dictionHost=dictionHost
        self.lock=lock
    def pushIntoDict(self):
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        all_servers=nova.servers.list()
        for server in all_servers:
            server=nova.servers.get(server.id)
            if (server.status=='MIGRATING' or server.status=='REBUILD') and not self.dictionTime.has_key(server.id):
                self.lock.acquire()
                self.dictionTime[server.id]=time.time()
                self.dictionHost[server.id]=getattr(server,'OS-EXT-SRV-ATTR:host')
                self.lock.release()
    def run(self):
        while self.goOnEvent.isSet():
            self.pushIntoDict()
