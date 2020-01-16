from __future__ import with_statement
import socket, threading,time
import ConfigParser
import random
import nodeTable

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
读取配置文件，初始化类属性
'''
SERVER_PORT=int(config.get('info','SERVER_PORT'))
CHECK_PERIOD=int(config.get('info','CHECK_PERIOD'))
CHECK_TIMEOUT=int(config.get('info','CHECK_TIMEOUT'))
SERVER_IP=config.get('info','SERVER_IP')
BEAT_PERIOD=int(config.get('info','BEAT_PERIOD'))

#SERVER_PORT=43279
#CHECK_PERIOD=20
#CHECK_TIMEOUT=15
#SERVER_IP='202.38.95.145'
#BEAT_PERIOD=5

class PushProcess(threading.Thread):
    '''
    定时发送心跳信息，计算RTT
    '''
    def __init__(self,goOnEvent,rtt,lock,nodetable):
        '''
        初始化Socket,RTT和集群节点状态表
        '''
        super(PushProcess,self).__init__()
        self.goOnEvent=goOnEvent
        self.recSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.recSocket.settimeout(CHECK_TIMEOUT)
        self.recSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.rtt=rtt
        self.lock=lock
        self.nodetable=nodetable
    def run(self):
        #print 'sending heartbeat to IP %s,port %d' % (SERVER_IP,SERVER_PORT)
        BEAT_PERIOD=float(config.get('info','BEAT_PERIOD'))
        temp=0
        while self.goOnEvent.isSet():
            #等待监控节点发送ACK回复
            while self.rtt['signal']:
                pass
            SEND_INFO=config.get('info','SEND_INFO')
            SEND_INFO=SEND_INFO+':'+str(self.nodetable.myid)+":TIME:"+str(time.time())+":RANK:"+str(self.rtt['rank'])
            self.lock.acquire()
            #普通心跳信息加上补充信息，包括协同检测结果信息
            SEND_INFO=SEND_INFO+':'+self.rtt['message']
            self.rtt['message']=''
            self.lock.release()
            hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            rand=random.randint(-1,1)
            if temp+0.2*rand>=0 and temp+0.2*rand<=10:
                temp=temp+0.2*rand
            time.sleep(temp)
            #发送心跳信息和其他补充信息
            hbSocket.sendto(SEND_INFO,(SERVER_IP,SERVER_PORT))
            print SEND_INFO
            self.rtt['signal']=True;
            if __debug__:
                pass
            self.lock.acquire()
            try:
                BEAT_PERIOD=self.rtt['rank']
            finally:
                self.lock.release()
            time.sleep(BEAT_PERIOD)
