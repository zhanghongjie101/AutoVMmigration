from __future__ import with_statement
import threading, time
from novaclient.v1_1 import servers
from novaclient import client
import ConfigParser
import sendEmail
import logging
import logging.handlers
import sig

config=ConfigParser.ConfigParser()
with open('/usr/local/bin/newHA/HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
TENANT_NAME=config.get('info','TENANT_NAME')
USERNAME=config.get('info','USERNAME')
PASSWORD=config.get('info','PASSWORD')
AUTH_URL=config.get('info','AUTH_URL')
VERSION=config.get('info','VERSION')

COM1_NODE=config.get('info','COM1_NODE')
COM2_NODE=config.get('info','COM2_NODE')
COM1_IP=config.get('info','COM1_IP')
COM2_IP=config.get('info','COM2_IP')

host_ip_dict={COM1_IP:COM1_NODE, COM2_IP:COM2_NODE}

LOG_FILE =config.get('info','NOVA_LOG_FILE')

class novaAgent(threading.Thread):
    def __init__(self,goOnEvent,signal):
        super(novaAgent,self).__init__()
        self.goOnEvent=goOnEvent
        #self.sig1=sig1
        #self.sig2=sig2
        self.signal=signal
        self.nodeDict={'com1','com2','com3','com4','com5','com6','com7','com8','com9','com10'}
    def migrate(self,source):
        nova = client.Client(VERSION,USERNAME,PASSWORD,TENANT_NAME,AUTH_URL)
        all_servers=nova.servers.list()
        count=0
        for server in all_servers:
            if getattr(server,'OS-EXT-SRV-ATTR:host')==source:
                count=count+1
                flag=True
                times=0
                while flag:
                    times=times+1
                    if times>=10:
                        break
                    try:
                        server.evacuate(on_shared_storage='True')
                        flag=False
                    except:
                        time.sleep(3)
        return count
    def run(self):
        while self.goOnEvent.isSet():
            if self.signal[2]:
                self.signal[2]=False
                T1=time.time()
                num=self.migrate(COM1_NODE)
                T2=time.time()
                T=T2-T1
                mail_head='Host %s is dead' % COM1_NODE
                mail_content='Host %s is dead. migrate servers from %s to other node. number: %d. used time: %d' % (COM1_NODE,COM1_NODE,num,T)
                #print mail_content
                sendEmail.send_mail(mail_head,mail_content)
            if self.signal[3]:
                self.signal[3]=False
                T1=time.time()
                num=self.migrate(COM2_NODE)
                T2=time.time()
                T=T2-T1
                mail_head='Host %s is dead' % COM2_NODE
                mail_content='Host %s is dead. migrate servers from %s to other node. number: %d. used time: %d' % (COM2_NODE,COM2_NODE,num,T)
                #print mail_content
                sendEmail.send_mail(mail_head,mail_content)
