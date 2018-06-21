#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   这个文件主要用于实时显示CSI的图片
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import socket
from struct import unpack
import numpy as np
from .read_bfree import read_bfree
from .scaled_csi import scaled_csi
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.animation as animation

ip = 'localhost'
port = 1234


class CSILive(object):
    def __init__(self):
        sns.set_context("notebook", font_scale=1.4, rc={"lines.linewidth": 2.5})
        Y = np.zeros(30)
        X = np.linspace(1, 30, 30)
        plt.xlim(1, 30)
        plt.ylim(-10, 35)
        plt.xlabel('subcarrier index')
        plt.ylabel('SNR (dB)')
        plt.title('CSI live')

        self.l11, = plt.plot(X, Y, color='#DC143C', linestyle='-', linewidth=2, marker='o')
        #self.l12, = plt.plot(X, Y, color="#DA70D6", linestyle='-', linewidth=2)
        #self.l13, = plt.plot(X, Y, color='#FFC0CB', linestyle='-', linewidth=1)

        self.l21, = plt.plot(X, Y, color='#000079', linestyle='-', linewidth=2, marker='H')
        #self.l22, = plt.plot(X, Y, color="#4a4aff", linestyle='-', linewidth=2)
        #self.l23, = plt.plot(X, Y, color="#b9b9ff", linestyle='-', linewidth=1)

        self.l31, = plt.plot(X, Y, color="#006000", linestyle='-', linewidth=2, marker='s')
        #self.l32, = plt.plot(X, Y, color="#00ec00", linestyle='-', linewidth=2)
        #self.l33, = plt.plot(X, Y, color="#93ff93", linestyle='-', linewidth=1)
        plt.legend((self.l11, self.l21, self.l31), ('antenna 1', 'antenna 2', 'antenna 3'))

    def update(self, data):
        """绘制动画的时候每一次都会调用这个函数来更新.
        data: 每一次要绘制的数据
        """
        #print("update")
        Y1, Y2, Y3 = data

        #tmp = self.l12.get_ydata(orig=True)
        #self.l12.set_ydata(self.l11.get_ydata(orig=True))
        #self.l13.set_ydata(tmp)
        self.l11.set_ydata(Y1)

        #tmp = self.l22.get_ydata(orig=True)
        #self.l22.set_ydata(self.l21.get_ydata(orig=True))
        #self.l23.set_ydata(tmp)
        self.l21.set_ydata(Y2)

        #tmp = self.l32.get_ydata(orig=True)
        #self.l32.set_ydata(self.l31.get_ydata(orig=True))
        #self.l33.set_ydata(tmp)
        self.l31.set_ydata(Y3)
        return self.l11, self.l21, self.l31


    def show(self):
        """显示图像
        """
        plt.show()


def read_data(sk):
    triangle = np.array([1, 3, 6])
    while True:
        length = unpack('>H', sk.recv(2))    # 解析成功
        buff = sk.recv(length)
        while len(buff) != length:
            buff = buff + sk.recv(length - len(buff))
        code = unpack('B', buff[0:1])[0]    # 代码
        if code == 187:
            data = read_bfree(buff[1:])
            perm = data['perm']
            nrx = data['nrx']
            csi = data['csi']
            if sum(perm) == triangle[nrx - 1]:  # 下标从0开始
                csi[:, perm - 1, :] = csi[:, [x for x in range(nrx)], :]
            scaled_csi(data)
            Y1 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 0, :]).T), 1e-8, 1e100))  # 转化为分贝
            Y2 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 1, :]).T), 1e-8, 1e100))  # 转化为分贝
            Y3 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 2, :]).T), 1e-8, 1e100))  # 转化为分贝
            yield Y1, Y2, Y3


def rand_CSI():
    while True:
        Y1 = np.random.randint(20, 50, 30)
        Y2 = np.random.randint(20, 50, 30)
        Y3 = np.random.randint(20, 50, 30)
        yield Y1, Y2, Y3


def live_begin(sk):
    fig = plt.figure()
    live = CSILive()
    item = animation.FuncAnimation(fig, live.update, frames=read_data(sk),
                                    interval=0, blit=True)
    plt.show()


def server():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.bind((ip, port))
    sk.listen(5)
    print('开始监听...')
    while True:
        client_sk, address = sk.accept()
        live_begin(client_sk)
        print('处理完了一个连接...')


if __name__ == '__main__':
    server()

