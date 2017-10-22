"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 *
 **/
"""
from THREE.Curve import *
from THREE.Bezier import *
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Geometry import *


"""
/**************************************************************
 *    Curved Path - a curve path is simply a array of connected
 *  curves, but retains the api of a curve
 **************************************************************/
"""

class CurvePath(Curve):
    def __init__(self):
        super().__init__()

        self.curves = []

        self.autoClose = False    # # // Automatically closes the path

    def add(self, curve ):
        self.curves.append( curve )

    def closePath(self):
        # // Add a line curve if start and end of lines are not connected
        startPoint = self.curves[ 0 ].getPoint( 0 )
        endPoint = self.curves[ len(self.curves) - 1 ].getPoint( 1 )

        if not startPoint.equals( endPoint ):
            self.curves.append( LineCurve( endPoint, startPoint ) )

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
            elif curve and curve.isSplineCurve:
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

    """
    /**************************************************************
     *    Create Geometries Helpers
     **************************************************************/
    
    # /// Generate geometry from path points (for Line or Points objects)
    """
    def createPointsGeometry(self, divisions ):
        pts = self.getPoints( divisions )
        return self.createGeometry( pts )

    # // Generate geometry from equidistant sampling along the path

    def createSpacedPointsGeometry(self, divisions ):
        pts = self.getSpacedPoints( divisions )
        return self.createGeometry( pts )

    def createGeometry(self, points ):
        geometry = Geometry()

        for i in range(len(points)):
            point = points[ i ]
            geometry.vertices.append( Vector3( point.x, point.y, point.z or 0 ) )

        return geometry


class EllipseCurve(Curve):
    isEllipseCurve = True
    
    def __init__(self, aX, aY, xRadius, yRadius, aStartAngle, aEndAngle, aClockwise, aRotation ):
        super().__init__( )
        self.set_class(isEllipseCurve)

        self.aX = aX
        self.aY = aY

        self.xRadius = xRadius
        self.yRadius = yRadius

        self.aStartAngle = aStartAngle
        self.aEndAngle = aEndAngle

        self.aClockwise = aClockwise

        self.aRotation = aRotation or 0

    def getPoint(self, t ):
        twoPi = math.pi * 2
        deltaAngle = self.aEndAngle - self.aStartAngle
        samePoints = abs( deltaAngle ) < Number.EPSILON

        # // ensures that deltaAngle is 0 .. 2 PI
        while deltaAngle < 0:
            deltaAngle += twoPi
        while deltaAngle > twoPi:
            deltaAngle -= twoPi

        if deltaAngle < Number.EPSILON:
            if samePoints:
                deltaAngle = 0
            else:
                deltaAngle = twoPi

        if self.aClockwise == True and not samePoints:
            if deltaAngle == twoPi:
                deltaAngle = - twoPi
            else:
                deltaAngle = deltaAngle - twoPi

        angle = self.aStartAngle + t * deltaAngle
        x = self.aX + self.xRadius * math.cos( angle )
        y = self.aY + self.yRadius * math.sin( angle )

        if self.aRotation != 0:
            cos = math.cos( self.aRotation )
            sin = math.sin( self.aRotation )

            tx = x - self.aX
            ty = y - self.aY

            # // Rotate the point about the center of the ellipse.
            x = tx * cos - ty * sin + self.aX
            y = tx * sin + ty * cos + self.aY

        return Vector2( x, y )

        
class SplineCurve(Curve):
    isSplineCurve = True
    
    def __init__(self, points=None ):
        super().__init__()

        self.points = [] if points is None else points


    def getPoint(self, t ):
        points = self.points
        point = ( len(self.points) - 1 ) * t

        intPoint = int( point )
        weight = point - intPoint

        point0 = points[ intPoint if intPoint == 0 else intPoint - 1 ]
        point1 = points[ intPoint ]
        point2 = points[ points.length - 1 if intPoint > points.length - 2 else intPoint + 1 ]
        point3 = points[ points.length - 1 if intPoint > points.length - 3 else intPoint + 2 ]

        return Vector2(
            CatmullRom( weight, point0.x, point1.x, point2.x, point3.x ),
            CatmullRom( weight, point0.y, point1.y, point2.y, point3.y )
        )

        
class CubicBezierCurve(Curve):
    def __init__(self, v0, v1, v2, v3 ):
        super().__init__()

        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def getPoint(self, t ):
        v0 = self.v0
        v1 = self.v1
        v2 = self.v2
        v3 = self.v3

        return Vector2(
            CubicBezier( t, v0.x, v1.x, v2.x, v3.x ),
            CubicBezier( t, v0.y, v1.y, v2.y, v3.y )
        )


class QuadraticBezierCurve(Curve):
    def __init__(self, v0, v1, v2 ):
        super().__init__()

        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

    def getPoint(self, t ):
        v0 = self.v0
        v1 = self.v1
        v2 = self.v2

        return Vector2(
            QuadraticBezier( t, v0.x, v1.x, v2.x ),
            QuadraticBezier( t, v0.y, v1.y, v2.y )
        )
