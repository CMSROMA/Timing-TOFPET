import socket
import time

class XYMover:

    def __init__(self,port):
        self.my_socket = socket.socket()
        self.my_socket.settimeout(60) #to be checked if this is sufficient
        self.my_socket.connect(('127.0.0.1', port))
        self.x = -1. 
        self.y = -1.
        self.currentX = -1.
        self.currentY = -1.
        self.home()

    def getSocketResponse(self):
        try:
            response = self.my_socket.recv(1024).decode('utf-8').strip()
        except socket.timeout:
            response = 'error'
        return response

    def waitForIdle(self):
        currentStatus = ''
        while (currentStatus != 'Idle'):
            currentStatus = self.status()
        return

    def home(self):
        self.my_socket.send(bytes('home'))
        #self.my_socket.send(bytes('home','utf-8')) #python3
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            self.waitForIdle()
            self.checkCurrentPosition()

            if (self.currentX != 1 or
                self.currentY != 1):
                return 'error'
            else:
                self.x=1.
                self.y=1.
                return 'ok'


    def moveAbsolute(self,pos,direction):
        if (direction == 'x'):
            self.my_socket.send(bytes('%3.1f %3.1f'%(pos,self.y)))
            #self.my_socket.send(bytes('%d %d'%(pos,self.y),'utf-8'))#python3
        elif (direction == 'y'):
            self.my_socket.send(bytes('%3.1f %3.1f'%(self.x,pos)))
            #self.my_socket.send(bytes('%d %d'%(self.x,pos),'utf-8'))#python3
        response = self.getSocketResponse()
        if not response.startswith('ok'):
            return 'error'
        else:
            time.sleep(0.1)
            self.waitForIdle()
            self.checkCurrentPosition()
            
            if ( (direction== 'x' and self.currentX != pos ) or 
                 (direction== 'y' and self.currentY != pos ) ):
                return 'error'
            else:
                if (direction == 'x'):
                    self.x=pos
                elif (direction == 'y'):
                    self.y=pos
                return 'ok'
        
    def moveAbsoluteXY(self,x,y):
        #moving x,y separately as it seems less noisy
        ret = self.moveAbsolute(x,'x')
        if ( ret != 'ok' ):
            return 'error'
        
        ret =self.moveAbsolute(y,'y')
        if ( ret != 'ok' ):
            return 'error'
        
        return 'ok'

#    def moveRelativeX(self,x):
#        self.my_socket.send(bytes('%+d %+d'%(x,0),'utf-8'))
#        response = self.getSocketResponse()
#        if not response.startswith('ok'):
#            return 'error'
#        else:
#            time.sleep(0.1)
#            self.waitForIdle()
#            self.checkCurrentPosition()
#            if (self.currentX != x+self.x):
#                return 'error'
#            else:
#                self.x=x+self.x
#                return 'ok'
#
#    def moveRelativeY(self,y):
#        self.my_socket.send(bytes('%+d %+d'%(0,y),'utf-8'))
#        response = self.getSocketResponse()
#        if not response.startswith('ok'):
#            return 'error'
#        else:
#            time.sleep(0.1)
#            self.waitForIdle()
#            self.checkCurrentPosition()
#            if (self.currentY != y+self.y):
#                return 'error'
#            else:
#                self.y=y+self.y
#                return 'ok'

    def estimatedPosition(self):
        return '%3.1f %3.1f'%(self.x,self.y)

    def status(self):
        self.my_socket.send(bytes('status'))
        #self.my_socket.send(bytes('status','utf-8'))#python3
        response = self.getSocketResponse()
        currentStatus = response.replace('<','').replace('>','').split(",")[0]
        return currentStatus

    def checkCurrentPosition(self):
        self.my_socket.send(bytes('status'))
        #self.my_socket.send(bytes('status','utf-8'))#python3
        response = self.getSocketResponse()
        currentPos = response.split("MPos:")[1].split(",")[0:2]
        self.currentX = abs(round(float(currentPos[0]),1))
        self.currentY = abs(round(float(currentPos[1]),1))

