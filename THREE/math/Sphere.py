"""
/**
 * @author bhouston / http://clara.io
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.math.Box3 import *

_cython = True


class Sphere:
    def __init__(self, center=None, radius=0 ):
        if center is None:
            self.center = Vector3()
        else:
            self.center = center

        self.radius = radius    

    def set(self, center, radius ):
        self.center.copy( center )    
        self.radius = radius    

        return self    

    def setFromPoints(self, points, optionalCenter=None):
        box = Box3()    
        center = self.center    
        if optionalCenter is not None:
            center.copy( optionalCenter )    
        else:
            box.setFromPoints( points ).getCenter( center )    

        maxRadiusSq = 0    

        for point in points:
            maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( point ) )

        self.radius = math.sqrt( maxRadiusSq )    

        return self    

    def clone(self):
        return type(self)().copy( self )

    def copy(self, sphere ):
        self.center.copy( sphere.center )    
        self.radius = sphere.radius    

        return self    

    def empty(self):
        return ( self.radius <= 0 )    

    def containsPoint(self, point ):
        return ( point.distanceToSquared( self.center ) <= ( self.radius * self.radius ) )    

    def distanceToPoint(self, point ):
        return ( point.distanceTo( self.center ) - self.radius )    

    def intersectsSphere(self, sphere ):
        radiusSum = self.radius + sphere.radius    

        return sphere.center.distanceToSquared( self.center ) <= ( radiusSum * radiusSum )    

    def intersectsBox(self, box ):
        return box.intersectsSphere( self )    

    def intersectsPlane(self, plane ):
        return abs( plane.distanceToPoint( self.center ) ) <= self.radius

    def clampPoint(self, point, target):
        deltaLengthSq = self.center.distanceToSquared( point )    

        target.copy( point )

        if deltaLengthSq > ( self.radius * self.radius ):
            target.sub( self.center ).normalize()
            target.multiplyScalar( self.radius ).add( self.center )

        return target

    def getBoundingBox(self, target):
        target.set( self.center, self.center )
        target.expandByScalar( self.radius )

        return target

    def applyMatrix4(self, matrix):
        global _cython
        if _cython:
            cSphere_applyMatrix4(self, matrix)
        else:
            self._applyMatrix4(matrix)

        return self

    def _applyMatrix4(self, matrix ):
        self.center.applyMatrix4( matrix )    
        self.radius = self.radius * matrix.getMaxScaleOnAxis()    

    def translate(self, offset ):
        self.center.add( offset )    

        return self    

    def equals(self, sphere ):
        return sphere.center.equals( self.center ) and ( sphere.radius == self.radius )    
