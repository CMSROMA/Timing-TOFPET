import socket

class XYMover:

    def __init__(self,port):
        self.my_socket = socket.socket()
        self.my_socket.connect(('127.0.0.1', port))
        self.home()

    def home(self):
        self.my_socket.send(bytes('home'))
        response = self.my_socket.recv(1024).decode().strip()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=0
            self.y=0
            return 'ok'

        
    def moveXY(self,x,y):
        self.my_socket.send(bytes('%d %d'%(x,y)))
        response = self.my_socket.recv(1024).decode().strip()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=x
            self.y=y
            return 'ok'

    def relativeX(self,x):
        self.my_socket.send(bytes('%d %d'%(self.x+x,self.y)))
        response = self.my_socket.recv(1024).decode().strip()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=x+self.x
            return 'ok'

    def relativeY(self,y):
        self.my_socket.send(bytes('%d %d'%(self.x,self.y+y)))
        response = self.my_socket.recv(1024).decode().strip()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.y=y+self.y
            return 'ok'

    def position(self):
        self.my_socket.send(bytes('position'))
        response = self.my_socket.recv(1024).decode().strip()
        xy = response.split(" ")
        if (int(xy[0]) != self.x or int(xy[1]) != self.y):
            return 'error'
        else:
            return '%d %d'%(self.x,self.y)

