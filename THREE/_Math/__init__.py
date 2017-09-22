import math
import array
import random

DEG2RAD= math.pi / 180
RAD2DEG= 180 / math.pi

def generateUUID():
    # // http://www.broofa.com/Tools/Math.uuid.htm

    chars = '0*1*2*3*4*5*6*7*8*9*A*B*C*D*E*F*G*H*I*J*K*L*M*N*O*P*Q*R*S*T*U*V*W*X*Y*Z*a*b*c*d*e*f*g*h*i*j*k*l*m*n*o*p*q*r*s*t*u*v*w*x*y*z'.split( '*' )
    uuid = [0 for a in range(36) ]
    rnd = 0

    for i in range(36):
        if i == 8 or i == 13 or i == 18 or i == 23:
            uuid[ i ] = '-'
        elif i == 14:
            uuid[ i ] = '4'
        else:
            if rnd <= 0x02:
                rnd = int(0x2000000 + ( random.random() * 0x1000000 )) or 0
            r = rnd & 0xf
            rnd = rnd >> 4
            if i== 19:
                uuid[ i ] = chars[ (r & 0x3 ) | 0x8]
            else:
                uuid[ i ] = chars[ r ]

    return ''.join(uuid)


def clamp( value, min, max ):
    return max( min, min( max, value ) )


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
    if x <= min: return 0
    if x >= max: return 1

    x = ( x - min ) / ( max - min )

    return x * x * ( 3 - 2 * x )


def smootherstep( x, min, max ):
    if x <= min: return 0
    if x >= max: return 1

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
    return degrees * _Math.DEG2RAD


def radToDeg( radians ):
    return radians * _Math.RAD2DEG


def isPowerOfTwo( value ):
    return ( value & ( value - 1 ) ) == 0 and value != 0


def nearestPowerOfTwo( value ):
    return math.pow( 2, round( math.log( value ) / math.log(2) ) )


def nextPowerOfTwo( value ):
    value -= 1
    value |= value >> 1
    value |= value >> 2
    value |= value >> 4
    value |= value >> 8
    value |= value >> 16
    value += 1

    return value