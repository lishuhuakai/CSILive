import socket
import time
from struct import unpack

addr = ('localhost', 8090)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        s.connect(addr)
        break
    except Exception as e:
        time.sleep(1)

with open('11.dat', 'rb') as f:
    try:
        while True:
            time.sleep(1)
            len = f.read(2)
            s.send(len)
            length = unpack('>H', len)[0]    # 解析成功
            print('........................................................')
            buff = f.read(length)
            s.send(buff)
    except Exception as e:
        pass

time.sleep(10)