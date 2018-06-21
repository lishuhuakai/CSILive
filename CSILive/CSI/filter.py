"""
    这个文件主要用于信号的过滤
"""
import numpy as np
import math
import scipy.signal as signal
import matplotlib.pyplot as plt


def amp_filter(amp_matrix):
    """
    过滤掉一些高频的幅度信息
    Args:
        amp_info 幅度矩阵
    Returns:
        过滤过后的幅度矩阵
    """
    def draw_pic(Ys):
        """
        绘制简单的演示图片.
        Args:
            Y: 一个包含所有要展示的Y的list
        """
        # 开始绘制图片
        assert(len(Ys) != 0)
        X = np.array(range(Ys[0].shape[0]))
        for Y in Ys:
            plt.plot(X, Y)
        plt.show()

    filtered_amp = np.zeros(amp_matrix.shape)
    rows = amp_matrix.shape[0]  # 矩阵的行数
    cols = amp_matrix.shape[1]  # 矩阵的列数

    b, a = signal.butter(2, 0.02, 'low')  # 低通过滤器
    for i in range(rows):
        carrier_data = amp_matrix[i]   # 获取每一路负载上的幅度信息
        # 然后进行过滤
        sf1 = signal.filtfilt(b, a, carrier_data)  # 过滤后的数据,事实上,我觉得这个过滤器效果更好
        sf = signal.lfilter(b, a, carrier_data) # 原始文件中采用的过滤器
        draw_pic([carrier_data, sf, sf1])
        filtered_amp[i] = sf
    print("OK!")
    return filtered_amp


def phase_transform(phase_matrix):
    """
    对周期的信息进行调整
    Args:
        phase_matrix: 关于周期信息的矩阵.
    Returns:
        调整过后的周期信息矩阵.
    """
    tuned_phase = np.zeros(phase_matrix.shape)
    rows = phase_matrix.shape[0]  # 矩阵的行数
    cols = phase_matrix.shape[1]  # 矩阵的列数

    for i in range(cols): # 对每一列数据进行调整
        diff = 0
        tuned_phase[0, i] = phase_matrix[0, i]
        for j in range(1, rows):
            if phase_matrix[j, i] - phase_matrix[j - 1, i] > math.pi:  # 周期超过pi
                diff += 1
            # 问题其实是存在的,并不是所有的波的周期都是2 * pi
            tuned_phase[j, i] = phase_matrix[j, i] - diff * 2 * math.pi # 这里做的事情其实就是让所有的周期对齐

    transformed_phase = np.zeros(phase_matrix.shape)
    m = [-28, -26, -24, -22, -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, -1, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28]
    for i in range(cols):
        k = (tuned_phase[rows - 1, i] - tuned_phase[0, i]) / (m[rows - 1] - m[0])
        b = np.sum(tuned_phase[:, i]) / rows
        for j in range(rows):
            transformed_phase[j, i] = tuned_phase[j, i] - k * m[j] - b
    return transformed_phase




