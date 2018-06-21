import numpy as np
from CSI.total_rss import total_rss, dbinv
from math import sqrt


def scaled_csi(data):
    """对得到的csi数据进行标准化
    """
    csi = data['csi']
    ntx = data['ntx']
    nrx = data['nrx']

    csi_sq = csi * np.conj(csi)
    csi_pwr = csi_sq.sum().real  # 求和
    rssi_pwr = dbinv(total_rss(data))
    # scale CSI -> Signal power : rssi_pwr / (mean of csi_pwr)
    scale = rssi_pwr / (csi_pwr / 30)

    # Thermal noise might be undefined if the trace was
    # captured in monitor mode
    # ... If so, set it to -92
    if data['noise'] == -127:
        noise = -92
    else:
        noise = data['noise']
    thermal_noise_pwr = dbinv(noise)

    quant_error_pwr = scale * (nrx * ntx)
    total_noise_pwr = thermal_noise_pwr + quant_error_pwr
    ret = csi * sqrt(scale / total_noise_pwr)

    if ntx == 2:
        ret = ret * sqrt(2)
    elif ntx == 3:
        ret = ret * sqrt(dbinv(4.5))

    return ret
