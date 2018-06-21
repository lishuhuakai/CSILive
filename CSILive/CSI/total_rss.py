import numpy as np


def dbinv(x):
    return 10**(x / 10)


def total_rss(data):
    rssi_mag = 0
    if data['rssi_a'] != 0:
        rssi_mag = rssi_mag + dbinv(data['rssi_a'])
    if data['rssi_b'] != 0:
        rssi_mag = rssi_mag + dbinv(data['rssi_b'])
    if data['rssi_c'] != 0:
        rssi_mag = rssi_mag + dbinv(data['rssi_c'])
    return 10 * np.log10(rssi_mag) - 44 - data['agc']