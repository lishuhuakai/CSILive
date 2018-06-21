"""
    这个文件主要用于播放dat文件的内容.
"""
from struct import unpack
import numpy as np
from CSI.read_bfree import read_bfree
from CSI.scaled_csi import scaled_csi
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.animation as animation


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
        self.l21, = plt.plot(X, Y, color='#000079', linestyle='-', linewidth=2, marker='H')
        self.l31, = plt.plot(X, Y, color="#006000", linestyle='-', linewidth=2, marker='s')
        plt.legend((self.l11, self.l21, self.l31), ('antenna 1', 'antenna 2', 'antenna 3'))

    def update(self, data):
        """绘制动画的时候每一次都会调用这个函数来更新.
        data: 每一次要绘制的数据
        """
        Y1, Y2, Y3 = data
        self.l11.set_ydata(Y1)
        self.l21.set_ydata(Y2)
        self.l31.set_ydata(Y3)
        return self.l11, self.l21, self.l31

    def show(self):
        """显示图像
        """
        plt.show()


def extract_csi(file_name):
    """抽取出csi信息.
    file_name: 文件的名称
    sample_rate: 采样率
    """
    triangle = np.array([1, 3, 6])
    with open(file_name, 'rb') as f:
        buff = f.read()
        curr = 0    # 记录当前已经处理到了的位置
        while curr < (len(buff) - 3):
            data_len = unpack('>H', buff[curr:curr+2])[0]  # 实际长度
            code = unpack('B', buff[curr+2:curr+3])[0] # 代码
            curr = curr + 3
            if code == 187:
                data = read_bfree(buff[curr:])
                perm = data['perm']
                nrx = data['nrx']
                csi = data['csi']
                if sum(perm) == triangle[nrx - 1]:  # 下标从0开始
                    csi[:, perm - 1, :] = csi[:, [x for x in range(nrx)], :]
                csi = scaled_csi(data)
                Y1 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 0, :]).T), 1e-8, 1e100))  # 转化为分贝
                Y2 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 1, :]).T), 1e-8, 1e100))  # 转化为分贝
                Y3 = 20 * np.log10(np.clip(np.abs(np.squeeze(csi[0, 2, :]).T), 1e-8, 1e100))  # 转化为分贝
                yield Y1, Y2, Y3
            curr = curr + data_len - 1


def play_dat(filepath):
    fig = plt.figure()
    live = CSILive()
    line_up = animation.FuncAnimation(fig, live.update,
                                      frames=extract_csi(filepath),
                                      interval=50,
                                      blit=True)
    plt.show()


__all__ = ['play_dat']

if __name__ == '__main__':
    fig = plt.figure()
    live = CSILive()
    line_up = animation.FuncAnimation(fig, live.update,
                                      frames=extract_csi('../20171116/10.dat'),
                                      interval=50,
                                      blit=True)
    plt.show()
