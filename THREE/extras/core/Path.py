"""
/**
 * @author zz85 / http://www.lab4games.net/zz85/blog
 * Creates free form 2d path using series of points, lines or curves.
 **/
"""
from THREE.extras.core.CurvePath import *
from THREE.math.Vector2 import *


class Path(CurvePath):
    def __init__(self, points=None ):
        super().__init__( )
        self.type = 'Path'
        self.currentPoint = Vector2()

        if points:
            self.setFromPoints( points )

    def setFromPoints(self, points ):
        self.moveTo( points[ 0 ].x, points[ 0 ].y )

        for i in range(1, len(points)):
            self.lineTo( points[ i ].x, points[ i ].y )

    def moveTo(self, x, y ):
        self.currentPoint.set( x, y )    # // TODO consider referencing vectors instead of copying?

    def lineTo(self, x, y ):
        curve = LineCurve( self.currentPoint.clone(), Vector2( x, y ) )
        self.curves.append( curve )

        self.currentPoint.set( x, y )

    def quadraticCurveTo(self, aCPx, aCPy, aX, aY ):
        curve = QuadraticBezierCurve(
            self.currentPoint.clone(),
            Vector2( aCPx, aCPy ),
            Vector2( aX, aY )
        )

        self.curves.append( curve )

        self.currentPoint.set( aX, aY )

    def bezierCurveTo(self, aCP1x, aCP1y, aCP2x, aCP2y, aX, aY ):
        curve = CubicBezierCurve(
            self.currentPoint.clone(),
            Vector2( aCP1x, aCP1y ),
            Vector2( aCP2x, aCP2y ),
            Vector2( aX, aY )
        )

        self.curves.append( curve )

        self.currentPoint.set( aX, aY )

    def splineThru(self, pts ):
        npts = [ self.currentPoint.clone() ].extend( pts )

        curve = SplineCurve( npts )
        self.curves.append( curve )

        self.currentPoint.copy( pts[ pts.length - 1 ] )

    def arc(self, aX, aY, aRadius, aStartAngle, aEndAngle, aClockwise ):
        x0 = self.currentPoint.x
        y0 = self.currentPoint.y

        self.absarc( aX + x0, aY + y0, aRadius, aStartAngle, aEndAngle, aClockwise )

    def absarc(self, aX, aY, aRadius, aStartAngle, aEndAngle, aClockwise ):
        self.absellipse( aX, aY, aRadius, aRadius, aStartAngle, aEndAngle, aClockwise )

    def ellipse(self, aX, aY, xRadius, yRadius, aStartAngle, aEndAngle, aClockwise, aRotation ):
        x0 = self.currentPoint.x
        y0 = self.currentPoint.y

        self.absellipse( aX + x0, aY + y0, xRadius, yRadius, aStartAngle, aEndAngle, aClockwise, aRotation )

    def absellipse(self, aX, aY, xRadius, yRadius, aStartAngle, aEndAngle, aClockwise, aRotation ):
        curve = EllipseCurve( aX, aY, xRadius, yRadius, aStartAngle, aEndAngle, aClockwise, aRotation )

        if len(self.curves) > 0:
            # // if a previous curve is present, attempt to join
            firstPoint = curve.getPoint( 0 )

            if not firstPoint.equals( self.currentPoint ):
                self.lineTo( firstPoint.x, firstPoint.y )

        self.curves.append( curve )

        lastPoint = curve.getPoint( 1 )
        self.currentPoint.copy( lastPoint )

    def copy(self, source):
        super().copy(source)

        self.currentPoint.copy( source.currentPoint )

        return self

    def toJSON(self):
        data = super().toJSON()

        data['currentPoint'] = self.currentPoint.toArray()

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.currentPoint.fromArray( json['currentPoint'] )

        return self
