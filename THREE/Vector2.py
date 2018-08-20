"""
 * @author mrdoob / http://mrdoob.com/
 * @author philogb / http://blog.thejit.org/
 * @author egraether / http://egraether.com/
 * @author zz85 / http://www.lab4games.net/zz85/blog
"""

import math
from THREE.pyOpenGLObject import *
import numpy as np


class Vector2(pyOpenGLObject):
    isVector2 = True

    def __init__(self, x=0, y=0):
        super().__init__()
        self.set_class(isVector2)

        self.np = np.zeros(2, np.float32)
        self.np[0] = x
        self.np[1] = y

    def set(self, x, y ):
        self.np[0] = x
        self.np[1] = y
        return self

    def setScalar(self, scalar ):
        self.np[0] = scalar
        self.np[1] = scalar
        return self

    def setX(self, x):
        self.np[0] = x
        return self

    def setY(self, y):
        self.np[1] = y
        return self

    def getX(self):
        return self.np[0]

    def getY(self):
        return self.np[1]

    x = property(getX, setX)
    y = property(getY, setY)

    def setComponent(self, index, value ):
        if index==0:
            self.np[0] = value
        elif index==1:
            self.np[1] = value
        else:
            print( 'index is out of range: ' + index )
        return self

    def getComponent(self, index ):
        if index==0:
            return self.np[0]
        elif index==1:
            return self.np[1]
        print( 'index is out of range: ' + index )

    def clone(self):
        return type(self)(self.np[0], self.np[1])

    def copy(self, v):
        self.np[0] = v.np[0]
        self.np[1] = v.np[1]
        return self

    def add(self, v):
        # if w is not None:
        #    print( 'THREE.Vector2: .add() now only accepts one argument. Use .addVectors( a, b ) instead.' )
        #    return self.addVectors( v, w )

        self.np += v.np
        # self.x += v.x
        # self.y += v.y

        return self

    def addScalar(self, s):
        self.np += s
        # self.x += s
        # self.y += s
        return self

    def addVectors(self, a, b):
        self.np = a.np + b.np
        # self.x = a.x + b.x
        # self.y = a.y + b.y
        return self

    def addScaledVector(self, v, s):
        self.np += v.np * s
        # self.x += v.x * s
        # self.y += v.y * s
        return self

    def sub(self, v):
        # if w is not None:
        #    print( 'THREE.Vector2: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.' )
        #    return self.subVectors( v, w )

        self.np -= v.np
        # self.x -= v.x
        # self.y -= v.y
        return self

    def subScalar(self, s):
        self.np -= s
        # self.x -= s
        # self.y -= s
        return self

    def subVectors(self, a, b ):
        self.np = a.np - b.np
        # self.x = a.x - b.x
        # self.y = a.y - b.y
        return self

    def multiply(self, v):
        self.np *= v.np
        # self.x *= v.x
        # self.y *= v.y
        return self

    def multiplyScalar(self, scalar):
        self.np *= scalar
        # self.x *= scalar
        # self.y *= scalar
        return self

    def divide(self, v):
        self.np /= v.np
        # self.x /= v.x
        # self.y /= v.y
        return self

    def divideScalar(self, scalar ):
        return self.multiplyScalar( 1 / scalar )

    def applyMatrix3(self, m):
        x = self.np[0]
        y = self.np[1]
        e = m.np

        self.np[0] = e[0] * x + e[3] * y + e[6]
        self.np[1] = e[1] * x + e[4] * y + e[7]

        return self

    def min(self, v):
        np.minimum(self.np, v.np, self.np)
        # self.x = min( self.x, v.x )
        # self.y = min( self.y, v.y )
        return self

    def max(self, v):
        np.maximum(self.np, v.np, self.np)
        # self.x = max( self.x, v.x )
        # self.y = max( self.y, v.y )
        return self

    def clamp(self, min, max):
        # // assumes min < max, componentwise
        self.x = max( min.x, min( max.x, self.x ) )
        self.y = max( min.y, min( max.y, self.y ) )
        return self

    def clampScalar(self, minVal, maxVal):
        min = Vector2()
        max = Vector2()

        min.set( minVal, minVal )
        max.set( maxVal, maxVal )

        return self.clamp( min, max )

    def clampLength(self, min, max ):
        length = self.length()
        return self.divideScalar( length or 1 ).multiplyScalar( max( min, min( max, length ) ) )

    def floor(self):
        np.floor(self.np, self.np)
        # self.x = math.floor( self.x )
        # self.y = math.floor( self.y )
        return self

    def ceil(self):
        np.ceil(self.np, self.np)
        # self.x = math.ceil( self.x )
        # self.y = math.ceil( self.y )
        return self

    def round(self):
        np.round(self.np, self.np)
        # self.x = round( self.x )
        # self.y = round( self.y )
        return self

    def roundToZero(self):
        self.x = math.floor( self.x )
        if self.x < 0:
            self.x =math.ceil( self.x )
        self.y = math.floor( self.y )
        if self.y < 0:
            self.y= math.ceil( self.y )

        return self

    def negate(self):
        self.np = -self.np
        # self.x = - self.x
        # self.y = - self.y
        return self

    def dot(self, v ):
        return np.dot(self.np, v.np)
        # return self.x * v.x + self.y * v.y

    def cross(self, v):
        return self.np[0] * v.np[1] - self.np[1] * v.np[0]

    def lengthSq(self):
        return self.np[0] * self.np[0] + self.np[1] * self.np[1]

    def length(self):
        return math.sqrt( self.np[0] * self.np[0] + self.np[1] * self.np[1] )

    def manhattanLength(self):
        return abs( self.np[0] ) + abs( self.np[1] )

    def normalize(self):
        return self.divideScalar( self.length() or 1 )

    def angle(self):
        # // computes the angle in radians with respect to the positive x-axis
        angle = math.atan2( self.np[1], self.np[0] )
        if angle < 0:
            angle += 2 * math.pi

        return angle

    def distanceTo(self, v ):
        return math.sqrt( self.distanceToSquared( v ) )

    def distanceToSquared(self, v ):
        dx = self.np[0] - v.np[0]
        dy = self.np[1] - v.np[1]
        return dx * dx + dy * dy

    def manhattanDistanceTo(self, v ):
        return abs( self.x - v.x ) + abs( self.y - v.y )

    def setLength(self, length ):
        return self.normalize().multiplyScalar( length )

    def lerp(self, v, alpha ):
        self.x += ( v.x - self.x ) * alpha
        self.y += ( v.y - self.y ) * alpha
        return self

    def lerpVectors(self, v1, v2, alpha ):
        return self.subVectors( v2, v1 ).multiplyScalar( alpha ).add( v1 )

    def equals(self, v ):
        return  ( v.x == self.x ) and ( v.y == self.y )

    def fromArray(self, array, offset=0 ):
        self.x = array[ offset ]
        self.y = array[ offset + 1 ]
        return self

    def toArray(self, array=None, offset=0):
        if array is None:
            array = [self.x, self.y]
        else:
            array[offset] = self.x
            array[offset + 1] = self.y
        return array

    def fromBufferAttribute(self, attribute, index, offset=None ):
        if offset is not None:
            print( 'THREE.Vector2: offset has been removed from .fromBufferAttribute().' )

        self.x = attribute.getX( index )
        self.y = attribute.getY( index )

        return self

    def rotateAround(self, center, angle ):
        c = math.cos( angle )
        s = math.sin( angle )

        x = self.x - center.x
        y = self.y - center.y

        self.x = x * c - y * s + center.x
        self.y = x * s + y * c + center.y

        return self

    def rotate(self, angle ):
        c = math.cos( angle )
        s = math.sin( angle )

        x = self.x
        y = self.y

        self.x = x * c - y * s
        self.y = x * s + y * c

        return self