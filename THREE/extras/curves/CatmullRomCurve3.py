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
from THREE.extras.core.Curve import *


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
    isCatmullRomCurve3 = True

    def __init__(self, points=None, closed=False, curveType='centripetal', tension=0.5):
        super().__init__( )
        self.type = 'CatmullRomCurve3'

        if len(points) < 2:
            raise RuntimeError( 'THREE.CatmullRomCurve3: Points array needs at least two entries.' )

        self.points = points or []
        self.closed = closed
        self.curveType = curveType
        self.tension = tension

    def getPoint(self, t, optionalTarget=None):
        if optionalTarget is None:
            optionalTarget = Vector3()

        point = optionalTarget
        points = self.points
        l = len(points)

        p = ( l - ( 0 if self.closed else 1 ) ) * t
        intPoint = math.floor( p )
        weight = p - intPoint

        if self.closed:
            intPoint += 0 if intPoint > 0 else ( math.floor( abs( intPoint ) / l ) + 1 ) * l

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

        if self.curveType == 'centripetal' or self.curveType == 'chordal':
            # // init Centripetal / Chordal Catmull-Rom
            pow = 0.5 if self.curveType == 'chordal' else 0.25
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

        elif self.curveType == 'catmullrom':
            px.initCatmullRom( p0.x, p1.x, p2.x, p3.x, self.tension )
            py.initCatmullRom( p0.y, p1.y, p2.y, p3.y, self.tension )
            pz.initCatmullRom( p0.z, p1.z, p2.z, p3.z, self.tension )

        return point.set( px.calc( weight ), py.calc( weight ), pz.calc( weight ) )

    def copy(self, source):
        super().copy(source)

        self.points = []

        for point in source.points:
            self.points.append( point.clone() )

        self.closed = source.closed
        self.curveType = source.curveType
        self.tension = source.tension

        return self

    def toJSON(self):
        data = super().toJSON()

        data['points'] = []

        for point in self.points:
            data['points'].append( point.toArray() )

        data['closed'] = self.closed
        data['curveType'] = self.curveType
        data['tension'] = self.tension

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.points = []

        for point in json['points']:
            self.points.append( Vector3().fromArray( point ) )

        self.closed = json['closed']
        self.curveType = json['curveType']
        self.tension = json['tension']

        return self
