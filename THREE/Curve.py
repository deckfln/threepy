"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 * Extensible curve object
 *
 * Some common of curve methods:
 * .getPoint(t), getTangent(t)
 * .getPointAt(u), getTangentAt(u)
 * .getPoints(), .getSpacedPoints()
 * .getLength()
 * .updateArcLengths()
 *
 * This following curves inherit from THREE.Curve:
 *
 * -- 2D curves --
 * THREE.ArcCurve
 * THREE.CubicBezierCurve
 * THREE.EllipseCurve
 * THREE.LineCurve
 * THREE.QuadraticBezierCurve
 * THREE.SplineCurve
 *
 * -- 3D curves --
 * THREE.CatmullRomCurve3
 * THREE.CubicBezierCurve3
 * THREE.LineCurve3
 * THREE.QuadraticBezierCurve3
 *
 * A series of curves can be represented as a THREE.CurvePath.
 *
 **/
"""
from THREE.Vector3 import *
from THREE.Matrix4 import *


import THREE._Math as _Math
from THREE.Constants import *
from THREE.pyOpenGLObject import *


class Curve(pyOpenGLObject):
    """
    /**************************************************************
     *    Abstract Curve base class
     **************************************************************/
    """
    def __init__(self):
        super().__init__()
        self.arcLengthDivisions = 200
        self.needsUpdate = False
        self.cacheArcLengths = None
        self.type = None

    def getPoint(self, t):
        """
        # // Virtual base class method to overwrite and implement in subclasses
        # //    - t [0 .. 1]
        """
        print( 'THREE.Curve: .getPoint() not implemented.' )
        return None

    def getPointAt(self, u ):
        """
        # // Get point at relative position in curve according to arc length
        # // - u [0 .. 1]
        """
        t = self.getUtoTmapping( u )
        return self.getPoint( t )

    def getPoints(self, divisions ):
        """
        # // Get sequence of points using getPoint( t )
        """
        if divisions is None:
            divisions = 5

        points = []

        for d in range(divisions+1):
            points.append( self.getPoint( d / divisions ) )

        return points

    def getSpacedPoints(self, divisions ):
        """
        # // Get sequence of points using getPointAt( u )
        """
        if divisions is None:
            divisions = 5

        points = []

        for d in range(divisions+1):
            points.append( self.getPointAt( d / divisions ) )

        return points

    def getLength(self):
        """
        # // Get total curve arc length
        """
        lengths = self.getLengths()
        return lengths[ len(lengths) - 1 ]

    def getLengths(self, divisions=None ):
        """
        # // Get list of cumulative segment lengths
        """
        if divisions is None:
            divisions = self.arcLengthDivisions

        if self.cacheArcLengths and \
            ( len(self.cacheArcLengths) == divisions + 1 ) and \
            not self.needsUpdate:

            return self.cacheArcLengths

        self.needsUpdate = False

        cache = []
        last = self.getPoint( 0 )
        sum = 0

        cache.append( 0 )

        for p in range(1, divisions+1):
            current = self.getPoint( p / divisions )
            sum += current.distanceTo( last )
            cache.append( sum )
            last = current

        self.cacheArcLengths = cache

        return cache    # # // { sums: cache, sum: sum }; Sum is in the last element.

    def updateArcLengths(self):
        self.needsUpdate = True
        self.getLengths()

    def getUtoTmapping(self, u, distance=None):
        """
        # // Given u ( 0 .. 1 ), get a t to find p. This gives you points which are equidistant
        """
        arcLengths = self.getLengths()

        i = 0
        il = len(arcLengths)

        targetArcLength = 0     # # // The targeted u distance value to get

        if distance:
            targetArcLength = distance
        else:
            targetArcLength = u * arcLengths[ il - 1 ]

        # // binary search for the index with largest value smaller than target u distance
        low = 0
        high = il - 1
        comparison = 0

        while low <= high:
            i = math.floor( low + ( high - low ) / 2 )     # // less likely to overflow, though probably not issue here, JS doesn't really have integers, all numbers are floats
            comparison = arcLengths[ i ] - targetArcLength

            if comparison < 0:
                low = i + 1
            elif comparison > 0:
                high = i - 1
            else:
                high = i
                break
                # // DONE

        i = high

        if arcLengths[ i ] == targetArcLength:
            return i / ( il - 1 )

        # // we could get finer grain at lengths, or use simple interpolation between two points

        lengthBefore = arcLengths[ i ]
        lengthAfter = arcLengths[ i + 1 ]

        segmentLength = lengthAfter - lengthBefore

        # // determine where we are between the 'before' and 'after' points

        segmentFraction = ( targetArcLength - lengthBefore ) / segmentLength

        # // add that fractional amount to t

        t = ( i + segmentFraction ) / ( il - 1 )

        return t

    def getTangent(self, t ):
        """
        # // Returns a unit vector tangent at t
        # // In case any sub curve does not implement its tangent derivation,
        # // 2 points a small delta apart will be used to find its gradient
        # // which seems to give a reasonable approximation
        """
        delta = 0.0001
        t1 = t - delta
        t2 = t + delta

        # // Capping in case of danger

        if t1 < 0:
            t1 = 0
        if t2 > 1:
            t2 = 1

        pt1 = self.getPoint( t1 )
        pt2 = self.getPoint( t2 )

        vec = pt2.clone().sub( pt1 )
        return vec.normalize()

    def getTangentAt(self, u ):
        t = self.getUtoTmapping( u )
        return self.getTangent( t )

    def computeFrenetFrames(self, segments, closed ):
        # // see http:# //www.cs.indiana.edu/pub/techreports/TR425.pdf

        normal = Vector3()

        tangents = [None for i in range(segments+1)]
        normals = [None for i in range(segments+1)]
        binormals = [None for i in range(segments+1)]

        vec = Vector3()
        mat = Matrix4()

        # // compute the tangent vectors for each segment on the curve

        for i in range(segments+1):
            u = i / segments

            tangents[i] = self.getTangentAt(u)
            tangents[i].normalize()

        # // select an initial normal vector perpendicular to the first tangent vector,
        # // and in the direction of the minimum tangent xyz component

        normals[ 0 ] = Vector3()
        binormals[ 0 ] = Vector3()
        min = float("+inf")
        tx = abs( tangents[ 0 ].x )
        ty = abs( tangents[ 0 ].y )
        tz = abs( tangents[ 0 ].z )

        if tx <= min:
            min = tx
            normal.set( 1, 0, 0 )

        if ty <= min:
            min = ty
            normal.set( 0, 1, 0 )

        if tz <= min:
            normal.set( 0, 0, 1 )

        vec.crossVectors( tangents[ 0 ], normal ).normalize()

        normals[ 0 ].crossVectors( tangents[ 0 ], vec )
        binormals[ 0 ].crossVectors( tangents[ 0 ], normals[ 0 ] )

        # // compute the slowly-varying normal and binormal vectors for each segment on the curve

        for i in range(1, segments+1):
            normals[ i ] = normals[ i - 1 ].clone()

            binormals[ i ] = binormals[ i - 1 ].clone()

            vec.crossVectors( tangents[ i - 1 ], tangents[ i ] )

            if vec.length() > Number.EPSILON:
                vec.normalize()

                theta = math.acos( _Math.clamp( tangents[ i - 1 ].dot( tangents[ i ] ), - 1, 1 ) )  # // clamp for floating pt errors

                normals[ i ].applyMatrix4( mat.makeRotationAxis( vec, theta ) )

            binormals[ i ].crossVectors( tangents[ i ], normals[ i ] )

        # // if the curve is closed, postprocess the vectors so the first and last normal vectors are the same

        if closed:
            theta = math.acos( _Math.clamp( normals[ 0 ].dot( normals[ segments ] ), - 1, 1 ) )
            theta /= segments

            if tangents[ 0 ].dot( vec.crossVectors( normals[ 0 ], normals[ segments ] ) ) > 0:
                theta = - theta

            for i in range(1, segments+1):
                # // twist a little...
                normals[ i ].applyMatrix4( mat.makeRotationAxis( tangents[ i ], theta * i ) )
                binormals[ i ].crossVectors( tangents[ i ], normals[ i ] )

        return {
            'tangents': tangents,
            'normals': normals,
            'binormals': binormals
        }


class LineCurve(Curve):
    isLineCurve = True

    def __init__(self, v1, v2 ):
        super().__init__()
        self.set_class(isLineCurve)

        self.v1 = v1
        self.v2 = v2

    def getPoint(self, t ):
        if t == 1:
            return self.v2.clone()

        point = self.v2.clone().sub( self.v1 )
        point.multiplyScalar( t ).add( self.v1 )

        return point

    def getPointAt(self, u ):
        """
        # // Line curve is linear, so we can overwrite default getPointAt
        """
        return self.getPoint( u )

    def getTangent(self, t ):
        tangent = self.v2.clone().sub( self.v1 )

        return tangent.normalize()
