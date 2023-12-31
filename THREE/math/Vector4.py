"""
/**
 * @author supereggbert / http://www.paulbrunt.co.uk/
 * @author philogb / http://blog.thejit.org/
 * @author mikael emtinger / http://gomo.se/
 * @author egraether / http://egraether.com/
 * @author WestLangley / http://github.com/WestLangley
 */
"""
import math
from THREE.pyOpenGLObject import *


class Vector4(pyOpenGLObject):
    isVector4 = True

    def __init__(self, x=0, y=0, z=0, w=None ):
        super().__init__()
        self.set_class(isVector4)

        self.x = x
        self.y = y
        self.z = z
        self.w = 1
        if w is not None:
            self.w = w


    def set(self, x, y, z, w ):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

        return self

    def setScalar(self, scalar ):
        self.x = scalar
        self.y = scalar
        self.z = scalar
        self.w = scalar

        return self

    def setX(self, x ):
        self.x = x

        return self

    def setY(self, y ):
        self.y = y

        return self

    def setZ(self, z ):
        self.z = z

        return self

    def setW(self, w ):
        self.w = w

        return self

    def setComponent(self, index, value ):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index ==  2: 
            self.z = value
        elif index ==  3:
            self.w = value
        else:
            raise ( 'index is out of range: ' + index )

        return self

    def getComponent(self, index ):
        if index == 0:
            return self.x
        elif index == 1: 
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        else:
            raise( 'index is out of range: ' + index )

    def clone(self,):
        return type(self)( self.x, self.y, self.z, self.w )

    def copy(self, v ):
        self.x = v.x
        self.y = v.y
        self.z = v.z
        self.w = 1
        if v.w is not None:
            self.w = v.w

        return self

    def add(self, v, w=None ):
        if  w is not None:
            print( 'THREE.Vector4: .add() now only accepts one argument. Use .addVectors( a, b ) instead.' )
            return self.addVectors( v, w )

        self.x += v.x
        self.y += v.y
        self.z += v.z
        self.w += v.w

        return self

    def addScalar(self, s ):
        self.x += s
        self.y += s
        self.z += s
        self.w += s

        return self

    def addVectors(self, a, b ):
        self.x = a.x + b.x
        self.y = a.y + b.y
        self.z = a.z + b.z
        self.w = a.w + b.w

        return self

    def addScaledVector(self, v, s ):
        self.x += v.x * s
        self.y += v.y * s
        self.z += v.z * s
        self.w += v.w * s

        return self

    def sub(self, v, w=None ):
        if  w is not None:
            print( 'THREE.Vector4: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.' )
            return self.subVectors( v, w )

        self.x -= v.x
        self.y -= v.y
        self.z -= v.z
        self.w -= v.w

        return self

    def subScalar(self, s ):
        self.x -= s
        self.y -= s
        self.z -= s
        self.w -= s

        return self

    def subVectors(self, a, b ):
        self.x = a.x - b.x
        self.y = a.y - b.y
        self.z = a.z - b.z
        self.w = a.w - b.w

        return self

    def multiplyScalar(self, scalar ):
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        self.w *= scalar

        return self

    def applyMatrix4(self, m ):
        x = self.x; y = self.y; z = self.z; w = self.w
        e = m.elements

        self.x = e[ 0 ] * x + e[ 4 ] * y + e[ 8 ] * z + e[ 12 ] * w
        self.y = e[ 1 ] * x + e[ 5 ] * y + e[ 9 ] * z + e[ 13 ] * w
        self.z = e[ 2 ] * x + e[ 6 ] * y + e[ 10 ] * z + e[ 14 ] * w
        self.w = e[ 3 ] * x + e[ 7 ] * y + e[ 11 ] * z + e[ 15 ] * w

        return self

    def divideScalar(self, scalar ):
        return self.multiplyScalar( 1 / scalar )

    def setAxisAngleFromQuaternion(self, q ):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/index.htm
        # // q is assumed to be normalized
        self.w = 2 * math.acos( q.w )
        s = math.sqrt( 1 - q.w * q.w )

        if  s < 0.0001:
            self.x = 1
            self.y = 0
            self.z = 0
        else:
            self.x = q.x / s
            self.y = q.y / s
            self.z = q.z / s
        return self

    def setAxisAngleFromRotationMatrix(self, m ):
        # // http://www.euclideanspace.com/maths/geometry/rotations/conversions/matrixToAngle/index.htm
        # // assumes the upper 3x3 of m is a pure rotation matrix (i.e, unscaled)
        epsilon = 0.01        # // margin to allow for rounding errors
        epsilon2 = 0.1        # // margin to distinguish between 0 and 180 degrees

        te = m.elements

        m11 = te[ 0 ]; m12 = te[ 4 ]; m13 = te[ 8 ],
        m21 = te[ 1 ]; m22 = te[ 5 ]; m23 = te[ 9 ],
        m31 = te[ 2 ]; m32 = te[ 6 ]; m33 = te[ 10 ]

        if  abs( m12 - m21 ) < epsilon and\
             abs( m13 - m31 ) < epsilon and\
             abs( m23 - m32 ) < epsilon:

            # // singularity found
            # // first check for identity matrix which must have +1 for all terms
            # // in leading diagonal and zero in other terms
            if  ( abs( m12 + m21 ) < epsilon2 ) and\
                 ( abs( m13 + m31 ) < epsilon2 ) and\
                 ( abs( m23 + m32 ) < epsilon2 ) and\
                 ( abs( m11 + m22 + m33 - 3 ) < epsilon2 ):

                # // self singularity is identity matrix so angle = 0

                self.set( 1, 0, 0, 0 )

                return self    # // zero angle, arbitrary axis

            # // otherwise self singularity is angle = 180
            angle = math.pi

            xx = ( m11 + 1 ) / 2
            yy = ( m22 + 1 ) / 2
            zz = ( m33 + 1 ) / 2
            xy = ( m12 + m21 ) / 4
            xz = ( m13 + m31 ) / 4
            yz = ( m23 + m32 ) / 4

            if  ( xx > yy ) and ( xx > zz ):
                # // m11 is the largest diagonal term
                if  xx < epsilon:
                    x = 0
                    y = 0.707106781
                    z = 0.707106781
                else:
                    x = math.sqrt( xx )
                    y = xy / x
                    z = xz / x
            elif  yy > zz:
                # // m22 is the largest diagonal term
                if  yy < epsilon:
                    x = 0.707106781
                    y = 0
                    z = 0.707106781
                else:
                    y = math.sqrt( yy )
                    x = xy / y
                    z = yz / y
            else:
                # // m33 is the largest diagonal term so base result on self
                if  zz < epsilon:
                    x = 0.707106781
                    y = 0.707106781
                    z = 0
                else:
                    z = math.sqrt( zz )
                    x = xz / z
                    y = yz / z

            self.set( x, y, z, angle )

            return self    # // return 180 deg rotation

        # // as we have reached here there are no singularities so we can handle normally

        s = math.sqrt( ( m32 - m23 ) * ( m32 - m23 ) +\
                           ( m13 - m31 ) * ( m13 - m31 ) +\
                           ( m21 - m12 ) * ( m21 - m12 ) ); # // used to normalize

        if  abs( s ) < 0.001:
            s = 1

        # // prevent divide by zero, should not happen if matrix is orthogonal and should be
        # // caught by singularity test above, but I've left it in just in case
        self.x = ( m32 - m23 ) / s
        self.y = ( m13 - m31 ) / s
        self.z = ( m21 - m12 ) / s
        self.w = math.acos( ( m11 + m22 + m33 - 1 ) / 2 )

        return self

    def min(self, v ):
        self.x = min( self.x, v.x )
        self.y = min( self.y, v.y )
        self.z = min( self.z, v.z )
        self.w = min( self.w, v.w )

        return self

    def max(self, v ):
        self.x = max( self.x, v.x )
        self.y = max( self.y, v.y )
        self.z = max( self.z, v.z )
        self.w = max( self.w, v.w )

        return self

    def clamp(self, min, max ):
        # // assumes min < max, componentwise
        self.x = max( min.x, min( max.x, self.x ) )
        self.y = max( min.y, min( max.y, self.y ) )
        self.z = max( min.z, min( max.z, self.z ) )
        self.w = max( min.w, min( max.w, self.w ) )

        return self

    def clampScalar(self, minVal, maxVal ):
        min = Vector4()
        max = Vector4()

        min.set( minVal, minVal, minVal, minVal )
        max.set( maxVal, maxVal, maxVal, maxVal )

        return self.clamp( min, max )

    def clampLength(self, min, max ):
        length = self.length()

        return self.divideScalar( length or 1 ).multiplyScalar( max( min, min( max, length ) ) )

    def floor(self):
        self.x = math.floor( self.x )
        self.y = math.floor( self.y )
        self.z = math.floor( self.z )
        self.w = math.floor( self.w )

        return self

    def ceil(self):
        self.x = math.ceil( self.x )
        self.y = math.ceil( self.y )
        self.z = math.ceil( self.z )
        self.w = math.ceil( self.w )

        return self

    def round(self):
        self.x = round( self.x )
        self.y = round( self.y )
        self.z = round( self.z )
        self.w = round( self.w )

        return self

    def roundToZero(self):
        self.x = math.floor( self.x )
        if self.x < 0:
            self.x = math.ceil( self.x )
        self.y = math.floor( self.y )
        if self.y < 0:
            self.y = math.ceil( self.y )
        self.z = math.floor( self.z )
        if self.z < 0:
            self.z = math.ceil( self.z )
        self.w = math.floor( self.w )
        if self.w < 0:
            self.w = math.ceil( self.w )

        return self

    def negate(self):
        self.x = - self.x
        self.y = - self.y
        self.z = - self.z
        self.w = - self.w

        return self

    def dot(self, v ):
        return self.x * v.x + self.y * v.y + self.z * v.z + self.w * v.w

    def lengthSq(self):
        return self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w

    def length(self):
        return math.sqrt( self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w )

    def manhattanLength(self):
        return abs( self.x ) + abs( self.y ) + abs( self.z ) + abs( self.w )

    def normalize(self):
        return self.divideScalar( self.length() or 1 )

    def setLength(self, length ):
        return self.normalize().multiplyScalar( length )

    def lerp(self, v, alpha ):
        self.x += ( v.x - self.x ) * alpha
        self.y += ( v.y - self.y ) * alpha
        self.z += ( v.z - self.z ) * alpha
        self.w += ( v.w - self.w ) * alpha

        return self

    def lerpVectors(self, v1, v2, alpha ):
        return self.subVectors( v2, v1 ).multiplyScalar( alpha ).add( v1 )

    def equals(self, v ):
        return ( v.x == self.x ) and ( v.y == self.y ) and ( v.z == self.z ) and ( v.w == self.w )

    def fromArray(self, array, offset=0 ):
        self.x = array[ offset ]
        self.y = array[ offset + 1 ]
        self.z = array[ offset + 2 ]
        self.w = array[ offset + 3 ]

        return self

    def toArray(self, array=None, offset=0 ):
        if  array is None:
            array = []

        array[ offset ] = self.x
        array[ offset + 1 ] = self.y
        array[ offset + 2 ] = self.z
        array[ offset + 3 ] = self.w

        return array

    def fromBufferAttribute(self, attribute, index, offset=None ):
        if  offset is not None:
            print( 'THREE.Vector4: offset has been removed from .fromBufferAttribute().' )

        self.x = attribute.getX( index )
        self.y = attribute.getY( index )
        self.z = attribute.getZ( index )
        self.w = attribute.getW( index )

        return self