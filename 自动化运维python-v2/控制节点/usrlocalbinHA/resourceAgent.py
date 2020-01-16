from __future__ import with_statement
import threading, time
from neutronclient.v2_0 import client as neutronclient
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

NET_NODE=config.get('info','NET_NODE')
COM_NODE=config.get('info','COM_NODE')
NET_IP=config.get('info','NET_IP')
COM_IP=config.get('info','COM_IP')

host_ip_dict={NET_IP:NET_NODE, COM_IP:COM_NODE}

ALIVE_NUM=int(config.get('info','ALIVE_NUM'))

LOG_FILE =config.get('info','LOG_FILE')

class NeutronAgent(threading.Thread):
    def __init__(self,goOnEvent,signal):
        super(NeutronAgent,self).__init__()
        self.goOnEvent=goOnEvent
        #self.sig1=sig1
        #self.sig2=sig2
        self.signal=signal
    def migrate(self,source,destination):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  

        formatter = logging.Formatter(fmt)   
        handler.setFormatter(formatter)

        logger = logging.getLogger('log')
        logger.addHandler(handler) 
        logger.setLevel(logging.DEBUG)
        neutron = neutronclient.Client(auth_url=AUTH_URL, username=USERNAME, password=PASSWORD, tenant_name=TENANT_NAME)
        source_routers = []
        agents = neutron.list_agents()
        for source_agent in agents['agents']:
            if source_agent['binary'] == 'neutron-l3-agent' and source_agent['host'] == source:
                source_agent_id=source_agent['id']
                source_routers = neutron.list_routers_on_l3_agent(source_agent_id)
                for source_router in source_routers['routers']:
                    source_router_id=source_router['id']
                    neutron.remove_router_from_l3_agent(source_agent_id, source_router_id)
                    information='remove router:%s from l3-agent:%s' % (source_router_id,source_agent_id)
                    logger.info(information)
                    #print "remove_router_from_l3_agent : L3 id is %s, router id is %s" %(source_agent_id, source_router_id)
        for dest_agent in agents['agents']:
            if dest_agent['binary'] == 'neutron-l3-agent' and dest_agent['host'] == destination:
                dest_agent_id=dest_agent['id']
                for dest_router in source_routers['routers']:
                    neutron.add_router_to_l3_agent(dest_agent_id, {"router_id":dest_router['id']})
                    information='add router:%s to l3-agent:%s' % (dest_router['id'],dest_agent_id)
                    logger.info(information)
                    dest_router_id=dest_router['id']
                    #print "add_router_to_l3_agent : L3 id is %s, router id is %s" %(dest_agent_id, dest_router_id)
        logger.removeHandler(handler)
        return len(source_routers['routers'])
    def count_router_mun(self,node):
        neutron = neutronclient.Client(auth_url=AUTH_URL, username=USERNAME, password=PASSWORD, tenant_name=TENANT_NAME)
        routers = []
        agents = neutron.list_agents()
        count=0
        for agent in agents['agents']:
            if agent['binary'] == 'neutron-l3-agent' and agent['host'] == node:
                agent_id=agent['id']
                routers = neutron.list_routers_on_l3_agent(agent_id)
                count=count+len(routers['routers'])
        return count
    def run(self):
        while self.goOnEvent.isSet():
            if self.signal[0] and self.signal[1]:
                mail_head='Nodes all dead'
                mail_content='Nodes all dead. Can not migrate router'
                sendEmail.send_mail(mail_head,mail_content)
                while self.signal[0] and self.signal[1]:
                    time.sleep(1)
            if self.signal[0] and not self.signal[1] and self.count_router_mun(NET_NODE)>0:
                self.signal[0]=False
                T1=time.time()
                num=self.migrate(NET_NODE,COM_NODE)
                T2=time.time()
                T=T2-T1
                mail_head='Server %s is dead' % NET_NODE
                mail_content='Server %s is dead. migrate router from %s to %s. number: %d. used time: %d' % (NET_NODE,NET_NODE,COM_NODE,num,T)		
                sendEmail.send_mail(mail_head,mail_content)
            if self.signal[1] and not self.signal[0] and self.count_router_mun(COM_NODE)>0:
                self.signal[1]=False
                T1=time.time()
                num=self.migrate(COM_NODE,NET_NODE)
                T2=time.time()
                T=T2-T1
                mail_head='Server %s is dead' % COM_NODE
                mail_content='Server %s is dead. migrate router from %s to %s. number: %d. used time: %d' % (COM_NODE,COM_NODE,NET_NODE,num,T)
                sendEmail.send_mail(mail_head,mail_content)
