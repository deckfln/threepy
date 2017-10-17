import math
from THREE.pyOpenGLObject import *


class Vector2(pyOpenGLObject):
    isVector2 = True

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set(self, x, y ):
        self.x = x
        self.y = y
        return self

    def setScalar(self, scalar ):
        self.x = scalar
        self.y = scalar
        return self

    def setX(self, x ):
        self.x = x
        return self

    def setY(self, y ):
        self.y = y
        return self

    def setComponent(self, index, value ):
        if index==0:
            self.x = value
        elif index==1:
            self.y = value
        else:
            print( 'index is out of range: ' + index )
        return self

    def getComponent(self, index ):
        if index==0:
            return self.x
        elif index==1:
            return self.y
        print( 'index is out of range: ' + index )

    def clone(self):
        return type(self)( self.x, self.y )

    def copy(self, v ):
        self.x = v.x
        self.y = v.y
        return self

    def add(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector2: .add() now only accepts one argument. Use .addVectors( a, b ) instead.' )
            return self.addVectors( v, w )

        self.x += v.x
        self.y += v.y

        return self

    def addScalar(self, s ):
        self.x += s
        self.y += s
        return self

    def addVectors(self, a, b ):
        self.x = a.x + b.x
        self.y = a.y + b.y
        return self

    def addScaledVector(self, v, s ):
        self.x += v.x * s
        self.y += v.y * s
        return self

    def sub(self, v, w=None ):
        if w is not None:
            print( 'THREE.Vector2: .sub() now only accepts one argument. Use .subVectors( a, b ) instead.' )
            return self.subVectors( v, w )

        self.x -= v.x
        self.y -= v.y
        return self

    def subScalar(self, s ):
        self.x -= s
        self.y -= s
        return self

    def subVectors(self, a, b ):
        self.x = a.x - b.x
        self.y = a.y - b.y
        return self

    def multiply(self, v ):
        self.x *= v.x
        self.y *= v.y
        return self

    def multiplyScalar(self, scalar ):
        self.x *= scalar
        self.y *= scalar
        return self

    def divide(self, v ):
        self.x /= v.x
        self.y /= v.y
        return self

    def divideScalar(self, scalar ):
        return self.multiplyScalar( 1 / scalar )

    def min(self, v ):
        self.x = min( self.x, v.x )
        self.y = min( self.y, v.y )
        return self

    def max(self, v ):
        self.x = max( self.x, v.x )
        self.y = max( self.y, v.y )
        return self

    def clamp(self, min, max ):
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
        self.x = math.floor( self.x )
        self.y = math.floor( self.y )
        return self

    def ceil(self):
        self.x = math.ceil( self.x )
        self.y = math.ceil( self.y )
        return self

    def round(self):
        self.x = round( self.x )
        self.y = round( self.y )
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
        self.x = - self.x
        self.y = - self.y
        return self

    def dot(self, v ):
        return self.x * v.x + self.y * v.y

    def lengthSq(self):
        return self.x * self.x + self.y * self.y

    def length(self):
        return math.sqrt( self.x * self.x + self.y * self.y )

    def lengthManhattan(self):
        return abs( self.x ) + abs( self.y )

    def normalize(self):
        return self.divideScalar( self.length() or 1 )

    def angle(self):
        # // computes the angle in radians with respect to the positive x-axis
        angle = math.atan2( self.y, self.x )
        if angle < 0:
            angle += 2 * math.pi

        return angle

    def distanceTo(self, v ):
        return math.sqrt( self.distanceToSquared( v ) )

    def distanceToSquared(self, v ):
        dx = self.x - v.x; dy = self.y - v.y
        return dx * dx + dy * dy

    def distanceToManhattan(self, v ):
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
        c = math.cos( angle ); s = math.sin( angle )

        x = self.x - center.x
        y = self.y - center.y

        self.x = x * c - y * s + center.x
        self.y = x * s + y * c + center.y

        return self