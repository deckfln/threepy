"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author kile / http://kile.stravaganza.org/
     * @author philogb / http://blog.thejit.org/
     * @author mikael emtinger / http://gomo.se/
     * @author egraether / http://egraether.com/
     * @author WestLangley / http://github.com/WestLangley
     */
"""
import math
from THREE.Quaternion import *
from THREE.Matrix4 import *
import THREE._Math as _Math
from THREE.pyOpenGLObject import *
from numba import jit


class Vector3(pyOpenGLObject):
    isVector3 = True

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, x, y, z ):
        self.x = x
        self.y = y
        self.z = z

        return self

    def setScalar(self, scalar ):
        self.x = scalar
        self.y = scalar
        self.z = scalar
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

    def setComponent(self, index, value ):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        elif index == 'x':
            self.x = value
        elif index == 'y':
            self.y = value
        elif index == 'z':
            self.z = value
        else:
            print( 'index is out of range: ' + index )

        return self

    def getComponent(self, index ):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            print( 'index is out of range: ' + index )

    def clone(self):
        return type(self)( self.x, self.y, self.z )

    def copy(self, v ):
        self.x = v.x
        self.y = v.y
        self.z = v.z
        return self

    @jit(cache=True)
    def add(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .add() now only accepts one argument. Use .addVectors( a, b ) instead.' )
            return self.addVectors( v, w )

        self.x += v.x
        self.y += v.y
        self.z += v.z

        return self

    @jit(cache=True)
    def addScalar(self, s ):
        self.x += s
        self.y += s
        self.z += s
        return self

    @jit(cache=True)
    def addVectors(self, a, b ):
        self.x = a.x + b.x
        self.y = a.y + b.y
        self.z = a.z + b.z
        return self

    @jit(cache=True)
    def addScaledVector(self, v, s ):
        self.x += v.x * s
        self.y += v.y * s
        self.z += v.z * s
        return self

    @jit(cache=True)
    def sub(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.' )
            return self.subVectors( v, w )

        self.x -= v.x
        self.y -= v.y
        self.z -= v.z
        return self

    @jit(cache=True)
    def subScalar(self, s ):
        self.x -= s
        self.y -= s
        self.z -= s
        return self

    @jit(cache=True)
    def subVectors(self, a, b ):
        self.x = a.x - b.x
        self.y = a.y - b.y
        self.z = a.z - b.z
        return self

    @jit(cache=True)
    def multiply(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .multiply() now only accepts one argument. Use .multiplyVectors( a, b ) instead.' )
            return self.multiplyVectors( v, w )

        self.x *= v.x
        self.y *= v.y
        self.z *= v.z
        return self

    @jit(cache=True)
    def multiplyScalar(self, scalar ):
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    @jit(cache=True)
    def multiplyVectors(self, a, b ):
        self.x = a.x * b.x
        self.y = a.y * b.y
        self.z = a.z * b.z
        return self

    @jit(cache=True)
    def applyEuler(self, euler):
        quaternion = Quaternion()
        if not( euler and euler.isEuler):
            print( 'THREE.Vector3: .applyEuler() now expects an Euler rotation rather than a Vector3 and order.' )

        return self.applyQuaternion( quaternion.setFromEuler( euler ) )

    @jit(cache=True)
    def applyAxisAngle(self, axis, angle):
        quaternion = Quaternion()
        return self.applyQuaternion( quaternion.setFromAxisAngle( axis, angle ) )

    @jit(cache=True)
    def applyMatrix3(self, m ):
        x = self.x; y = self.y; z = self.z
        e = m.elements

        self.x = e[ 0 ] * x + e[ 3 ] * y + e[ 6 ] * z
        self.y = e[ 1 ] * x + e[ 4 ] * y + e[ 7 ] * z
        self.z = e[ 2 ] * x + e[ 5 ] * y + e[ 8 ] * z

        return self

    @jit(cache=True)
    def applyMatrix4(self, m ):
        x = self.x; y = self.y; z = self.z
        e = m.elements

        if e[ 3 ] * x + e[ 7 ] * y + e[ 11 ] * z + e[ 15 ] == 0:
            self.z = float("-inf")
            return self

        w = 1 / ( e[ 3 ] * x + e[ 7 ] * y + e[ 11 ] * z + e[ 15 ] )

        self.x = ( e[ 0 ] * x + e[ 4 ] * y + e[ 8 ]  * z + e[ 12 ] ) * w
        self.y = ( e[ 1 ] * x + e[ 5 ] * y + e[ 9 ]  * z + e[ 13 ] ) * w
        self.z = ( e[ 2 ] * x + e[ 6 ] * y + e[ 10 ] * z + e[ 14 ] ) * w

        return self

    @jit(cache=True)
    def applyQuaternion(self, q ):
        x = self.x; y = self.y; z = self.z
        qx = q.x; qy = q.y; qz = q.z; qw = q.w

        # # // calculate quat * vector

        ix =  qw * x + qy * z - qz * y
        iy =  qw * y + qz * x - qx * z
        iz =  qw * z + qx * y - qy * x
        iw = - qx * x - qy * y - qz * z

        # # // calculate result * inverse quat

        self.x = ix * qw + iw * - qx + iy * - qz - iz * - qy
        self.y = iy * qw + iw * - qy + iz * - qx - ix * - qz
        self.z = iz * qw + iw * - qz + ix * - qy - iy * - qx

        return self

    @jit(cache=True)
    def project(self, camera):
        matrix = Matrix4()
        matrix.multiplyMatrices( camera.projectionMatrix, matrix.getInverse( camera.matrixWorld ) )
        return self.applyMatrix4( matrix )

    @jit(cache=True)
    def unproject(self, camera):
        matrix = Matrix4()
        matrix.multiplyMatrices( camera.matrixWorld, matrix.getInverse( camera.projectionMatrix ) )
        return self.applyMatrix4( matrix )

    @jit(cache=True)
    def transformDirection(self, m ):
        # // input: THREE.Matrix4 affine matrix
        # // vector interpreted as a direction

        x = self.x; y = self.y; z = self.z
        e = m.elements

        self.x = e[ 0 ] * x + e[ 4 ] * y + e[ 8 ]  * z
        self.y = e[ 1 ] * x + e[ 5 ] * y + e[ 9 ]  * z
        self.z = e[ 2 ] * x + e[ 6 ] * y + e[ 10 ] * z

        return self.normalize()

    @jit(cache=True)
    def divide(self, v ):
        self.x /= v.x
        self.y /= v.y
        self.z /= v.z

        return self

    @jit(cache=True)
    def divideScalar(self, scalar ):
        return self.multiplyScalar( 1 / scalar )

    @jit(cache=True)
    def min(self, v ):
        self.x = min( self.x, v.x )
        self.y = min( self.y, v.y )
        self.z = min( self.z, v.z )
        return self

    @jit(cache=True)
    def max(self, v ):
        self.x = max( self.x, v.x )
        self.y = max( self.y, v.y )
        self.z = max( self.z, v.z )
        return self

    @jit(cache=True)
    def clamp(self, min, max ):
        # // assumes min < max, componentwise
        self.x = max( min.x, min( max.x, self.x ) )
        self.y = max( min.y, min( max.y, self.y ) )
        self.z = max( min.z, min( max.z, self.z ) )

        return self

    @jit(cache=True)
    def clampScalar(self, minVal, maxVal):
        min = Vector3()
        max = Vector3()

        min.set( minVal, minVal, minVal )
        max.set( maxVal, maxVal, maxVal )

        return self.clamp( min, max )

    @jit(cache=True)
    def clampLength(self, min, max ):
        length = self.length()
        return self.divideScalar( length or 1 ).multiplyScalar( max( min, min( max, length ) ) )

    @jit(cache=True)
    def floor(self):
        self.x = math.floor( self.x )
        self.y = math.floor( self.y )
        self.z = math.floor( self.z )
        return self

    @jit(cache=True)
    def ceil(self):
        self.x = math.ceil( self.x )
        self.y = math.ceil( self.y )
        self.z = math.ceil( self.z )

        return self

    @jit(cache=True)
    def round(self):
        self.x = round( self.x )
        self.y = round( self.y )
        self.z = round( self.z )
        return self

    @jit(cache=True)
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

        return self

    @jit(cache=True)
    def negate(self):
        self.x = - self.x
        self.y = - self.y
        self.z = - self.z

        return self

    @jit(cache=True)
    def dot(self, v ):
        return self.x * v.x + self.y * v.y + self.z * v.z

    # // TODO lengthSquared?
    @jit(cache=True)
    def lengthSq(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    @jit(cache=True)
    def length(self):
        return math.sqrt( self.x * self.x + self.y * self.y + self.z * self.z )

    @jit(cache=True)
    def lengthManhattan(self):
        return abs( self.x ) + abs( self.y ) + abs( self.z )

    @jit(cache=True)
    def normalize(self):
        return self.divideScalar( self.length() or 1 )

    @jit(cache=True)
    def setLength(self, length ):
        return self.normalize().multiplyScalar( length )

    @jit(cache=True)
    def lerp(self, v, alpha ):
        self.x += ( v.x - self.x ) * alpha
        self.y += ( v.y - self.y ) * alpha
        self.z += ( v.z - self.z ) * alpha

        return self

    @jit(cache=True)
    def lerpVectors(self, v1, v2, alpha ):
        return self.subVectors( v2, v1 ).multiplyScalar( alpha ).add( v1 )

    @jit(cache=True)
    def cross(self, v, w=None ):
            if w is not None:
                print( 'THREE.Vector3: .cross() now only accepts one argument. Use .crossVectors( a, b ) instead.' )
                return self.crossVectors( v, w )

            x = self.x; y = self.y; z = self.z

            self.x = y * v.z - z * v.y
            self.y = z * v.x - x * v.z
            self.z = x * v.y - y * v.x

            return self

    @jit(cache=True)
    def crossVectors(self, a, b ):
        ax = a.x; ay = a.y; az = a.z
        bx = b.x; by = b.y; bz = b.z

        self.x = ay * bz - az * by
        self.y = az * bx - ax * bz
        self.z = ax * by - ay * bx

        return self

    @jit(cache=True)
    def projectOnVector(self, vector ):
        scalar = vector.dot( self ) / vector.lengthSq()

        return self.copy( vector ).multiplyScalar( scalar )

    @jit(cache=True)
    def projectOnPlane(self, planeNormal):
        v1 = Vector3()
        v1.copy( self ).projectOnVector( planeNormal )
        return self.sub( v1 )

    @jit(cache=True)
    def reflect(self, normal):
        # // reflect incident vector off plane orthogonal to normal
        # // normal is assumed to have unit length
        v1 = Vector3()
        return self.sub( v1.copy( normal ).multiplyScalar( 2 * self.dot( normal ) ) )

    @jit(cache=True)
    def angleTo(self, v ):
        theta = self.dot( v ) / ( math.sqrt( self.lengthSq() * v.lengthSq() ) )

        # // clamp, to handle numerical problems

        return math.acos( _Math.clamp( theta, - 1, 1 ) )

    @jit(cache=True)
    def distanceTo(self, v ):
        return math.sqrt( self.distanceToSquared( v ) )

    @jit(cache=True)
    def distanceToSquared(self, v ):
        dx = self.x - v.x; dy = self.y - v.y; dz = self.z - v.z
        return dx * dx + dy * dy + dz * dz

    @jit(cache=True)
    def distanceToManhattan(self, v ):
        return abs( self.x - v.x ) + abs( self.y - v.y ) + abs( self.z - v.z )

    @jit(cache=True)
    def setFromSpherical(self, s ):
        sinPhiRadius = math.sin( s.phi ) * s.radius
        self.x = sinPhiRadius * math.sin( s.theta )
        self.y = math.cos( s.phi ) * s.radius
        self.z = sinPhiRadius * math.cos( s.theta )
        return self

    @jit(cache=True)
    def setFromCylindrical(self, c ):
        self.x = c.radius * math.sin( c.theta )
        self.y = c.y
        self.z = c.radius * math.cos( c.theta )

        return self

    @jit(cache=True)
    def setFromMatrixPosition(self, m ):
        e = m.elements

        self.x = e[ 12 ]
        self.y = e[ 13 ]
        self.z = e[ 14 ]

        return self

    @jit(cache=True)
    def setFromMatrixScale(self, m ):
        sx = self.setFromMatrixColumn( m, 0 ).length()
        sy = self.setFromMatrixColumn( m, 1 ).length()
        sz = self.setFromMatrixColumn( m, 2 ).length()

        self.x = sx
        self.y = sy
        self.z = sz

        return self

    @jit(cache=True)
    def setFromMatrixColumn(self, m, index ):
        return self.fromArray( m.elements, index * 4 )

    @jit(cache=True)
    def equals(self, v ):
        return ( v.x == self.x ) and ( v.y == self.y ) and ( v.z == self.z )

    @jit(cache=True)
    def fromArray(self, array, offset=0 ):
        self.x = array[ offset ]
        self.y = array[ offset + 1 ]
        self.z = array[ offset + 2 ]

        return self

    @jit(cache=True)
    def toArray(self, array=None, offset=0 ):
        if array is None:
            array= [0,0,0]

        array[ offset ] = self.x
        array[ offset + 1 ] = self.y
        array[ offset + 2 ] = self.z

        return array

    @jit(cache=True)
    def fromBufferAttribute(self, attribute, index, offset=None ):
        if offset is not None:
            print( 'THREE.Vector3: offset has been removed from .fromBufferAttribute().' )

        self.x = attribute.getX( index )
        self.y = attribute.getY( index )
        self.z = attribute.getZ( index )

        return self
