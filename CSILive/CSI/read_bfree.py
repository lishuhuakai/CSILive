from struct import unpack, pack
import numpy as np


def expandable_or(a, b):
    """获取两个数的或.
    a: 需要操作的数a
    b: 需要操作的数b
    """
    r = a | b
    low = r & 0xff
    return unpack('b', pack('B', low))[0]


def read_bfree(array):
    """从array中读取出csi数据
    """
    result = {}
    timestamp_low = array[0] + (array[1] << 8) + (array[2] << 16) + (array[3] << 24)
    bf_count = array[4] + (array[5] << 8)
    nrx = array[8]  # 接收天线的数目
    ntx = array[9]
    rssi_a = array[10]
    rssi_b = array[11]
    rssi_c = array[12]
    # noise
    noise = unpack('b', pack('B', array[13]))[0]
    agc = array[14]
    antenna_sel = array[15]
    len = array[16] + (array[17] << 8)
    fake_rate_n_flags = array[18] + (array[19] << 8)
    calc_len = (30 * (nrx * ntx * 8 * 2 + 3) + 7) // 8
    index = 0
    payload = array[20:]

    if len != calc_len:
        print('数据发现错误!')
        exit(0)

    result['timestamp_low'] = timestamp_low
    result['bfree_count'] = bf_count
    result['rssi_a'] = rssi_a
    result['rssi_b'] = rssi_b
    result['rssi_c'] = rssi_c
    result['nrx'] = nrx
    result['ntx'] = ntx
    result['agc'] = agc
    result['rate'] = fake_rate_n_flags
    result['noise'] = noise

    csi = np.zeros((ntx, nrx, 30), dtype=np.complex64)
    # 现在开始构建numpy array
    idx = 0        # 下标
    remainder = 0  # 余数
    for sub_idx in range(30):
        idx = idx + 3
        remainder = idx % 8
        for r in range(nrx):
            for t in range(ntx):
                real = expandable_or((payload[idx // 8] >> remainder), (payload[idx // 8 + 1] << (8 - remainder)))
                img = expandable_or((payload[idx // 8 + 1] >> remainder), (payload[idx // 8 + 2] << (8 - remainder)))
                csi[t, r, sub_idx] = complex(real, img)     # 构建一个复数
                idx = idx + 16
    result['csi'] = csi
    # 这里稍微做了一点修改
    perm = np.zeros(3, dtype=np.uint32)
    perm[0] = (antenna_sel & 0x3) + 1
    perm[1] = ((antenna_sel >> 2) & 0x3) + 1
    perm[2] = ((antenna_sel >> 4) & 0x3) + 1

    result['perm'] = perm
    return result