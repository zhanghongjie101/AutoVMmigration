ALIVE=0
SUSPECT=1
DEAD=2
LEAVE=3
COUNT=12
class node:
    '''
    �ڵ��ඨ�壬ÿ����������״̬������Ϊһ���ڵ�
    '''
    def __init__(self,num):
        '''
        ��ʼ״̬ΪLEAVE��id��ip��ʼ��
        '''
        self.status=LEAVE
        self.number=num
        self.ip='0.0.0.0'
    #���Ե�get��set
    def get_status(self):
        return self.status
    def set_status(self,state):
        self.status=state
    def set_ip(self,ip):
        self.ip=ip
    def get_ip(self):
        return self.ip

class nodeTable:
    '''
    �ڵ�״̬���壬��Ⱥ�еĽڵ�״̬��������������У�ͨ���ض���Э��ͬ��ÿ���ڵ��״̬��
    '''
    def __init__(self,myid,ip_list):
        '''
        ͨ�������ip�б������id������ʼ���ڵ�״̬��
        '''
        self.table=[node(0),node(1),node(2),node(3),node(4),node(5),node(6),node(7),
            node(8),node(9),node(10),node(11)]
        for i in range(COUNT):
            self.table[i].set_ip(ip_list[i])
        self.myid=myid
    #״̬���get��set
    def set_status(self,num,state):
        self.table[num].set_status(state)
    def get_status(self,num):
        return self.table[num].get_status()
    def is_neighbor(self,target):
        '''
        �жϵ�ǰ�ڵ�ʱ����Ŀ��ڵ�ĵ�һ����Ծ���ھ�
        '''
        i=(self.myid+1)%COUNT
        while i!=self.myid:
            if i==target:
                return True
            if self.table[i].get_status()==ALIVE:
                break
            else:
                i=(i+1)%COUNT
        i=(self.myid-1+COUNT)%COUNT
        while i!=self.myid:
            if i==target:
                return True
            if self.table[i].get_status()==ALIVE:
                break
            else:
                i=(i-1+COUNT)%COUNT
        return False
    def get_ip(self,num):
        return self.table[num].get_ip()
