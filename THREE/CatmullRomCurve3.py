"""
/**
 * @author zz85 https://github.com/zz85
 *
 * Centripetal CatmullRom Curve - which is useful for avoiding
 * cusps and self-intersections in non-uniform catmull rom curves.
 * http://www.cemyuksel.com/research/catmullrom_param/catmullrom.pdf
 *
 * curve.type accepts centripetal(default), chordal and catmullrom
 * curve.tension is used for catmullrom which defaults to 0.5
 */
"""

"""
/*
Based on an optimized c++ solution in
 - http://stackoverflow.com/questions/9489736/catmull-rom-curve-with-no-cusps-and-no-self-intersections/
 - http://ideone.com/NoEbVM

This CubicPoly class could be used for reusing some variables and calculations,
but for three.js curve use, it could be possible inlined and flatten into a single function call
which can be placed in CurveUtils.
*/
"""
from THREE.Curve import *
from THREE.Bezier import *
from THREE.CurvePath import *


class CubicPoly():
    def __init__(self, x0=0, x1=0, t0=0, t1=0):
        self.c0 = x0
        self.c1 = t0
        self.c2 = - 3 * x0 + 3 * x1 - 2 * t0 - t1
        self.c3 = 2 * x0 - 2 * x1 + t0 + t1

    def initCatmullRom(self, x0, x1, x2, x3, tension ):
        self.__init__( x1, x2, tension * ( x2 - x0 ), tension * ( x3 - x1 ) )

    def initNonuniformCatmullRom(self, x0, x1, x2, x3, dt0, dt1, dt2 ):
        # // compute tangents when parameterized in [t1,t2]
        t1 = ( x1 - x0 ) / dt0 - ( x2 - x0 ) / ( dt0 + dt1 ) + ( x2 - x1 ) / dt1
        t2 = ( x2 - x1 ) / dt1 - ( x3 - x1 ) / ( dt1 + dt2 ) + ( x3 - x2 ) / dt2

        # // rescale tangents for parametrization in [0,1]
        t1 *= dt1
        t2 *= dt1

        self.__init__( x1, x2, t1, t2 )

    def calc(self, t ):
            t2 = t * t
            t3 = t2 * t
            return self.c0 + self.c1 * t + self.c2 * t2 + self.c3 * t3


tmp = Vector3()
px = CubicPoly()
py = CubicPoly()
pz = CubicPoly()


class CatmullRomCurve3(Curve):
    def __init__(self, points=None ):
        super().__init__( )

        if len(points) < 2:
            raise RuntimeError( 'THREE.CatmullRomCurve3: Points array needs at least two entries.' )

        self.points = points or []
        self.closed = False
        self.tension = None

    def getPoint(self, t ):
        points = self.points
        l = len(points)

        point = ( l - ( 0 if self.closed else 1 ) ) * t
        intPoint = math.floor( point )
        weight = point - intPoint

        if self.closed:
            intPoint += 0 if intPoint > 0 else ( math.floor( abs( intPoint ) / len(points) ) + 1 ) * len(points)

        elif weight == 0 and intPoint == l - 1:
            intPoint = l - 2
            weight = 1

        # p0, p1, p2, p3; // 4 points

        if self.closed or intPoint > 0:
            p0 = points[ ( intPoint - 1 ) % l ]

        else:
            # // extrapolate first point
            tmp.subVectors( points[ 0 ], points[ 1 ] ).add( points[ 0 ] )
            p0 = tmp

        p1 = points[ intPoint % l ]
        p2 = points[ ( intPoint + 1 ) % l ]

        if self.closed or intPoint + 2 < l:
            p3 = points[ ( intPoint + 2 ) % l ]

        else:
            # // extrapolate last point
            tmp.subVectors( points[ l - 1 ], points[ l - 2 ] ).add( points[ l - 1 ] )
            p3 = tmp

        if self.type is None or self.type == 'centripetal' or self.type == 'chordal':
            # // init Centripetal / Chordal Catmull-Rom
            pow = 0.5 if self.type == 'chordal' else 0.25
            dt0 = math.pow( p0.distanceToSquared( p1 ), pow )
            dt1 = math.pow( p1.distanceToSquared( p2 ), pow )
            dt2 = math.pow( p2.distanceToSquared( p3 ), pow )

            # // safety check for repeated points
            if dt1 < 1e-4:
                dt1 = 1.0
            if dt0 < 1e-4:
                dt0 = dt1
            if dt2 < 1e-4:
                dt2 = dt1

            px.initNonuniformCatmullRom( p0.x, p1.x, p2.x, p3.x, dt0, dt1, dt2 )
            py.initNonuniformCatmullRom( p0.y, p1.y, p2.y, p3.y, dt0, dt1, dt2 )
            pz.initNonuniformCatmullRom( p0.z, p1.z, p2.z, p3.z, dt0, dt1, dt2 )

        elif self.type == 'catmullrom':

            tension = self.tension if self.tension is not None else 0.5
            px.initCatmullRom( p0.x, p1.x, p2.x, p3.x, tension )
            py.initCatmullRom( p0.y, p1.y, p2.y, p3.y, tension )
            pz.initCatmullRom( p0.z, p1.z, p2.z, p3.z, tension )

        return Vector3( px.calc( weight ), py.calc( weight ), pz.calc( weight ) )

        
class CubicBezierCurve3(Curve):
    def __init__(self, v0, v1, v2, v3 ):
        super().__init__( )

        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3


    def getPoint(self, t ):
        v0 = self.v0
        v1 = self.v1
        v2 = self.v2
        v3 = self.v3

        return Vector3(
            CubicBezier( t, v0.x, v1.x, v2.x, v3.x ),
            CubicBezier( t, v0.y, v1.y, v2.y, v3.y ),
            CubicBezier( t, v0.z, v1.z, v2.z, v3.z )
        )

        
class QuadraticBezierCurve3(Curve):
    def __init__(self, v0, v1, v2 ):
        super().__init__( )
        
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

    def getPoint(self, t ):
        v0 = self.v0
        v1 = self.v1
        v2 = self.v2

        return Vector3(
            QuadraticBezier( t, v0.x, v1.x, v2.x ),
            QuadraticBezier( t, v0.y, v1.y, v2.y ),
            QuadraticBezier( t, v0.z, v1.z, v2.z )
        )

        
class LineCurve3(Curve):
    def __init__(self, v1, v2 ):
        super().__init__()

        self.v1 = v1
        self.v2 = v2

    def getPoint(self, t ):
        if t == 1:
            return self.v2.clone()

        vector = Vector3()

        vector.subVectors( self.v2, self.v1 )    # // diff
        vector.multiplyScalar( t )
        vector.add( self.v1 )

        return vector


class ArcCurve(EllipseCurve):
    def __init__(self, aX, aY, aRadius, aStartAngle, aEndAngle, aClockwise ):
        super().__init__( aX, aY, aRadius, aRadius, aStartAngle, aEndAngle, aClockwise )

