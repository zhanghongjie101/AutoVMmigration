from __future__ import with_statement
import socket, threading, time
from neutronclient.v2_0 import client as neutronclient
import ConfigParser
import sendEmail
import logging  
import logging.handlers
import queue
import heartRecive
import heartTest
import resourceAgent
import novaAgent
import snapShot
import monitorVM
import sig
import nodeTable

def main():
    #queue1=queue.Queue(200)
    #queue2=queue.Queue(200)
    #sig1=sig.SIG(False)
    #sig2=sig.SIG(False)
    '''
    myqueue={'net1':queue.Queue(200),'net2':queue.Queue(200),'com1':queue.Queue(200),'com2':queue.Queue(200),
            'com3':queue.Queue(200),'com4':queue.Queue(200),'com5':queue.Queue(200),'com6':queue.Queue(200),
            'com7':queue.Queue(200),'com8':queue.Queue(200),'com9':queue.Queue(200),'com10':queue.Queue(200)}
    signal={'net1':False,'net2':False,'com1':False,'com2':False,
            'com3':False,'com4':False,'com5':False,'com6':False,
            'com7':False,'com8':False,'com9':False,'com10':False}
    '''
    myqueue=[queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200),
            queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200),queue.Queue(200)]
    signal=[False,False,False,False,False,False,False,False,False,False,False,False]
    #lock1=threading.Lock()
    #lock2=threading.Lock()
    '''
    lock={'net1':threading.Lock(),'net2':threading.Lock(),'com1':threading.Lock(),'com2':threading.Lock(),
            'com3':threading.Lock(),'com4':threading.Lock(),'com5':threading.Lock(),'com6':threading.Lock(),
            'com7':threading.Lock(),'com8':threading.Lock(),'com9':threading.Lock(),'com10':threading.Lock()}
    '''
    lock=[threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock(),
            threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock(),threading.Lock()]
    lockdict=threading.Lock()
    ip_list=['192.168.11.2','192.168.11.3','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0',
            '0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0','0.0.0.0']
    nodetable=nodeTable.nodeTable(ip_list=ip_list)
    dictionTime={}
    dictionHost={}
    
    receiverEvent=threading.Event()
    receiverEvent.set()
    receiver=heartRecive.Receiver(goOnEvent=receiverEvent,myqueue=myqueue,lock=lock,nodetable=nodetable)
    receiver.start()
    heart_test=heartTest.heartTest(goOnEvent=receiverEvent,myqueue=myqueue,lock=lock,signal=signal,nodetable=nodetable)
    heart_test.start()
    neutron_agent=resourceAgent.NeutronAgent(goOnEvent=receiverEvent,signal=signal)
    neutron_agent.start()
    nova_agent=novaAgent.novaAgent(goOnEvent=receiverEvent,signal=signal)
    nova_agent.start()
    snapshot_agent=snapShot.snapShotAgent(goOnEvent=receiverEvent)
    snapshot_agent.start()
    logvm=monitorVM.logVM(goOnEvent=receiverEvent,dictionTime=dictionTime,dictionHost=dictionHost,lock=lockdict)
    logvm.start()
    monitorvm=monitorVM.monitorVM(goOnEvent=receiverEvent,dictionTime=dictionTime,dictionHost=dictionHost,lock=lockdict)
    monitorvm.start()

    print 'press Ctrl-C to stop'

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print 'Exiting, please wait...'
        receiverEvent.clear()
        receiver.join()
        heart_test.join()
        neutron_agent.join()
        nova_agent.join()
        snapshot_agent.join()
        logvm.join
        monitorvm.join()
        print 'Finished.'
	
if __name__=='__main__':
    main()
