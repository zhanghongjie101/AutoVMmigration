from __future__ import with_statement
import socket, threading,time
import ConfigParser
import random
import nodeTable

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
读取配置文件的信息，初始化系统
'''
SERVER_PORT=int(config.get('info','SERVER_PORT'))
RECIVE_PORT=int(config.get('info','RECIVE_PORT'))
CHECK_PERIOD=int(config.get('info','CHECK_PERIOD'))
CHECK_TIMEOUT=int(config.get('info','CHECK_TIMEOUT'))
BEAT_PERIOD=int(config.get('info','BEAT_PERIOD'))
rank1_send=int(config.get('info','rank1_send'))
rank2_send=int(config.get('info','rank2_send'))
rank3_send=int(config.get('info','rank3_send'))
rank1_range_max=int(config.get('info','rank1_range_max'))
rank2_range_min=int(config.get('info','rank2_range_min'))
rank2_range_max=int(config.get('info','rank2_range_max'))
rank3_range_min=int(config.get('info','rank3_range_min'))
FACT=float(config.get('info','FACT'))
PING_THRESHOLD=int(config.get('info','PING_THRESHOLD'))

class PullProcess(threading.Thread):
    '''
    接收来自监控节点的控制信息，根据不同的控制信息调整自己的状态
    '''
    def __init__(self,goOnEvent,rtt,lock,nodetable):
        '''
        初始化Socket，当前网络拥塞情况RTT，锁，集群节点状态表，ping的参数设置
        '''
        super(PullProcess,self).__init__()
        self.goOnEvent=goOnEvent
        self.recSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.recSocket.settimeout(CHECK_TIMEOUT)
        self.recSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.recSocket.bind(('',RECIVE_PORT))
        self.rtt=rtt
        self.lock=lock
        self.nodetable=nodetable
        self.pingtime=time.time()
        self.pingflag=False
        self.pingnode=0
    def run(self):
        while self.goOnEvent.isSet():
            try:
                data,addr=self.recSocket.recvfrom(100)
                print data," ",time.time()
                '''
                根据包中不同的字段得到进行不同的动作
                '''
                if data.find('ACK')>=0:
                    '''
                    ACK:TEST:i:TIME:60563421:RANK:15
                    '''
                    self.lock.acquire()
                    try:
                        self.rtt['time']=FACT*self.rtt['time']+(1-FACT)*(time.time()-float(data.split(':')[4]))
                        print self.rtt['time']
                        if self.rtt['time']<=rank1_range_max:
                            self.rtt['rank']=rank1_send
                        if self.rtt['time']>rank2_range_min and self.rtt['time']<=rank2_range_max:
                            self.rtt['rank']=rank2_send
                        if self.rtt['time']>rank3_range_min:
                            self.rtt['rank']=rank3_send
                        self.rtt['signal']=False
                    finally:
                        self.lock.release()
                    if data.find('table')>=0:
                        self.lock.acquire()
                        try:
                            index=0
                            temp_data=data.split(':')
                            for i in range(8,19):
                                self.nodetable.set_status(index,int(temp_data[i]))
                        finally:
                            self.lock.release()
                if data.find('BROAD')>=0:
                    '''
                    BROAD:NODE:i:STATUS:XXX
                    '''
                    status=int(data.split(':')[4])
                    if status==nodeTable.ALIVE:
                        nodeid=int(data.split(':')[2])
                        if nodeid!=self.nodetable.myid:
                            self.lock.acquire()
                            try:
                                self.nodetable.set_status(nodeid,nodeTable.ALIVE)
                            finally:
                                self.lock.release()
                    if status==nodeTable.SUSPECT:
                        nodeid=int(data.split(':')[2])
                        if nodeid!=self.nodetable.myid:
                            #if self.nodetable.is_neighbor(nodeid):
                            if True:
                                recSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                                recSocket.settimeout(CHECK_TIMEOUT)
                                recSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                                hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                                hbSocket.sendto('PING',(self.nodetable.get_ip(nodeid),SERVER_PORT))
                                self.pingtime=time.time()
                                self.pingflag=True
                                self.pingnode=nodeid
                    if status==nodeTable.DEAD:
                        nodeid=int(data.split(':')[2])
                        if nodeid!=self.nodetable.myid:
                            self.nodetable.set_status(nodeid,status)
                    if status==nodeTable.LEAVE:
                        nodeid=int(data.split(':')[2])
                        self.nodetable.set_status(nodeid,status)
                if data.find('PING')>=0:
                    '''
                    PING:ACK
                    '''	
                    if data.find('ACK')>=0:
                        nodeid=int(data.split(':')[2])
                        self.lock.acquire()
                        try:
                            message='SUSPECT:'+nodeid+':'+str(nodeTable.ALIVE)
                            self.rtt['message']=message
                        finally:
                            self.lock.release()	
                        self.pingflag=False
                if self.pingflag:
                    '''
                    PING:NAK
                    '''
                    if self.pingtime<time.time()-PING_THRESHOLD:
                        self.lock.acquire()
                        try:
                            message='SUSPECT:'+str(self.pingnode)+':'+str(nodeTable.DEAD)
                            self.rtt['message']=message
                        finally:
                            self.lock.release()
                        self.pingflag=False
            except socket.timeout:
                self.rtt['signal']=False
