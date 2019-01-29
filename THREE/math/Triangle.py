"""
    /**
     * @author bhouston / http://clara.io
     * @author mrdoob / http://mrdoob.com/
     */
"""
from THREE.math.Plane import *

_v0 = Vector3()


class Triangle:
    def __init__(self, a=None, b=None, c=None ):
        if a is None:
            a = Vector3()
        if b is None:
            b = Vector3()
        if c is None:
            c = Vector3()
        self.a = a
        self.b = b
        self.c = c

    def _getNormal(self, a, b, c, target):
        target.subVectors(c, b)

        target.subVectors( c, b )
        _v0.subVectors( a, b )
        target.cross( _v0 )

        targetLengthSq = target.lengthSq()
        if targetLengthSq > 0:
            return target.multiplyScalar( 1 / math.sqrt( targetLengthSq) )

        return target.set( 0, 0, 0 )

    # // static/instance method to calculate barycentric coordinates
    # // based on: http://www.blackpawn.com/texts/pointinpoly/default.html
    def _getBarycoord(self, point, a, b, c, target):
        v0 = Vector3()
        v1 = Vector3()
        v2 = Vector3()

        v0.subVectors( c, a )
        v1.subVectors( b, a )
        v2.subVectors( point, a )

        dot00 = v0.dot( v0 )
        dot01 = v0.dot( v1 )
        dot02 = v0.dot( v2 )
        dot11 = v1.dot( v1 )
        dot12 = v1.dot( v2 )

        denom = ( dot00 * dot11 - dot01 * dot01 )

        # // collinear or singular triangle
        if denom == 0:
            # // arbitrary location outside of triangle?
            # // not sure if self is the best idea, maybe should be returning undefined
            return target.set( - 2, - 1, - 1 )

        invDenom = 1 / denom
        u = ( dot11 * dot02 - dot01 * dot12 ) * invDenom
        v = ( dot00 * dot12 - dot01 * dot02 ) * invDenom

        # // barycentric coordinates must always sum to 1
        return target.set( 1 - u - v, v, u )

    def _containsPoint(self, point, a, b, c):
        v1 = Vector3()
        self._getBarycoord( point, a, b, c, v1 )

        return ( v1.x >= 0 ) and ( v1.y >= 0 ) and ( ( v1.x + v1.y ) <= 1 )

    def set(self, a, b, c ):
        self.a.copy( a )
        self.b.copy( b )
        self.c.copy( c )

        return self

    def setFromPointsAndIndices(self, points, i0, i1, i2 ):
        self.a.copy( points[ i0 ] )
        self.b.copy( points[ i1 ] )
        self.c.copy( points[ i2 ] )

        return self

    def clone(self):
        return type(self)().copy( self )

    def copy(self, triangle ):
        self.a.copy( triangle.a )
        self.b.copy( triangle.b )
        self.c.copy( triangle.c )

        return self

    def getArea(self):
        v0 = Vector3()
        v1 = Vector3()

        v0.subVectors( self.c, self.b )
        v1.subVectors( self.a, self.b )

        return v0.cross( v1 ).length() * 0.5

    def getMidpoint(self, target):
        return target.addVectors( self.a, self.b ).add( self.c ).multiplyScalar( 1 / 3 )

    def getNormal(self, target):
        return self._getNormal(self.a, self.b, self.c, target)

    def getPlane(self, target):
        return target.setFromCoplanarPoints( self.a, self.b, self.c )

    def getBarycoord(self, point, target):
        return self._getBarycoord(point, self.a, self.b, self.c, target)

    def containsPoint(self, point ):
        return self._containsPoint( point, self.a, self.b, self.c)

    def intersectsBox(self, box):
        return box.intersectsTriangle(self)

    def closestPointToPoint(self, target):
        vab = Vector3()
        vac = Vector3()
        vbc = Vector3()
        vap = Vector3()
        vbp = Vector3()
        vcp = Vector3()

        a = self.a
        b = self.b
        c = self.c

        """
        // algorithm thanks to Real-Time Collision Detection by Christer Ericson,
        // published by Morgan Kaufmann Publishers, (c) 2005 Elsevier Inc.,
        // under the accompanying license; see chapter 5.1.5 for detailed explanation.
        // basically, we're distinguishing which of the voronoi regions of the triangle
        // the point lies in with the minimum amount of redundant computation.
        """
        vab.subVectors( b, a )
        vac.subVectors( c, a )
        vap.subVectors( p, a )
        d1 = vab.dot( vap )
        d2 = vac.dot( vap )
        if d1 <= 0 and d2 <= 0:
            # vertex region of A; barycentric coords (1, 0, 0)
            return target.copy( a )

        vbp.subVectors( p, b )
        d3 = vab.dot( vbp )
        d4 = vac.dot( vbp )
        if d3 >= 0 and d4 <= d3:
            # vertex region of B; barycentric coords (0, 1, 0)
            return target.copy( b )

        vc = d1 * d4 - d3 * d2
        if vc <= 0 and d1 >= 0 and d3 <= 0:
            v = d1 / ( d1 - d3 )
            # edge region of AB; barycentric coords (1-v, v, 0)
            return target.copy( a ).addScaledVector( vab, v )

        vcp.subVectors( p, c )
        d5 = vab.dot( vcp )
        d6 = vac.dot( vcp )
        if d6 >= 0 and d5 <= d6:
            # vertex region of C; barycentric coords (0, 0, 1)
            return target.copy( c )

        vb = d5 * d2 - d1 * d6
        if vb <= 0 and d2 >= 0 and d6 <= 0:
            w = d2 / ( d2 - d6 )
            # edge region of AC; barycentric coords (1-w, 0, w)
            return target.copy( a ).addScaledVector( vac, w )

        va = d3 * d6 - d5 * d4
        if va <= 0 and ( d4 - d3 ) >= 0 and ( d5 - d6 ) >= 0:
            vbc.subVectors( c, b )
            w = ( d4 - d3 ) / ( ( d4 - d3 ) + ( d5 - d6 ) )
            # edge region of BC; barycentric coords (0, 1-w, w)
            return target.copy( b ).addScaledVector( vbc, w )   # edge region of BC

        # face region
        denom = 1 / ( va + vb + vc )
        # u = va * denom
        v = vb * denom
        w = vc * denom
        return target.copy( a ).addScaledVector( vab, v ).addScaledVector( vac, w )

    def equals(self, triangle ):
        return triangle.a.equals( self.a ) and triangle.b.equals( self.b ) and triangle.c.equals( self.c )
