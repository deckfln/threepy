"""
/**
 * @author bhouston / http://clara.io
 */
"""
from THREE.math.Vector3 import *
import THREE._Math as _Math


class Line3:
    def __init__(self, start=None, end=None ):
        self.start = start if start  else Vector3()
        self.end = end if end else Vector3()


    def set(self, start, end ):
        self.start.copy( start )
        self.end.copy( end )

        return self

    def clone(self):
        return type(self)().copy( self )

    def copy(self, line ):
        self.start.copy( line.start )
        self.end.copy( line.end )

        return self

    def getCenter(self, target):
        return target.addVectors( self.start, self.end ).multiplyScalar( 0.5 )

    def delta(self, target):
        return target.subVectors( self.end, self.start )

    def distanceSq(self):
        return self.start.distanceToSquared( self.end )

    def distance(self):
        return self.start.distanceTo( self.end )

    def at(self, t, target):
        return self.delta( target).multiplyScalar( t ).add( self.start )

    def closestPointToPointParameter(self, point, clampToLine):
        startP = Vector3()
        startEnd = Vector3()

        startP.subVectors( point, self.start )
        startEnd.subVectors( self.end, self.start )

        startEnd2 = startEnd.dot( startEnd )
        startEnd_startP = startEnd.dot( startP )

        t = startEnd_startP / startEnd2

        if clampToLine:
            t = _Math.clamp( t, 0, 1 )

        return t

    def closestPointToPoint(self, point, clampToLine, target):
        t = self.closestPointToPointParameter( point, clampToLine )

        return self.delta( target).multiplyScalar( t ).add( self.start )

    def applyMatrix4(self, matrix ):
        self.start.applyMatrix4( matrix )
        self.end.applyMatrix4( matrix )

        return self

    def equals(self, line ):
        return line.start.equals( self.start ) and line.end.equals( self.end )
