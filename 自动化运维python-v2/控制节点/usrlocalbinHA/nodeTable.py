ALIVE=0
SUSPECT=1
DEAD=2
LEAVE=3
BACK=4
COUNT=12
class node:
    def __init__(self,num):
        self.status=LEAVE
        self.number=num
        self.ip='0.0.0.0'
    def get_status(self):
        return self.status
    def set_status(self,state):
        self.status=state
    def set_ip(self,ip):
        self.ip=ip
    def get_ip(self):
        return self.ip

class nodeTable:
    def __init__(self,ip_list):
        self.table=[node(0),node(1),node(2),node(3),node(4),node(5),node(6),node(7),
            node(8),node(9),node(10),node(11)]
        for i in range(COUNT):
            self.table[i].set_ip(ip_list[i])
        self.alivenum=0
    def set_status(self,num,state):
        self.table[num].set_status(state)
    def get_status(self,num):
        return self.table[num].get_status()
    def get_ip(self,num):
        return self.table[num].get_ip()
