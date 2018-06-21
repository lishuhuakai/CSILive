import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QDialog, QSizePolicy, QVBoxLayout, QPushButton,
QGridLayout, QApplication)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import datetime
import socket
from struct import unpack
from AddrSetting import AddrSetting
from Calc import CalcCSI
from Config import port, ip, liveGap
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("darkgrid",{"font.sans-serif":['simhei','Droid Sans Fallback']})


def recvAll(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('对方已经关闭了连接.')
        data += more
    return data


#==========================================
# GenerateCSI
#==========================================


class GenerateCSI(QThread):
    sigLive = pyqtSignal(object)    # 用于传递实时数据

    def __init__(self, ip, port, parent=None):
        super().__init__(parent)
        self.strIP = ip
        self.iPort = port

        self.bLive = True   # 是否要直播波形?
        self.bLiveGap = liveGap if liveGap >= 0.05 else 0.05

        self.now = datetime.datetime.now()
        self.thdWorker = QThread()
        self.objCalc = CalcCSI()
        self.objCalc.moveToThread(self.thdWorker)
        self.sigLive.connect(self.objCalc.calc)
        self.objCalc.sigCalcCompleted.connect(win.live.canvas.updateAni)
        self.thdWorker.start()

    def handleClient(self, sk):
        while True:
            try:
                buff1 = recvAll(sk, 2)
                length = unpack('>H', buff1)[0]    # 解析成功
                buff2 = recvAll(sk, length)
            except EOFError as e:
                print(e)    # 对方关闭连接
                break

            now = datetime.datetime.now()
            if self.bLive and (now - self.now).total_seconds() > self.bLiveGap:
                self.sigLive.emit(buff2)
                self.now = now

    def run(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置端口复用
        sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('准备在', self.strIP, '和', self.iPort, '监听!')
        sk.bind((self.strIP, self.iPort))
        sk.listen(5)
        print('开始监听...')
        while True:
            client_sk, address = sk.accept()
            print('成功接收到连接')
            self.handleClient(client_sk)
            print('处理完了一个连接...')

#==========================================
# CustomFigCanvas
#==========================================


class CustomFigCanvas(FigureCanvas):
    def __init__(self):
        Y = np.zeros(30)
        X = np.linspace(1, 30, 30)
        self.fig = Figure(tight_layout=True)
        super().__init__(self.fig)
        plt.rcParams['axes.unicode_minus']=False
        self.amp = self.fig.add_subplot(121)
        self.l11, = self.amp.plot(X, Y, color='#DC143C', linestyle='-', linewidth=2, marker='o', label='at1')
        self.l21, = self.amp.plot(X, Y, color='#000079', linestyle='-', linewidth=2, marker='H', label='at2')
        self.l31, = self.amp.plot(X, Y, color='#006000', linestyle='-', linewidth=2, marker='s', label='at3')

        self.amp.set_xlim(1, 30)
        self.amp.set_ylim(0, 35)
        self.amp.set_autoscale_on(False)
        self.amp.set_xlabel('子信道编号')
        self.amp.set_ylabel('信噪比 (dB)')
        self.amp.set_title('幅度信息')
        self.amp.legend()

        self.phase = self.fig.add_subplot(122)
        self.l12, = self.phase.plot(X, Y, color='#00BFFF', linestyle='-', linewidth=2, marker='o', label='1&2')
        self.l22, = self.phase.plot(X, Y, color='#F4A460', linestyle='-', linewidth=2, marker='H', label='2&3')
        self.l32, = self.phase.plot(X, Y, color='#800080', linestyle='-', linewidth=2, marker='s', label='3&1')
        self.phase.set_xlim(1, 30)
        self.phase.set_ylim(-1, 1)
        self.phase.set_autoscale_on(False)
        self.phase.set_xlabel('子信道编号')
        self.phase.set_ylabel('')
        self.phase.set_title('相位差信息')
        self.phase.legend()
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)

    def updateAni(self, data):
        """绘制动画的时候每一次都会调用这个函数来更新.
        data: 每一次要绘制的数据
        """
        Y1, Y2, Y3, Y4, Y5, Y6 = data
        self.l11.set_ydata(Y1)
        self.l21.set_ydata(Y2)
        self.l31.set_ydata(Y3)
        self.l12.set_ydata(Y4)
        self.l22.set_ydata(Y5)
        self.l32.set_ydata(Y6)
        self.fig.canvas.draw()

#==========================================
# PMplCanvasWrapper
#==========================================


class MplCanvasWrapper(QDialog):
    def __init__(self):
        super().__init__()
        self.canvas = CustomFigCanvas()
        self.iPort = port
        self.strIP = ip
        vbl = QVBoxLayout()
        self.btnStart = QPushButton()
        self.btnStart.setText('开始')
        self.btnPause = QPushButton()
        self.btnPause.setText('停止')
        self.btnListen = QPushButton('开始监听')
        self.btnSetting = QPushButton('参数设置')
        gdl = QGridLayout()
        gdl.addWidget(self.btnSetting, 1, 0)
        gdl.addWidget(self.btnListen, 2, 0)
        gdl.addWidget(self.btnStart, 1, 1)
        gdl.addWidget(self.btnPause, 2, 1)
        vbl.addWidget(self.canvas)
        vbl.addLayout(gdl)
        self.setLayout(vbl)
        self.btnStart.clicked.connect(self.startPlot)  # 开始绘图
        self.btnPause.clicked.connect(self.pausePlot)  # 停止绘图
        self.btnSetting.clicked.connect(self.startSetting)
        self.btnListen.clicked.connect(self.beginListen)

    def startPlot(self):
        if hasattr(self, 'thdWorker'):
            self.thdWorker.bLive = True
        else:
            print('没有该属性!')

    def pausePlot(self):
        if hasattr(self, 'thdWorker'):
            self.thdWorker.bLive = False
        else:
            print('没有该属性!')

    def startSetting(self):
        bindPair = AddrSetting(self.strIP, self.iPort)
        if bindPair.exec_():
            self.strIP = bindPair.leIP.text()
            self.iPort = int(bindPair.lePort.text())
            print(self.strIP, ' ', self.iPort)

    def beginListen(self):
        print('准备开始监听了!')
        self.thdWorker = GenerateCSI(self.strIP, self.iPort)
        self.thdWorker.start()
        self.btnListen.setEnabled(False)
        self.btnSetting.setEnabled(False)

#==========================================
# CSILive
#==========================================
class CSILive(QDialog):
    def __init__(self, parent=None):
        super(CSILive, self).__init__(parent)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint|Qt.WindowMinimizeButtonHint|Qt.WindowCloseButtonHint)
        self.setWindowTitle('CSILive')
        self.setWindowIcon(QIcon('images/live.jpg'))
        self.live = MplCanvasWrapper()
        vbl = QVBoxLayout()
        vbl.addWidget(self.live)
        vbl.setStretch(0, 10)
        vbl.setStretch(1, 2)
        self.setLayout(vbl)
        #self.resize(1300, 800)
        self.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CSILive()
    win.show()
    sys.exit(app.exec_())



