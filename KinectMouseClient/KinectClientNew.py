import socket, sys
import win32api, win32con, math, time

(width, height) = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))['Monitor'][2:4]
if (len(sys.argv) > 1):
    ip = sys.argv[1]
else:
    ip = "10.139.58.163"
server_address = (ip, 10005)

def tryToConnect(server_address):
    global ip, sock
    connected = False
    srvr_address = server_address
    while (not connected):
        try:
            print("Trying to connect")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect(server_address)
            print("Connected successfully")
            sock.send(b"get|1|HandRight|1|HandLeft")
            connected = True
        except socket.timeout:
            print("Failed. Trying after 10 seconds")
            server_address = srvr_address
            time.sleep(10)



tryToConnect(server_address)


x = 0
y = 0


def moveTo(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0,0)

def mouseDown(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouseUp(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def scroll(x,y,amount):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,x,y,amount,0)

def uncompressNumber(s):
    return (ord(s[0])*255 + ord(s[1]))

newPosition = (0,0)
lastY = 0
newY = 0
changeY = 0
newClick = False
click = False
clickTime = None
newScroll = False
lastTime = time.time()

sock.settimeout(5.0)

class SmoothInteger:
    
    def __init__(self):
        self.values = []
        self.loc = 0
        self.total = 0.0
        self.smoothness = 15.0
        self.threshold = 150.0
        self.lastRetValue = 0
    
    def add(self, v):
        retValue = 0
        if (len(self.values) == self.smoothness):
            self.total += -self.values[self.loc] + v
            self.values[self.loc] = v
            self.loc += 1
            if (self.loc == self.smoothness): self.loc = 0
            retValue = self.total/self.smoothness
        else: 
            self.total += v
            self.values.append(v)
            retValue = self.total / len(self.values)
        
        if (math.fabs(self.lastRetValue - retValue) < self.threshold): retValue = self.lastRetValue
        self.lastRetValue = retValue
        return retValue

def readStream(useInformation):
    global sock, server_address
    recv = b""
    startWait = time.time()
    try:
        for i in range(0,3):
            sock.recv(1)
        for i in range(0,16):
            recv += sock.recv(1)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        tryToConnect(server_address)
        recv = b"N-------N-------"

    if (len(recv) == 0):
        print("Connection lost")
        tryToConnect(server_address)
        recv = b"N-------N-------"
    if (not useInformation): return
    recv = recv.decode('ISO-8859-1')
    
    data = {}
    if (recv[0] != 'N'):
        data['HandRight'] = (uncompressNumber(recv[2:4]), 65535 - uncompressNumber(recv[4:6]))
        data['RightState'] = (recv[1] == 'O')
    else:
        data['HandRight'] = None
        data['RightState'] = None

    if (recv[8] != 'N'):    
        data['HandLeft'] = (uncompressNumber(recv[10:12]), 65535 - uncompressNumber(recv[12:14]))
        data['LeftState'] = (recv[9] == 'O')
    
    fullData = {}
    fullData['Body 0'] = data
    return fullData

x = SmoothInteger()
y = SmoothInteger()
while (True):
    
    if (time.time() - lastTime < 0.032):
        data = readStream(False)
        continue
    else:
        data = readStream(True)

    

    newPosition = data['Body 0']['HandRight']
    newClick = not data['Body 0']['RightState']
   # newScroll = not data['Body 0']['LeftState']
   # newY = int(data['Body 0']['HandLeft'][1])
    #print(newPosition)
    if (newPosition == None): continue
    newTime = time.time()
    #if (newTime != lastTime and lastTime != None): print(1/(newTime - lastTime))
    print(newPosition)
    lastTime = newTime
    #moveTo(newPosition[0] - lastPosition[0], newPosition[1] - lastPosition[1])
    X = int(x.add(newPosition[0]))
    Y = int(y.add(newPosition[1]))


    moveTo(X,Y)

    if (clickTime != None and clickTime < time.time()):
        mouseDown(0,0)
        clickTime = None

    if (newClick != click):
        click = newClick
        if (newClick):
            clickTime = time.time() + 1.0
        else:
            mouseDown(0,0)
            mouseUp(0,0)
            clickTime = None

    
    """
    if (newScroll or changeY != 0):
        if (newScroll):
            scroll(0, 0, newY - lastY)
            changeY = newY - lastY
        else:
            scroll(0, 0, changeY)
            if (changeY > 0): changeY -= 1
            else: changeY += 1

    lastY = newY
    """

