"""

"""
import numpy as np


def Float32Array(size):
    if isinstance(size, list):
        return np.zeros(size, 'f')
    else:
        return np.zeros(int(size), 'f')


def Uint16Array(size):
    if isinstance(size, list):
        return np.array(size, 'H')
    else:
        return np.zeros(int(size), 'H')


def Uint8Array(size):
    if isinstance(size, list):
        return np.array(size, 'B')
    else:
        return np.zeros(int(size), 'B')
