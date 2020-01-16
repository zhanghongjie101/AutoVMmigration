ALIVE=0
SUSPECT=1
DEAD=2
LEAVE=3
COUNT=12
class node:
    '''
    节点类定义，每个服务器的状态都保存为一个节点
    '''
    def __init__(self,num):
        '''
        初始状态为LEAVE，id和ip初始化
        '''
        self.status=LEAVE
        self.number=num
        self.ip='0.0.0.0'
    #属性的get和set
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
    节点状态表定义，集群中的节点状态都保存在这个表中，通过特定的协议同步每个节点的状态表
    '''
    def __init__(self,myid,ip_list):
        '''
        通过传入的ip列表参数和id参数初始化节点状态表
        '''
        self.table=[node(0),node(1),node(2),node(3),node(4),node(5),node(6),node(7),
            node(8),node(9),node(10),node(11)]
        for i in range(COUNT):
            self.table[i].set_ip(ip_list[i])
        self.myid=myid
    #状态表的get和set
    def set_status(self,num,state):
        self.table[num].set_status(state)
    def get_status(self,num):
        return self.table[num].get_status()
    def is_neighbor(self,target):
        '''
        判断当前节点时候是目标节点的第一个活跃的邻居
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
