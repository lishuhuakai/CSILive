import numpy as np
from CSI.read_bfree import read_bfree
from CSI.scaled_csi import scaled_csi
from struct import unpack


def extract_csi(file_name):
    """抽取出csi信息.
    file_name: 文件的名称
    """
    triangle = np.array([1, 3, 6])
    csis = []
    with open(file_name, 'rb') as f:
        buff = f.read()
        curr = 0    # 记录当前已经处理到了的位置
        length = len(buff)
        while curr < (length - 3):
            data_len = unpack('>H', buff[curr:curr+2])[0]  # 实际长度
            if data_len > (length - curr - 2):  # 防止越界的错误
                break
            code = unpack('B', buff[curr+2:curr+3])[0] # 代码
            curr = curr + 3
            if code == 187:
                data = read_bfree(buff[curr:])
                perm = data['perm']
                nrx = data['nrx']
                csi = data['csi']
                if sum(perm) == triangle[nrx - 1]:  # 下标从0开始
                    csi[:, perm - 1, :] = csi[:, [x for x in range(nrx)], :]
                #csi = scaled_csi(data)
                csis.append(data)
                #print('len(csis) = ', len(csis))
            curr = curr + data_len - 1
    return csis


def extract_csi_matrix(csis):
    nums = len(csis)
    carriers = 30
    matrix = np.zeros((3, carriers, len), dtype=np.complex64)
    for at in range(3):
        for i in range(len):
            csi = csis[i]['csi']
            csi = scaled_csi(csis[i])
            for j in range(carriers):
                matrix[at, j, i] = csi[0, at, j]
    return matrix


def handle_csi(file_name, sample_rate):
    """处理csi数据.
    sample_rate: 采样率,实际上指的是每秒钟接收包的个数.
    file_name: 文件的名称.
    """
    csis = extract_csi(file_name)
    nums = len(csis)  # 接收到数据的个数
    start = sample_rate * 10  # 去掉前10秒的数据
    end = nums - (nums % sample_rate) - sample_rate * 8 - 1  # 去除后8秒
    carriers = 30   # 一共有30路负载
    csi_data = np.zeros((carriers, end - start + 1), dtype=np.complex64)

    for i in range(start, end + 1):
        csi = csis[i]['csi']
        csi = scaled_csi(csis[i])
        for j in range(carriers):
            csi_data[j, i - start] = csi[0, 0, j]  # 这里实际上只用了第一根天线的数据
    return csi_data



