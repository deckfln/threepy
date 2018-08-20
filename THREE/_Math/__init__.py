import math
import array
import sys
import random

from THREE.cython.cthree import *

DEG2RAD = math.pi / 180
RAD2DEG = 180 / math.pi

cython = True

_lut = [('0' if i < 16 else '') + hex(i) for i in range(256)]


def generateUUID():
    # http://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid-in-javascript/21963136#21963136
    global _lut
    d0 = int(random.random() * 0xffffffff) | 0
    d1 = int(random.random() * 0xffffffff) | 0
    d2 = int(random.random() * 0xffffffff) | 0
    d3 = int(random.random() * 0xffffffff) | 0
    uuid = _lut[ d0 & 0xff ] + _lut[ d0 >> 8 & 0xff ] + _lut[ d0 >> 16 & 0xff ] + _lut[ d0 >> 24 & 0xff ] + '-' + \
        _lut[ d1 & 0xff ] + _lut[ d1 >> 8 & 0xff ] + '-' + _lut[ d1 >> 16 & 0x0f | 0x40 ] + _lut[ d1 >> 24 & 0xff ] + '-' + \
        _lut[ d2 & 0x3f | 0x80 ] + _lut[ d2 >> 8 & 0xff ] + '-' + _lut[ d2 >> 16 & 0xff ] + _lut[ d2 >> 24 & 0xff ] + \
        _lut[ d3 & 0xff ] + _lut[ d3 >> 8 & 0xff ] + _lut[ d3 >> 16 & 0xff ] + _lut[ d3 >> 24 & 0xff ]

    # .toUpperCase() here flattens concatenated strings to save heap memory space.
    return uuid.upper()


def _clamp( value, mi, mx ):
    return max( mi, min( mx, value ) )


def clamp( value, mi, mx ):
    if cython:
        return cMath_clamp( value, mi, mx )
    else:
        return _clamp(value, mi, mx)


# // compute euclidian modulo of m % n
# // https://en.wikipedia.org/wiki/Modulo_operation
def euclideanModulo( n, m ):
    return ( ( n % m ) + m ) % m


# // Linear mapping from range <a1, a2> to range <b1, b2>
def mapLinear( x, a1, a2, b1, b2 ):
    return b1 + ( x - a1 ) * ( b2 - b1 ) / ( a2 - a1 )


# // https://en.wikipedia.org/wiki/Linear_interpolation
def lerp( x, y, t ):
    return ( 1 - t ) * x + t * y


# // http://en.wikipedia.org/wiki/Smoothstep
def smoothstep( x, min, max ):
    if x <= min:
        return 0
    if x >= max:
        return 1

    x = ( x - min ) / ( max - min )

    return x * x * ( 3 - 2 * x )


def smootherstep( x, min, max ):
    if x <= min:
        return 0
    if x >= max:
        return 1

    x = ( x - min ) / ( max - min )

    return x * x * x * ( x * ( x * 6 - 15 ) + 10 )


# // Random integer from <low, high> interval
def randInt( low, high ):
    return low + math.floor( random.random() * ( high - low + 1 ) )


# // Random float from <low, high> interval
def randFloat( low, high ):
    return low + random.random() * ( high - low )


# // Random float from <-range/2, range/2> interval
def randFloatSpread( range ):
    return range * ( 0.5 - random.random() )


def degToRad( degrees ):
    global DEG2RAD
    return degrees * DEG2RAD


def radToDeg( radians ):
    global RAD2DEG
    return radians * RAD2DEG


def isPowerOfTwo( value ):
    return ( value & ( value - 1 ) ) == 0 and value != 0


def ceilPowerOfTwo( value ):
    return math.pow( 2, math.ceil( math.log( value ) / math.log(2) ) )


def floorPowerOfTwo( value ):
    return math.pow(2, math.floor(math.log(value) / math.LN2))
