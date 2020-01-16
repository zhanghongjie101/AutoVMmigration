from __future__ import with_statement
import socket, threading, time
import queue
import ConfigParser
import random
import nodeTable
config=ConfigParser.ConfigParser()
with open('/usr/local/bin/newHA/HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
读取配置文件信息，初始化类的属性
'''
UDP_PORT=int(config.get('info','UDP_PORT'))
CHECK_TIMEOUT=int(config.get('info','CHECK_TIMEOUT'))
BROADCAST_PORT=int(config.get('info','BROADCAST_PORT'))
BROADCAST_IP=config.get('info','BROADCAST_IP')
#将节点数限制为12个，根据具体情况而定
COUNT=12

class Receiver(threading.Thread):
    '''
    接收来自被监控节点的心跳信息
    '''
    def __init__(self,goOnEvent,myqueue,lock,nodetable):
        super(Receiver,self).__init__()
        self.goOnEvent=goOnEvent
        self.recSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.recSocket.settimeout(CHECK_TIMEOUT)
        self.recSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.recSocket.bind(('',UDP_PORT))
        #self.queue1=queue1
        #self.queue2=queue2
        #self.lock1=lock1
        #self.lock2=lock2
        self.myqueue=myqueue
        self.lock=lock
        self.nodetable=nodetable
        '''
        self.commandDict1={'STOP1':'net1','STOP2':'net2','STOP3':'com1','STOP4':'com2','STOP5':'com3','STOP6':'com4','STOP7':'com5','STOP8':'com6',
                'STOP9':'com7','STOP10':'com8','STOP11':'com9','STOP12':'com10'}
        self.commandDict2={'TEST1':'net1','TEST2':'net2','TEST3':'com1','TEST4':'com2','TEST5':'com3','TEST6':'com4','TEST7':'com5','TEST8':'com6',
                'TEST9':'com7','TEST10':'com8','TEST11':'com9','TEST12':'com10'}
        '''
        self.count=[1,1,1,1,1,1,1,1,1,1,1,1]
        self.flag=[True,True,True,True,True,True,True,True,True,True,True,True]
    def sendACK(self,ip,port,content):
        hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.sendto(content,(ip,port))
    def broadcast(self,ip,port,content):
        hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hbSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        hbSocket.sendto(content,(ip,port))
    def run(self):
        delay=0
        while self.goOnEvent.isSet():
            try:
                data,addr=self.recSocket.recvfrom(50)
                print addr[0]," ",data
                if data.find('STOP')>=0:
                    nodeid=int(data.split(':')[1])
                    self.lock[nodeid].acquire()
                    try:
                        self.myqueue[nodeid].clear()
                        self.nodetable.set_status(nodeid,nodeTable.LEAVE)
                        broadinfo='BROAD:NODE:%d:STATUS:%d' % (nodeid,nodeTable.LEAVE)
                        self.broadcast(BROADCAST_IP,BROADCAST_PORT,broadinfo)
                    finally:
                        self.lock[nodeid].release()
                if data.find('TEST')>=0:
                    nodeid=int(data.split(':')[1])
                    self.lock[nodeid].acquire()
                    try:
                        threshold=int(data.split(':')[5])
                        self.myqueue[nodeid].set_threshold(threshold*2)
                        self.myqueue[nodeid].insert(time.time())
                        content="ACK:"+data
                        allstatus=''
                        if self.nodetable.get_status(nodeid)==nodeTable.LEAVE or self.nodetable.get_status(nodeid)==nodeTable.DEAD or self.nodetable.get_status(nodeid)==nodeTable.SUSPECT:
                                self.nodetable.set_status(nodeid,nodeTable.ALIVE)
                                self.nodetable.alivenum=self.nodetable.alivenum+1
                                allstatus='table'
                                for i in range(COUNT):
                                        status=self.nodetable.get_status(i)
                                        allstatus=allstatus+':'+str(status)
                                broadinfo='BROAD:NODE:%d:STATUS:%d' % (nodeid,nodeTable.ALIVE)
                                self.broadcast(BROADCAST_IP,BROADCAST_PORT,broadinfo)
                        content=content+allstatus
                        self.sendACK(addr[0],UDP_PORT,content)
                    finally:
                        self.lock[nodeid].release()
                    if data.find('SUSPECT')>=0:
                        susid=int(data.split(':')[7])
                        sustatu=int(data.split(':')[8])
                        if sustatu==nodeTable.ALIVE:
                            self.lock[susid].acquire()
                            self.flag[susid]=False
                            self.lock[susid].release()
                        if self.count[susid]<self.nodetable.alivenum:
                            self.count[susid]=self.count[susid]+1
                        else:
                            if self.flag[susid]:
                                self.lock[susid].acquire()
                                self.nodetable.set_status(susid,nodeTable.DEAD)
                                self.count[susid]=1
                                self.flag[susid]=True
                                self.lock[susid].release()
                            else:
                                self.lock[susid].acquire()
                                self.nodetable.set_status(susid,nodeTable.BACK)
                                self.count[susid]=1
                                self.flag[susid]=True
                                self.lock[susid].release()
            except socket.timeout:
                pass
