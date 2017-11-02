"""

"""
import numpy as np


def Uint8Array(size):
    if isinstance(size, list):
        return np.array(size, 'B')
    elif isinstance(size, bytes):
        return np.fromstring(size, np.uint8)
    else:
        return np.zeros(int(size), 'B')


def Int8Array(size):
    if isinstance(size, list):
        return np.array(size, 'b')
    else:
        return np.zeros(int(size), 'b')


def Uint8ClampedArray(size):
    if isinstance(size, list):
        return np.array(size, 'B')
    else:
        return np.zeros(int(size), 'B')


def Int16Array(size):
    if isinstance(size, list):
        return np.array(size, 'h')
    else:
        return np.zeros(int(size), 'h')


def Uint16Array(size):
    if isinstance(size, list):
        return np.array(size, 'H')
    else:
        return np.zeros(int(size), 'H')


def Int32Array(size):
    if isinstance(size, list):
        return np.array(size, 'l')
    else:
        return np.zeros(int(size), 'l')


def Uint32Array(size):
    if isinstance(size, list):
        return np.array(size, 'L')
    else:
        return np.zeros(int(size), 'L')


def Float32Array(size):
    if isinstance(size, list):
        return np.array(size, 'f')
    else:
        return np.zeros(int(size), 'f')


def Float64Array(size):
    if isinstance(size, list):
        return np.array(size, 'd')
    else:
        return np.zeros(int(size), 'd')

