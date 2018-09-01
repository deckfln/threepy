"""
/**
 * @author zz85 / http://www.lab4games.net/zz85/blog
 * minimal class for proxing functions to Path. Replaces old "extractSubpaths()"
 **/
"""

from THREE.math.Color import *
from THREE.extras.core.Path import *
from THREE.extras.core.Shape import *


def _toShapesNoHoles(inSubpaths):
    shapes = []
    for i in range(len(inSubpaths.length)):
        tmpPath = inSubpaths[i]

        tmpShape = Shape()
        tmpShape.curves = tmpPath.curves

        shapes.append(tmpShape)

    return shapes


def _isPointInsidePolygon(inPt, inPolygon):
    polyLen = len(inPolygon)

    """
    # // inPt on polygon contour => immediate success    or
    # // toggling of inside/outside at every single! intersection point of an edge
    # //  with the horizontal line through inPt, left of inPt
    # //  not counting lowerY endpoints of edges and whole edges on that line
    """
    inside = False
    p = polyLen - 1
    for q in range(polyLen):
        edgeLowPt = inPolygon[p]
        edgeHighPt = inPolygon[q]

        edgeDx = edgeHighPt.x - edgeLowPt.x
        edgeDy = edgeHighPt.y - edgeLowPt.y

        if abs(edgeDy) > Number.EPSILON:
            # // not parallel
            if edgeDy < 0:
                edgeLowPt = inPolygon[q]
                edgeDx = - edgeDx
                edgeHighPt = inPolygon[p]
                edgeDy = - edgeDy

            if inPt.y < edgeLowPt.y or inPt.y > edgeHighPt.y:
                continue

            if inPt.y == edgeLowPt.y:
                if inPt.x == edgeLowPt.x:
                    return True  # // inPt is on contour ?
                    # // continue;                # // no intersection or edgeLowPt => doesn't count !!!

            else:
                perpEdge = edgeDy * (inPt.x - edgeLowPt.x) - edgeDx * (inPt.y - edgeLowPt.y)
                if perpEdge == 0:
                    return True  # // inPt is on contour ?
                if perpEdge < 0:
                    continue
                inside = not inside  # // True intersection left of inPt

        else:
            # // parallel or collinear
            if inPt.y != edgeLowPt.y:
                continue  # // parallel
            # // edge lies on the same horizontal line as inPt
            if ((edgeHighPt.x <= inPt.x) and (inPt.x <= edgeLowPt.x)) or \
                    ((edgeLowPt.x <= inPt.x) and (inPt.x <= edgeHighPt.x)):
                return True  # // inPt: Point on contour !
                # // continue

        p = q

    return inside


class ShapePath:
    def __init__(self):
        self.type = 'ShapePath'

        self.color = Color()
        self.subPaths = []
        self.currentPath = None

    def moveTo(self, x, y ):
        self.currentPath = Path()
        self.subPaths.append( self.currentPath )
        self.currentPath.moveTo( x, y )

    def lineTo(self, x, y ):
        self.currentPath.lineTo( x, y )

    def quadraticCurveTo(self, aCPx, aCPy, aX, aY ):
        self.currentPath.quadraticCurveTo( aCPx, aCPy, aX, aY )

    def bezierCurveTo(self, aCP1x, aCP1y, aCP2x, aCP2y, aX, aY ):
        self.currentPath.bezierCurveTo( aCP1x, aCP1y, aCP2x, aCP2y, aX, aY )

    def splineThru(self, pts ):
        self.currentPath.splineThru( pts )

    def toShapes(self, isCCW, noHoles=False ):
        isClockWise = ShapeUtils.isClockWise

        subPaths = self.subPaths
        if len(subPaths) == 0:
            return []

        if noHoles:
            return _toShapesNoHoles( subPaths )

        shapes = []

        if len(subPaths) == 1:
            tmpPath = subPaths[ 0 ]
            tmpShape = Shape()
            tmpShape.curves = tmpPath.curves
            shapes.append( tmpShape )
            return shapes

        holesFirst = not isClockWise( subPaths[ 0 ].getPoints() )
        holesFirst = not holesFirst if isCCW else holesFirst

        # // console.log("Holes first", holesFirst)

        newShapes = [None for i in range(len(self.subPaths))]
        newShapeHoles = [None for i in range(len(self.subPaths))]
        mainIdx = 0

        newShapes[ mainIdx ] = None
        newShapeHoles[ mainIdx ] = []

        for i in range(len(self.subPaths)):
            tmpPath = subPaths[ i ]
            tmpPoints = tmpPath.getPoints()
            solid = isClockWise( tmpPoints )
            solid = not solid if isCCW else solid

            if solid:
                if ( not holesFirst ) and ( newShapes[ mainIdx ] ):
                    mainIdx += 1

                newShapes[ mainIdx ] = { 's': Shape(), 'p': tmpPoints }
                newShapes[ mainIdx ]['s'].curves = tmpPath.curves

                if holesFirst:
                    mainIdx += 1
                newShapeHoles[ mainIdx ] = []

                # //console.log('cw', i)

            else:
                newShapeHoles[ mainIdx ].append( { 'h': tmpPath, 'p': tmpPoints[ 0 ] } )

                # //console.log('ccw', i)


        # // only Holes? -> probably all Shapes with wrong orientation
        if not newShapes[ 0 ]:
            return _toShapesNoHoles( self.subPaths )

        if len(newShapes) > 1:
            betterShapeHoles = [[] for i in range(mainIdx+1)]

            ambiguous = False
            toChange = []

            for sIdx in range(mainIdx+1):
                sho = newShapeHoles[ sIdx ]

                for hIdx in range(len(sho)):
                    ho = sho[ hIdx ]
                    hole_unassigned = True

                    for s2Idx in range(mainIdx+1):
                        if _isPointInsidePolygon( ho['p'], newShapes[ s2Idx ]['p'] ):

                            if sIdx != s2Idx:
                                toChange.append( { 'froms': sIdx, 'tos': s2Idx, 'hole': hIdx } )
                            if hole_unassigned:
                                hole_unassigned = False
                                betterShapeHoles[ s2Idx ].append( ho )

                            else:
                                ambiguous = True

                    if hole_unassigned:
                        betterShapeHoles[ sIdx ].append( ho )

            # // console.log("ambiguous: ", ambiguous)
            if len(toChange) > 0:
                # // console.log("to change: ", toChange)
                if not ambiguous:
                    newShapeHoles = betterShapeHoles

        for i in range(mainIdx+1):
            tmpShape = newShapes[ i ]['s']
            shapes.append( tmpShape )
            tmpHoles = newShapeHoles[ i ]

            for j in range(len(tmpHoles)):
                tmpShape.holes.append( tmpHoles[ j ]['h'] )

        # //console.log("shape", shapes)

        return shapes
