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
VERSION_NUM=int(config.get('info','version_num'))
snapshot_time=config.get('info','snapshot_time')

LOG_FILE =config.get('info','SNAPSHOT_LOG_FILE')

class snapShotAgent(threading.Thread):
    def __init__(self,goOnEvent):
        super(snapShotAgent,self).__init__()
        self.goOnEvent=goOnEvent
    def snapshot(self):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)

        logger = logging.getLogger('snapshot_log')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        all_servers=nova.servers.list()
        count=0
        for server in all_servers:
            if getattr(server,'OS-EXT-STS:vm_state')=='active':
                count=count+1
                flag=True
                while flag:
                    try:
                        server.create_image(server.name)
                        self.delete_last(server.name,VERSION_NUM)
                        flag=False
                    except:
                        time.sleep(3)
                information='create snapshot %s from instance %s' % (server.name,server.name)
                logger.info(information)
        logger.removeHandler(handler)
        return count
    def delete_last(self,vmname,num):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger = logging.getLogger('snapshot_log')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        image_list=nova.images.findall(name=vmname)
        count=len(image_list)
        if count<=num:
            logger.removeHandler(handler)
            return 0
        sorted(image_list,key = lambda x:x.created)
        temp=count-num
        i=1
        while i<=temp:
            nova.images.delete(image_list[count-i])
            i=i+1
            information='delete old snapshot %s' % (vmname)
            logger.info(information)
        logger.removeHandler(handler)
        return temp
    def delete_snapshot(self):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger = logging.getLogger('snapshot_log')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        image_list=nova.images.list()
        for image in image_list:
            try:
                server=image.server
                serverid=server['id']
                try:
                    vm=nova.servers.get(serverid)
                except:
                    nova.images.delete(image.id)
                    information='delete snapshot with no instance: %s' % (image.id)
                    logger.info(information)
            except:
                    pass
        logger.removeHandler(handler)
    def run(self):
        while self.goOnEvent.isSet():
            now=time.strftime("%X", time.localtime())
            if now==snapshot_time:
                self.snapshot()
            self.delete_snapshot()
