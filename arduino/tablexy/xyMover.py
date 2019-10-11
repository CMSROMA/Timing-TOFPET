import socket

class XYMover:

    def __init__(self,port):
        self.my_socket = socket.socket()
        self.my_socket.settimeout(10) #to be checked if this is sufficient
        self.my_socket.connect(('127.0.0.1', port))
        self.home()

    def getSocketResponse(self):
        try:
            response = self.my_socket.recv(1024).decode().strip()
        except socket.timeout:
            response = 'error'
        return response

    def home(self):
        self.my_socket.send(bytes('home'))
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=0
            self.y=0
            return 'ok'

        
    def moveAbsoluteXY(self,x,y):
        self.my_socket.send(bytes('%d %d'%(x,y)))
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=x
            self.y=y
            return 'ok'

    def moveRelativeX(self,x):
        self.my_socket.send(bytes('%+d %+d'%(x,0)))
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.x=x+self.x
            return 'ok'

    def moveRelativeY(self,y):
        self.my_socket.send(bytes('%+d %+d'%(0,y)))
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.y=y+self.y
            return 'ok'

    def position(self):
        self.my_socket.send(bytes('position'))
        response = self.getSocketResponse()
        xy = response.split(" ")
        if (int(xy[0]) != self.x or int(xy[1]) != self.y):
            return 'error'
        else:
            return '%d %d'%(self.x,self.y)

