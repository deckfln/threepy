"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 *
 **/
"""
from THREE.extras.core.Curves import *


"""
/**************************************************************
 *    Curved Path - a curve path is simply a array of connected
 *  curves, but retains the api of a curve
 **************************************************************/
"""


class CurvePath(Curve):
    def __init__(self):
        super().__init__()

        self.type = 'CurvePath'
        self.curves = []

        self.autoClose = False    # # // Automatically closes the path

    def add(self, curve ):
        self.curves.append( curve )

    def closePath(self):
        global Curves
        # // Add a line curve if start and end of lines are not connected
        startPoint = self.curves[ 0 ].getPoint( 0 )
        endPoint = self.curves[ len(self.curves) - 1 ].getPoint( 1 )

        if not startPoint.equals( endPoint ):
            self.curves.append( Curves['LineCurve']( endPoint, startPoint ) )

    """
    # // To get accurate point with reference to
    # // entire path distance at time t,
    # // following has to be done:

    # // 1. Length of each sub path have to be known
    # // 2. Locate and identify type of curve
    # // 3. Get t for the curve
    # // 4. Return curve.getPointAt(t')
    """
    def getPoint(self, t):
        d = t * self.getLength()
        curveLengths = self.getCurveLengths()
        i = 0

        # // To think about boundaries points.

        while i < len(curveLengths):
            if curveLengths[ i ] >= d:
                diff = curveLengths[ i ] - d
                curve = self.curves[ i ]

                segmentLength = curve.getLength()
                u = 0 if segmentLength == 0 else 1 - diff / segmentLength

                return curve.getPointAt( u )

            i += 1

        return None

        # // loop where sum != 0, sum > d , sum+1 <d

    """
    # // We cannot use the default THREE.Curve getPoint() with getLength() because in
    # // THREE.Curve, getLength() depends on getPoint() but in THREE.CurvePath
    # // getPoint() depends on getLength
    """
    def getLength(self):
        lens = self.getCurveLengths()
        return lens[ len(lens) - 1 ]

    # // cacheLengths must be recalculated.
    def updateArcLengths(self):
        self.needsUpdate = True
        self.cacheLengths = None
        self.getCurveLengths()

    """
    # // Compute lengths and cache them
    # // We cannot overwrite getLengths() because UtoT mapping uses it.
    """
    def getCurveLengths(self):
        # // We use cache values if curves and cache array are same length
        if self.cacheLengths and len(self.cacheLengths) == len(self.curves):
            return self.cacheLengths

        # // Get length of sub-curve
        # // Push sums into cached array

        lengths = []
        sums = 0

        for i in range(len(self.curves)):
            sums += self.curves[ i ].getLength()
            lengths.append( sums )

        self.cacheLengths = lengths

        return lengths

    def getSpacedPoints(self, divisions ):
        if divisions is None:
            divisions = 40

        points = []

        for i in range(divisions+1):
            points.append( self.getPoint( i / divisions ) )

        if self.autoClose:
            points.append( points[ 0 ] )

        return points

    def getPoints(self, divisions=12 ):
        points = []
        last = None

        for curve in self.curves:
            if curve and curve.my_class(isEllipseCurve):
                resolution = divisions * 2
            elif curve and curve.isLineCurve:
                resolution = 1
            elif curve and curve.isSplineCurve or curve.isLineCurve3:
                resolution = divisions * len(curve.points)
            else:
                resolution = divisions

            pts = curve.getPoints( resolution )

            for j in range(len(pts)):
                point = pts[ j ]

                if last and last.equals( point ):
                    continue # // ensures no consecutive points are duplicates

                points.append( point )
                last = point

        if self.autoClose and len(points) > 1 and not points[ len(points) - 1 ].equals( points[ 0 ] ):
            points.append( points[ 0 ] )

        return points

    def copy(self, source):
        super().copy( source )

        self.curves = []

        for curve in source.curves:
            self.curves.append( curve.clone() )

        self.autoClose = source.autoClose

        return self

    def toJSON(self):
        data = super().toJSON()

        data['autoClose'] = self.autoClose
        data['curves'] = []

        for curve in self.curves:
            data['curves'].append( curve.toJSON())

        return data

    def fromJSON(self, json):
        global Curves
        super().fromJSON(json)

        self.autoClose = json.autoClose
        self.curves = []

        for curve in json['curves']:
            self.curves.append( Curves[ curve.type ]().fromJSON( curve ) )

        return self

