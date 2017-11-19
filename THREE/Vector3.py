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
import numpy as np

from THREE.Quaternion import *
from THREE.Matrix4 import *
import THREE._Math as _Math
from THREE.pyOpenGLObject import *


class Vector3(pyOpenGLObject):
    isVector3 = True

    def __init__(self, x=0, y=0, z=0):
        super().__init__()
        self.set_class(isVector3)
        self.np = np.array([x, y, z], np.float64)
        """
        self.x = x
        self.y = y
        self.z = z
        """
        self.array = np.array([0, 0, 0, 1], np.float64)

    def set(self, x, y, z ):
        self.np[0] = x
        self.np[1] = y
        self.np[2] = z

        return self

    def setScalar(self, scalar ):
        self.x = scalar
        self.y = scalar
        self.z = scalar
        return self

    def setX(self, x ):
        self.np[0] = x
        return self

    def setY(self, y ):
        self.np[1] = y
        return self

    def setZ(self, z ):
        self.np[2] = z
        return self

    def getX(self):
        return self.np[0]

    def getY(self):
        return self.np[1]

    def getZ(self):
        return self.np[2]

    x = property(getX, setX)
    y = property(getY, setY)
    z = property(getZ, setZ)

    def setComponent(self, index, value ):
        if index == 0:
            self.np[0] = value
        elif index == 1:
            self.np[1] = value
        elif index == 2:
            self.np[2] = value
        elif index == 'x':
            self.np[0] = value
        elif index == 'y':
            self.np[1] = value
        elif index == 'z':
            self.np[2] = value
        else:
            print( 'index is out of range: ' + index )

        return self

    def getComponent(self, index ):
        if index == 0:
            return self.np[0]
        elif index == 1:
            return self.np[1]
        elif index == 2:
            return self.np[2]
        else:
            print( 'index is out of range: ' + index )

    def clone(self):
        return type(self)( self.np[0], self.np[1], self.np[2] )

    def copy(self, v ):
        np.copyto(self.np, v.np)
        return self

    def add(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .add() now only accepts one argument. Use .addVectors( a, b ) instead.' )
            return self.addVectors( v, w )

        self.np += v.np

        return self

    def addScalar(self, s ):
        self.np += s
        return self

    def addVectors(self, a, b ):
        self.np = a.np + b.np
        return self

    def addScaledVector(self, v, s ):
        self.np += v.np * s
        return self

    def sub(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.' )
            return self.subVectors( v, w )

        self.np -= v.np
        return self

    def subScalar(self, s ):
        self.np -= s
        return self

    def subVectors(self, a, b ):
        self.np = a.np - b.np
        return self

    def multiply(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector3: .multiply() now only accepts one argument. Use .multiplyVectors( a, b ) instead.' )
            return self.multiplyVectors( v, w )

        self.np *= v.np
        return self

    def multiplyScalar(self, scalar ):
        self.np *= scalar
        return self

    def multiplyVectors(self, a, b ):
        self.np = a.np * b.np
        return self

    def applyEuler(self, euler):
        quaternion = Quaternion()
        if not( euler and euler.isEuler):
            print( 'THREE.Vector3: .applyEuler() now expects an Euler rotation rather than a Vector3 and order.' )

        return self.applyQuaternion( quaternion.setFromEuler( euler ) )

    def applyAxisAngle(self, axis, angle):
        quaternion = Quaternion()
        return self.applyQuaternion( quaternion.setFromAxisAngle( axis, angle ) )

    def applyMatrix3(self, m ):
        self.np.dot(m.matrix)

        return self

    def applyMatrix4(self, m ):
        np.put(self.array, (0,1,2), self.np)
        c = np.dot(self.array, m.matrix)

        if c[3] == 0:
            self.z = float("-inf")
            return self

        c /= c[3]

        np.put(self.np, (0,1,2), c)

        return self

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

    def project(self, camera):
        matrix = Matrix4()
        matrix.multiplyMatrices( camera.projectionMatrix, matrix.getInverse( camera.matrixWorld ) )
        return self.applyMatrix4( matrix )

    def unproject(self, camera):
        matrix = Matrix4()
        matrix.multiplyMatrices( camera.matrixWorld, matrix.getInverse( camera.projectionMatrix ) )
        return self.applyMatrix4( matrix )

    def transformDirection(self, m ):
        # // input: THREE.Matrix4 affine matrix
        # // vector interpreted as a direction

        x = self.np[0]; y = self.np[1]; z = self.np[2]
        e = m.elements

        self.np[0] = e[ 0 ] * x + e[ 4 ] * y + e[ 8 ]  * z
        self.np[1] = e[ 1 ] * x + e[ 5 ] * y + e[ 9 ]  * z
        self.np[2] = e[ 2 ] * x + e[ 6 ] * y + e[ 10 ] * z

        return self.normalize()

    def divide(self, v ):
        self.x /= v.x
        self.y /= v.y
        self.z /= v.z

        return self

    def divideScalar(self, scalar ):
        return self.multiplyScalar( 1 / scalar )

    def min(self, v ):
        self.np = np.fmin(self.np, v.np)
        return self

    def max(self, v ):
        self.np = np.fmax(self.np, v.np)
        return self

    def clamp(self, min, max ):
        # // assumes min < max, componentwise
        self.x = max( min.x, min( max.x, self.x ) )
        self.y = max( min.y, min( max.y, self.y ) )
        self.z = max( min.z, min( max.z, self.z ) )

        return self

    def clampScalar(self, minVal, maxVal):
        min = Vector3()
        max = Vector3()

        min.set( minVal, minVal, minVal )
        max.set( maxVal, maxVal, maxVal )

        return self.clamp( min, max )

    def clampLength(self, min, max ):
        length = self.length()
        return self.divideScalar( length or 1 ).multiplyScalar( max( min, min( max, length ) ) )

    def floor(self):
        self.x = math.floor( self.x )
        self.y = math.floor( self.y )
        self.z = math.floor( self.z )
        return self

    def ceil(self):
        self.x = math.ceil( self.x )
        self.y = math.ceil( self.y )
        self.z = math.ceil( self.z )

        return self

    def round(self):
        self.x = round( self.x )
        self.y = round( self.y )
        self.z = round( self.z )
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

        return self

    def negate(self):
        self.x = - self.x
        self.y = - self.y
        self.z = - self.z

        return self

    def dot(self, v ):
        return self.np.dot(v.np)

    # // TODO lengthSquared?
    def lengthSq(self):
        s1 = np.dot(self.np, self.np)
        return s1

    def length(self):
        return np.sqrt( self.lengthSq() )

    def lengthManhattan(self):
        return abs( self.x ) + abs( self.y ) + abs( self.z )

    def normalize(self):
        return self.divideScalar( self.length() or 1 )

    def setLength(self, length ):
        return self.normalize().multiplyScalar( length )

    def lerp(self, v, alpha ):
        self.x += ( v.x - self.x ) * alpha
        self.y += ( v.y - self.y ) * alpha
        self.z += ( v.z - self.z ) * alpha

        return self

    def lerpVectors(self, v1, v2, alpha ):
        return self.subVectors( v2, v1 ).multiplyScalar( alpha ).add( v1 )

    def cross(self, v, w=None ):
            if w is not None:
                print( 'THREE.Vector3: .cross() now only accepts one argument. Use .crossVectors( a, b ) instead.' )
                return self.crossVectors( v, w )

            self.np = np.cross(self.np, v.np)

            return self

    def crossVectors(self, a, b ):
        self.np = np.cross(a.np, b.np)

        return self

    def projectOnVector(self, vector ):
        scalar = vector.dot( self ) / vector.lengthSq()

        return self.copy( vector ).multiplyScalar( scalar )

    def projectOnPlane(self, planeNormal):
        v1 = Vector3()
        v1.copy( self ).projectOnVector( planeNormal )
        return self.sub( v1 )

    def reflect(self, normal):
        # // reflect incident vector off plane orthogonal to normal
        # // normal is assumed to have unit length
        v1 = Vector3()
        return self.sub( v1.copy( normal ).multiplyScalar( 2 * self.dot( normal ) ) )

    def angleTo(self, v ):
        theta = self.dot( v ) / ( math.sqrt( self.lengthSq() * v.lengthSq() ) )

        # // clamp, to handle numerical problems

        return math.acos( _Math.clamp( theta, - 1, 1 ) )

    def distanceTo(self, v ):
        return math.sqrt( self.distanceToSquared( v ) )

    def distanceToSquared(self, v ):
        dm = np.subtract(self.np, v.np)
        d = np.dot(dm, dm)
        return d

    def distanceToManhattan(self, v ):
        return abs( self.x - v.x ) + abs( self.y - v.y ) + abs( self.z - v.z )

    def setFromSpherical(self, s ):
        sinPhiRadius = math.sin( s.phi ) * s.radius
        self.x = sinPhiRadius * math.sin( s.theta )
        self.y = math.cos( s.phi ) * s.radius
        self.z = sinPhiRadius * math.cos( s.theta )
        return self

    def setFromCylindrical(self, c ):
        self.x = c.radius * math.sin( c.theta )
        self.y = c.y
        self.z = c.radius * math.cos( c.theta )

        return self

    def setFromMatrixPosition(self, m):
        self.np[0] = m.elements[12]
        self.np[1] = m.elements[13]
        self.np[2] = m.elements[14]
        return self

    def setFromMatrixScale(self, m ):
        sx = self.setFromMatrixColumn( m, 0 ).length()
        sy = self.setFromMatrixColumn( m, 1 ).length()
        sz = self.setFromMatrixColumn( m, 2 ).length()

        self.x = sx
        self.y = sy
        self.z = sz

        return self

    def setFromMatrixColumn(self, m, index ):
        return self.fromArray( m.elements, index * 4 )

    def equals(self, v ):
        return ( v.x == self.x ) and ( v.y == self.y ) and ( v.z == self.z )

    def fromArray(self, array, offset=0 ):
        self.x = array[ offset ]
        self.y = array[ offset + 1 ]
        self.z = array[ offset + 2 ]

        return self

    def toArray(self, array=None, offset=0 ):
        if array is None:
            array= [0,0,0]

        array[ offset ] = self.x
        array[ offset + 1 ] = self.y
        array[ offset + 2 ] = self.z

        return array

    def fromBufferAttribute(self, attribute, index, offset=None ):
        if offset is not None:
            print( 'THREE.Vector3: offset has been removed from .fromBufferAttribute().' )

        self.x = attribute.getX( index )
        self.y = attribute.getY( index )
        self.z = attribute.getZ( index )

        return self
