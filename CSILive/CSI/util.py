"""
    这个文件主要包括了一些常用的函数,比如加载mat文件等.
"""

import numpy as np
import os
from scipy import io as spio

colors = [
    '#CE0000', '#00DB00', '#0072E3', '#6C3365', '#000000',
    '#FF69B4', '#FF0000',
    '#800080', '#2E8B57', '#F4A460', '#0000ff', '#8a2be2',
    '#a52a2a', '#deb887', '#5f9ea0', '#7fff00', '#d269e1',
    '#ff7350', '#6495ed', '#fff8dc', '#dc143c', '#00ffff',
    '#00008b', '#008b8b', '#b8860b', '#a9a9a9', '#006400',
    '#bdb76b', '#8b008b', '#556b2f', '#ff8c00', '#2F4F4F',
    '#9932CC', '#8B0000', '#E9967A', '#8FBC8F', '#483D8B',
    '#FF1493', '#00BFFF',  '#1E90FF', '#D19275',
    '#228B22', '#FF00FF', '#FFD700',
    '#DAA520', '#808080', '#008000', '#ADFF2F',
    '#CD5C5C', '#4B0082', '#F0E68C', '#E6E6FA',
    '#7CFC00', '#ADD8E6', '#F08080',
    '#D3D3D3', '#90EE90', '#FFA07A', '#20B2AA',
    '#8470FF', '#778899', '#B0C4DE', '#00FF00',
    '#FF00FF', '#800000', '#66CDAA', '#0000CD',
    '#9370D8', '#3CB371', '#7B68EE', '#00FA9A',
    '#191970', '#FFDEAD', '#000080',
    '#808000', '#6B8E23', '#FFA500', '#FF4500',
    '#EEE8AA', '#98FB98', '#AFEEEE', '#FFDAB9',
    '#CD853F', '#FFC0CB', '#DDA0DD', '#B0E0E6',
    '#BC8F8F', '#4169E1', '#8B4513', '#FA8072',
    '#A0522D', '#C0C0C0', '#87CEEB', '#6A5ACD', '#708090',
    '#00FF7F', '#D2B48C', '#008080', '#D8BFD8',
    '#FF6347', '#40E0D0', '#EE82EE', '#D02090',

]


def fill_neg_inf(matrix):
    """填充掉负无穷大.
    matrix: 放入的矩阵
    """
    rows = matrix.shape[0]
    for i in range(rows):
        ith_row = matrix[i]
        idx = ith_row == -np.Inf  # 记录下下标
        ith_row[idx] = 0
        ith_row[idx] = np.mean(ith_row)
    return matrix


def load_mat(path):
    """加载.mat文件
    Args:
        path: 文件所在的路径.
    Yields:
        每次读取一份数据.
    """
    names = os.listdir(path)
    for name in names:
        if name.endswith('.mat'):  # 只处理以.mat结尾的文件
            data = spio.loadmat(path + name) # 加载文件
            yield name, data['DataSample']


def extract_amp(mat):
    """从原始的mat文件中抽取出幅度的信息.
    Args:
        mat: 原始的mat矩阵
    Returns:
        矩阵中的幅度信息.
    """
    amp = np.zeros(mat.shape)
    for i in range(mat.shape[0]):
        amp[i] = 20 * np.log10(np.abs(mat[i].T))
        fill_neg_inf(amp)  # 将-Inf填充掉
    return amp


