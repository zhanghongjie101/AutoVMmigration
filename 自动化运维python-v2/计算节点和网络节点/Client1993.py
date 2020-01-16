from __future__ import with_statement
import socket, threading,time
import ConfigParser

import socket,threading,time
import pushProcess,pullProcess
import nodeTable

config=ConfigParser.ConfigParser()
with open('HAconfig.cfg','rw') as cfgfile:
    config.readfp(cfgfile)

SEND_INFO=config.get('info','SEND_INFO')
MYID=int(config.get('info','MYID'))

def send_sig(
                SERVER_IP='202.38.95.145',
                SERVER_PORT=43279,
                BEAT_PERIOD=5
        ):
    print 'sending heartbeat to IP %s,port %d' % (SERVER_IP,SERVER_PORT)
    print 'press Ctrl-C to stop'
    while True:
        hbSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hbSocket.sendto('TEST',(SERVER_IP,SERVER_PORT))
        if __debug__:
            print 'Time: %s' % time.ctime()
        time.sleep(BEAT_PERIOD)

def main():
    event=threading.Event()
    event.set()
    rtt={'time':0,'rank':5,'signal':False,'message':''}
    lock=threading.Lock()
    ip_list=['192.168.11.2','192.168.11.3','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0',
	    '0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0']
    nodetable=nodeTable.nodeTable(myid=MYID,ip_list=ip_list)
    push=pushProcess.PushProcess(goOnEvent=event,rtt=rtt,lock=lock,nodetable=nodetable)
    #启动发送心跳进程
    push.start()
    pull=pullProcess.PullProcess(goOnEvent=event,rtt=rtt,lock=lock,nodetable=nodetable)
    #启动监听控制信号的进程
    pull.start()
    try:
        while True:
            SEND_INFO=config.get('info','SEND_INFO')
            #如果配置文件中的SEND_INFO变成了STOP就停止两个进程，退出程序
            if SEND_INFO=='STOP':
                pushEvent.clear()
                push.join()
                print 'End push'
                config.set('info','SEND_INFO','TEST')
                config.write(open("HAconfig.cfg","w"))
                return 0
            time.sleep(1)
        except KeyboardInterrupt:
            #按下Ctrl+C终止进程
            event.clear()
            push.join()
            pull.join()
            print 'End push'
            return 0

if __name__=='__main__':
    main()
