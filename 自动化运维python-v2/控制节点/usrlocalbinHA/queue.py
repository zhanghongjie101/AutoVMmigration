class Queue():
    def __init__(self,size):
        self.size=size
        self.count=0
        self.front=size-1
        self.rear=0
        self.data=[i for i in range(size)]
        self.threshold=30
    def insert(self,time_data):
        if self.count==self.size:
            self.rear=(self.rear+1)%self.size
        else:
            self.count=self.count+1
        self.front=(self.front+1)%self.size
        self.data[self.front]=time_data
    def get_front(self):
        return self.data[self.front]
    def get_rear(self):
        return self.data[self.rear]
    def get_count(self):
        return self.count
    def get_threshold(self):
        return self.threshold
    def set_threshold(self,threshold):
        self.threshold=threshold
    def clear(self):
        self.count=0
        self.front=self.size-1
        self.rear=0
        self.threshold=30
    def is_empty(self):
        return self.count==0
