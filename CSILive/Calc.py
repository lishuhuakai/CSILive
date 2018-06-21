from PyQt5.QtCore import QObject, QThread, pyqtSignal
from struct import unpack
from CSI.read_bfree import read_bfree
from CSI.scaled_csi import scaled_csi
import numpy as np
from Config import triangle


class CalcCSI(QObject):
    sigCalcCompleted = pyqtSignal([list])

    def __init__(self):
        super().__init__()

    def calc(self, buff):
        """calc 准备开始计算csi了
        """
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
            # 接下来的话,需要计算相位差
            # 然后进行必要的转换
            phase = np.angle(csi)
            Y4 = np.sin(np.unwrap(phase[0, 0] - phase[0, 1]))
            Y5 = np.sin(np.unwrap(phase[0, 1] - phase[0, 2]))
            Y6 = np.sin(np.unwrap(phase[0, 2] - phase[0, 0]))
            self.sigCalcCompleted.emit([Y1, Y2, Y3, Y4, Y5, Y6])
