import socket, sys
import win32api, win32con, math, time

(width, height) = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))['Monitor'][2:4]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if (len(sys.argv) > 1):
    ip = sys.argv[1]
else:
    ip = "10.139.62.221"
server_address = (ip, 8000)
sock.connect(server_address)

#sock.send(b"HandRight|Width|65535|Height|65535|Output|0|LeftState|RightState")
sock.send(b"HandRight|Width|" + str(width).encode() + b"|Height|" + str(height).encode() + b"|Output|2|HandLeft|LeftState|RightState")
x = 0
y = 0


def moveTo(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0,0)
   # print((x,y))

def mouseDown(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

def mouseUp(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def scroll(x,y,amount):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,x,y,amount,0)
   # print(amount)

def uncompressNumber(s):
    return (ord(s[0])*255 + ord(s[1]))

def uncompressVector(s):
    return (uncompressNumber(s[0:2]),uncompressNumber(s[2:4]))

lastPosition = win32api.GetCursorPos()
newPosition = (0,0)
lastY = 0
newY = 0
changeY = 0
newClick = False
click = False
newScroll = False
#scroll = False

def readPython():
    data = b"";
    nBracket = None
    while (nBracket != 0):
        c = sock.recv(1)
       # print(nBracket)
        if (c == b'{'):
            if (nBracket == None): nBracket = 1
            else: nBracket += 1
        if (c == b'}'): nBracket -= 1
        data += c

    data = data.decode('utf-8')
    data = eval(data)
    return data

def readStream():
    #HandRight, HandLeft, LeftState,RightState
    recv = b""
    for i in range(0,10):
        recv += sock.recv(1)
    
    recv = recv.decode('ISO-8859-1')

    data = {}
    data['HandRight'] = uncompressVector(recv[0:4])
    data['HandLeft'] = uncompressVector(recv[4:8])
    data['LeftState'] = (recv[8] == 'O')
    data['RightState'] = (recv[9] == 'O')
    fullData = {}
    fullData['Body 0'] = data
    return fullData

def readCompressedData():
    char = None
    bodyID = None
    data = {}
    while (bodyID != b'\n'):
        bodyID = sock.recv(1)
        if (bodyID == b'\n'): break
        bodyID = "Body " + bodyID.decode('ISO-8859-1')
        if (bodyID not in data): data[bodyID] = {}
        jointID = sock.recv(1)
        jointID += sock.recv(1)
        jointID = jointID.decode('ISO-8859-1')
        if (jointID == "07"):
            s = b""
            for i in range(0,4):
                s += sock.recv(1)
            s = s.decode('ISO-8859-1')
            data[bodyID]['HandLeft'] = uncompressVector(s)
        elif (jointID == "11"):
            s = b""
            for i in range(0,4):
                s += sock.recv(1)
            s = s.decode('ISO-8859-1')
            data[bodyID]['HandRight'] = uncompressVector(s)
        elif (jointID == "HL"):
            handOpen = sock.recv(1)
            data[bodyID]['LeftState'] = (handOpen == b'O')
        elif (jointID == "HR"):
            handOpen = sock.recv(1)
            data[bodyID]['RightState'] = (handOpen == b'O')
    return data

start = time.time()
while (True):
    #data = readCompressedData()
    data = readStream()

    newPosition = data['Body 0']['HandRight']
    newClick = not data['Body 0']['RightState']
    newScroll = not data['Body 0']['LeftState']
    newY = int(data['Body 0']['HandLeft'][1])
    #print(lastPosition, newPosition)
    #moveTo(newPosition[0] - lastPosition[0], newPosition[1] - lastPosition[1])
    print(time.time() - start)
    start = time.time()
    x = int((newPosition[0]) * 65535.0 / width)
    y = int((newPosition[1]) * 65535.0 / height)
    moveTo(x,y)
    if (newClick != click):
        if (newClick):
            mouseDown(0,0)
            print("CLick")
        else:
            mouseUp(0,0)
            print("No Click")
        click = newClick
    lastPosition = win32api.GetCursorPos()
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

