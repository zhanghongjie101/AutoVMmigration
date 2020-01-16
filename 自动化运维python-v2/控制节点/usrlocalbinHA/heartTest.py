from __future__ import with_statement
import heartRecive
import socket,threading, time
import queue
import ConfigParser
import sig
import nodeTable

config=ConfigParser.ConfigParser()
with open('/usr/local/bin/newHA/HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)

BROADCAST_PORT=int(config.get('info','BROADCAST_PORT'))
BROADCAST_IP=config.get('info','BROADCAST_IP')

class heartTest(threading.Thread):
    def __init__(self,goOnEvent,myqueue,lock,signal,nodetable):
        super(heartTest,self).__init__()
        self.goOnEvent=goOnEvent
        #self.queue1=queue1
        #self.queue2=queue2
        #self.lock1=lock1
        #self.lock2=lock2
        #self.sig1=sig1
        #self.sig2=sig2
        self.myqueue=myqueue
        self.lock=lock
        self.signal=signal
        self.nodetable=nodetable
        #self.nodeDict=['net1','net2','com1','com2','com3','com4','com5','com6','com7','com8','com9','com10']
    def broadcast(self,ip,port,content):
        hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        hbSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        hbSocket.sendto(content,(ip,port))
    def run(self):
        while self.goOnEvent.isSet():
            #limit=time.time()-heartRecive.CHECK_TIMEOUT
            for v in range(nodeTable.COUNT):
                self.lock[v].acquire()
                try:
                    if not self.myqueue[v].is_empty():
                        if self.myqueue[v].get_front()<(time.time()-self.myqueue[v].get_threshold()):
                            if self.nodetable.get_status(v)==nodeTable.DEAD:
                                print 'dead!%s' % v
                                self.signal[v]=True
                                self.myqueue[v].clear()
                                content='BROAD:NODE:%d:STATUS:%d' % (v,nodeTable.DEAD)
                                self.broadcast(BROADCAST_IP,BROADCAST_PORT,content)
                                print content
                                self.nodetable.alivenum=self.nodetable.alivenum-1
                            if self.nodetable.get_status(v)==nodeTable.ALIVE:
                                print 'suspect!%s' % v
                                self.nodetable.set_status(v,nodeTable.SUSPECT)
                                content='BROAD:NODE:%d:STATUS:%d' % (v,nodeTable.SUSPECT)
                                self.broadcast(BROADCAST_IP,BROADCAST_PORT,content)
                                print content
                                self.nodetable.alivenum=self.nodetable.alivenum-1
                            if self.nodetable.get_status(v)==nodeTable.BACK:
                                print 'back!%s' % v
                                self.nodetable.set_status(v,nodeTable.ALIVE)
                                self.nodetable.alivenum=self.nodetable.alivenum+1		
                                self.myqueue[v].insert(time.time())
                finally:
                    self.lock[v].release()
