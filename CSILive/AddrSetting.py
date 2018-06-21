from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import re


class AddrSetting(QDialog):
    reIP = re.compile("^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$")

    def __init__(self, ip='127.0.0.1', port=8090, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('设置监听的地址')
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon('images/setting.ico'))
        vbl = QVBoxLayout()
        self.lbl1 = QLabel("请输入地址：")
        self.leIP = QLineEdit()
        self.leIP.setText(ip)
        self.lbl2 = QLabel("请输入端口号: ")
        self.lePort = QLineEdit()
        self.lePort.setText(str(port))
        self.btn1 = QPushButton('取消')
        self.btn2 = QPushButton('确认')
        hbl = QHBoxLayout()
        hbl.addWidget(self.btn1)
        hbl.addWidget(self.btn2)
        vbl.addWidget(self.lbl1)
        vbl.addWidget(self.leIP)
        vbl.addWidget(self.lbl2)
        vbl.addWidget(self.lePort)
        vbl.addLayout(hbl)
        self.setLayout(vbl)

        self.btn2.clicked.connect(self.validateInput)
        self.btn1.clicked.connect(self.reject)

    def validateInput(self):
        ip = self.leIP.text()
        if not self.reIP.match(ip):
            QMessageBox.warning(self, '警告', '输入的ip地址不规范.')
            return
        try:
            port = int(self.lePort.text())
        except ValueError as e:
            QMessageBox.warning(self, '警告', '输入的端口不是数字.')
            return

        if port < 1 or port > 65535:
            QMessageBox.warning(self, '警告', '端口范围在1~65535之间.')
            return
        self.accept()