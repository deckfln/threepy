"""
Javascript compatible arrays
"""
import numpy as np


def Uint8Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'B')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        return np.fromstring(src[byteOffset:byteOffset + count], np.uint8)
    else:
        return np.zeros(int(size), 'B')


def Int8Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'b')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        return np.fromstring(src[byteOffset:byteOffset + count], np.int8)
    else:
        return np.zeros(int(size), 'b')


def Uint8ClampedArray(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'B')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        return np.fromstring(src[byteOffset:byteOffset + count], np.uint8)
    else:
        return np.zeros(int(size), 'B')


def Int16Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'h')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 2
        return np.fromstring(src[byteOffset:byteOffset + count], np.int16)
    else:
        return np.zeros(int(size), 'h')


def Uint16Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'H')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 2
        return np.fromstring(src[byteOffset:byteOffset + count], np.uint16)
    else:
        return np.zeros(int(size), 'H')


def Int32Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'l')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 4
        return np.fromstring(src[byteOffset:byteOffset + count], np.int32)
    else:
        return np.zeros(int(size), dtype=np.int32)


def Uint32Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, dtype=np.uint32)
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 4
        return np.fromstring(src[byteOffset:byteOffset + count], np.uint32)
    else:
        return np.zeros(int(size), dtype=np.uint32)


def Float32Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, np.float32)
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 4
        return np.fromstring(src[byteOffset:byteOffset + count], np.float32)
    else:
        return np.zeros(int(size), np.float32)


def Float64Array(size, byteOffset=0, count=-1):
    if isinstance(size, list):
        return np.array(size, 'd')
    elif isinstance(size, bytes):
        src = size
        if count < 0:
            count = len(src)
        else:
            count *= 8
        return np.fromstring(src[byteOffset:byteOffset + count], np.float64)
    else:
        return np.zeros(int(size), 'd')

