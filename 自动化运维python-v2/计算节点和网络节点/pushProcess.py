from __future__ import with_statement
import socket, threading,time
import ConfigParser
import random
import nodeTable

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)
'''
��ȡ�����ļ�����ʼ��������
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
    ��ʱ����������Ϣ������RTT
    '''
    def __init__(self,goOnEvent,rtt,lock,nodetable):
        '''
        ��ʼ��Socket,RTT�ͼ�Ⱥ�ڵ�״̬��
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
            #�ȴ���ؽڵ㷢��ACK�ظ�
            while self.rtt['signal']:
                pass
            SEND_INFO=config.get('info','SEND_INFO')
            SEND_INFO=SEND_INFO+':'+str(self.nodetable.myid)+":TIME:"+str(time.time())+":RANK:"+str(self.rtt['rank'])
            self.lock.acquire()
            #��ͨ������Ϣ���ϲ�����Ϣ������Эͬ�������Ϣ
            SEND_INFO=SEND_INFO+':'+self.rtt['message']
            self.rtt['message']=''
            self.lock.release()
            hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            rand=random.randint(-1,1)
            if temp+0.2*rand>=0 and temp+0.2*rand<=10:
                temp=temp+0.2*rand
            time.sleep(temp)
            #����������Ϣ������������Ϣ
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
