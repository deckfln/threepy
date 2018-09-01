"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 */
"""
from THREE.Constants import *


# // calculate area of the contour polygon

def area( contour ):
    n = len(contour)
    a = 0.0

    q = 0
    p = n -1
    while q < n:
        a += contour[ p ].x * contour[ q ].y - contour[ q ].x * contour[ p ].y
        p = q
        q += 1

    return a * 0.5


def isClockWise( pts ):
    return area( pts ) < 0


def triangulate(contour, indices):
    """
    /**
     * This code is a quick port of code written in C++ which was submitted to
     * flipcode.com by John W. Ratcliff  # // July 22, 2000
     * See original code and more information here:
     * http:# //www.flipcode.com/archives/Efficient_Polygon_Triangulation.shtml
     *
     * ported to actionscript by Zevan Rosser
     * www.actionsnippet.com
     *
     * ported to javascript by Joshua Koo
     * http:# //www.lab4games.net/zz85/blog
     *
     */
    """
    def snip( contour, u, v, w, n, verts ):
        ax = contour[ verts[ u ] ].x
        ay = contour[ verts[ u ] ].y

        bx = contour[ verts[ v ] ].x
        by = contour[ verts[ v ] ].y

        cx = contour[ verts[ w ] ].x
        cy = contour[ verts[ w ] ].y

        if ( bx - ax ) * ( cy - ay ) - ( by - ay ) * ( cx - ax ) <= 0:
            return False

        aX = cx - bx;  aY = cy - by
        bX = ax - cx;  bY = ay - cy
        cX = bx - ax;  cY = by - ay

        for p in range(n):
            px = contour[ verts[ p ] ].x
            py = contour[ verts[ p ] ].y

            if ( ( px == ax ) and ( py == ay ) ) or \
                 ( ( px == bx ) and ( py == by ) ) or \
                 ( ( px == cx ) and ( py == cy ) ):
                continue

            apx = px - ax;  apy = py - ay
            bpx = px - bx;  bpy = py - by
            cpx = px - cx;  cpy = py - cy

            # // see if p is inside triangle abc

            aCROSSbp = aX * bpy - aY * bpx
            cCROSSap = cX * apy - cY * apx
            bCROSScp = bX * cpy - bY * cpx

            if ( aCROSSbp >= - Number.EPSILON ) and ( bCROSScp >= - Number.EPSILON ) and ( cCROSSap >= - Number.EPSILON ):
                return False

        return True


    # // takes in an contour array and returns

    n = len(contour)

    if n < 3:
        return None

    result = []
    verts = [None for i in range(n)]
    vertIndices = []

    # /* we want a counter-clockwise polygon in verts */

    if area( contour ) > 0.0:
        for v in range(n):
            verts[ v ] = v

    else:
        for v in range(n):
            verts[ v ] = ( n - 1 ) - v

    nv = n

    # /*  remove nv - 2 vertices, creating 1 triangle every time */

    count = 2 * nv   # /* error detection */

    v = nv - 1
    while nv > 2:
        # /* if we loop, it is probably a non-simple polygon */

        if count <= 0:
            count -= 1
            # //** Triangulate: ERROR - probable bad polygon!

            # //throw ( "Warning, unable to triangulate polygon!" )
            # //return null
            # // Sometimes warning is fine, especially polygons are triangulated in reverse.
            print( 'THREE.ShapeUtils: Unable to triangulate polygon! in triangulate()' )

            if indices:
                return vertIndices
            return result

        # /* three consecutive vertices in current polygon, <u,v,w> */

        u = v
        if nv <= u:
            u = 0    #     /* previous */
        v = u + 1
        if nv <= v:
            v = 0    #     /* v    */
        w = v + 1
        if nv <= w:
            w = 0    #     /* next     */

        if snip( contour, u, v, w, nv, verts ):
            # /* True names of the vertices */

            a = verts[ u ]
            b = verts[ v ]
            c = verts[ w ]

            # /* output Triangle */

            result.append( [ contour[ a ],    contour[ b ],    contour[ c ] ] )
            vertIndices.append( [ verts[ u ], verts[ v ], verts[ w ] ] )

            # /* remove v from the remaining polygon */

            s = v
            t = v +1
            while t < nv:
                verts[ s ] = verts[ t ]
                s += 1
                t += 1

            nv -= 1

            # /* reset error detection counter */

            count = 2 * nv

    if indices:
        return vertIndices
    return result


def triangulateShape( contour, holes ):
    def removeDupEndPts(points):
        l = len(points)

        if l > 2 and points[l - 1].equals( points[0] ):
            points.pop()

    removeDupEndPts(contour)
    for h in holes:
        removeDupEndPts(h)

    def point_in_segment_2D_colin( inSegPt1, inSegPt2, inOtherPt ):
        # // inOtherPt needs to be collinear to the inSegment
        if inSegPt1.x != inSegPt2.x:
            if inSegPt1.x < inSegPt2.x:
                return    ( ( inSegPt1.x <= inOtherPt.x ) and ( inOtherPt.x <= inSegPt2.x ) )

            else:
                return    ( ( inSegPt2.x <= inOtherPt.x ) and ( inOtherPt.x <= inSegPt1.x ) )

        else:
            if inSegPt1.y < inSegPt2.y:
                return    ( ( inSegPt1.y <= inOtherPt.y ) and ( inOtherPt.y <= inSegPt2.y ) )

            else:
                return    ( ( inSegPt2.y <= inOtherPt.y ) and ( inOtherPt.y <= inSegPt1.y ) )

    def intersect_segments_2D( inSeg1Pt1, inSeg1Pt2, inSeg2Pt1, inSeg2Pt2, inExcludeAdjacentSegs ):
        seg1dx = inSeg1Pt2.x - inSeg1Pt1.x
        seg1dy = inSeg1Pt2.y - inSeg1Pt1.y
        seg2dx = inSeg2Pt2.x - inSeg2Pt1.x
        seg2dy = inSeg2Pt2.y - inSeg2Pt1.y

        seg1seg2dx = inSeg1Pt1.x - inSeg2Pt1.x
        seg1seg2dy = inSeg1Pt1.y - inSeg2Pt1.y

        limit        = seg1dy * seg2dx - seg1dx * seg2dy
        perpSeg1    = seg1dy * seg1seg2dx - seg1dx * seg1seg2dy

        if abs( limit ) > Number.EPSILON:
            # // not parallel
            if limit > 0:
                if ( perpSeg1 < 0 ) or ( perpSeg1 > limit ):
                    return []
                perpSeg2 = seg2dy * seg1seg2dx - seg2dx * seg1seg2dy
                if ( perpSeg2 < 0 ) or ( perpSeg2 > limit ):
                    return []

            else:
                if ( perpSeg1 > 0 ) or ( perpSeg1 < limit ):
                    return []
                perpSeg2 = seg2dy * seg1seg2dx - seg2dx * seg1seg2dy
                if ( perpSeg2 > 0 ) or ( perpSeg2 < limit ):
                    return []

            # // i.e. to reduce rounding errors
            # // intersection at endpoint of segment#1?
            if perpSeg2 == 0:
                if ( inExcludeAdjacentSegs ) and \
                     ( ( perpSeg1 == 0 ) or ( perpSeg1 == limit ) ):
                    return []
                return [ inSeg1Pt1 ]

            if perpSeg2 == limit:
                if ( inExcludeAdjacentSegs ) and \
                     ( ( perpSeg1 == 0 ) or ( perpSeg1 == limit ) ):
                    return []
                return [ inSeg1Pt2 ]

            # // intersection at endpoint of segment#2?
            if perpSeg1 == 0:
                return [ inSeg2Pt1 ]
            if perpSeg1 == limit:
                return [ inSeg2Pt2 ]

            # // return real intersection point
            factorSeg1 = perpSeg2 / limit
            return    [ { 'x': inSeg1Pt1.x + factorSeg1 * seg1dx,
                        'y': inSeg1Pt1.y + factorSeg1 * seg1dy } ]

        else:
            # // parallel or collinear
            if ( perpSeg1 != 0 ) or \
                 ( seg2dy * seg1seg2dx != seg2dx * seg1seg2dy ):
                return []

            # // they are collinear or degenerate
            seg1Pt = ( ( seg1dx == 0 ) and ( seg1dy == 0 ) )    #;    # // segment1 is just a point?
            seg2Pt = ( ( seg2dx == 0 ) and ( seg2dy == 0 ) )    #;    # // segment2 is just a point?
            # // both segments are points
            if seg1Pt and seg2Pt:
                if ( inSeg1Pt1.x != inSeg2Pt1.x ) or \
                     ( inSeg1Pt1.y != inSeg2Pt1.y ):
                     return []        # // they are distinct  points
                return [ inSeg1Pt1 ]                                         # // they are the same point

            # // segment#1  is a single point
            if seg1Pt:
                if not point_in_segment_2D_colin( inSeg2Pt1, inSeg2Pt2, inSeg1Pt1 ):
                    return []        # // but not in segment#2
                return [ inSeg1Pt1 ]

            # // segment#2  is a single point
            if seg2Pt:
                if not point_in_segment_2D_colin( inSeg1Pt1, inSeg1Pt2, inSeg2Pt1 ):
                    return []        # // but not in segment#1
                return [ inSeg2Pt1 ]

            # // they are collinear segments, which might overlap
            if seg1dx != 0:
                # // the segments are NOT on a vertical line
                if inSeg1Pt1.x < inSeg1Pt2.x:
                    seg1min = inSeg1Pt1; seg1minVal = inSeg1Pt1.x
                    seg1max = inSeg1Pt2; seg1maxVal = inSeg1Pt2.x

                else:
                    seg1min = inSeg1Pt2; seg1minVal = inSeg1Pt2.x
                    seg1max = inSeg1Pt1; seg1maxVal = inSeg1Pt1.x

                if inSeg2Pt1.x < inSeg2Pt2.x:
                    seg2min = inSeg2Pt1; seg2minVal = inSeg2Pt1.x
                    seg2max = inSeg2Pt2; seg2maxVal = inSeg2Pt2.x

                else:
                    seg2min = inSeg2Pt2; seg2minVal = inSeg2Pt2.x
                    seg2max = inSeg2Pt1; seg2maxVal = inSeg2Pt1.x

            else:
                # // the segments are on a vertical line
                if inSeg1Pt1.y < inSeg1Pt2.y:
                    seg1min = inSeg1Pt1; seg1minVal = inSeg1Pt1.y
                    seg1max = inSeg1Pt2; seg1maxVal = inSeg1Pt2.y

                else:
                    seg1min = inSeg1Pt2; seg1minVal = inSeg1Pt2.y
                    seg1max = inSeg1Pt1; seg1maxVal = inSeg1Pt1.y

                if inSeg2Pt1.y < inSeg2Pt2.y:
                    seg2min = inSeg2Pt1; seg2minVal = inSeg2Pt1.y
                    seg2max = inSeg2Pt2; seg2maxVal = inSeg2Pt2.y

                else:
                    seg2min = inSeg2Pt2; seg2minVal = inSeg2Pt2.y
                    seg2max = inSeg2Pt1; seg2maxVal = inSeg2Pt1.y

            if seg1minVal <= seg2minVal:
                if seg1maxVal <  seg2minVal:
                    return []
                if seg1maxVal == seg2minVal:
                    if inExcludeAdjacentSegs:
                        return []
                    return [ seg2min ]

                if seg1maxVal <= seg2maxVal:
                    return [ seg2min, seg1max ]
                return    [ seg2min, seg2max ]

            else:
                if seg1minVal >  seg2maxVal:
                    return []
                if seg1minVal == seg2maxVal:
                    if inExcludeAdjacentSegs:
                        return []
                    return [ seg1min ]

                if seg1maxVal <= seg2maxVal:
                    return [ seg1min, seg1max ]
                return    [ seg1min, seg2max ]


    def isPointInsideAngle( inVertex, inLegFromPt, inLegToPt, inOtherPt ):
        # // The order of legs is important

        # // translation of all points, so that Vertex is at (0,0)
        legFromPtX    = inLegFromPt.x - inVertex.x
        legFromPtY    = inLegFromPt.y - inVertex.y
        legToPtX    = inLegToPt.x    - inVertex.x
        legToPtY        = inLegToPt.y    - inVertex.y
        otherPtX    = inOtherPt.x    - inVertex.x
        otherPtY        = inOtherPt.y    - inVertex.y

        # // main angle >0: < 180 deg.; 0: 180 deg.; <0: > 180 deg.
        from2toAngle    = legFromPtX * legToPtY - legFromPtY * legToPtX
        from2otherAngle    = legFromPtX * otherPtY - legFromPtY * otherPtX

        if abs( from2toAngle ) > Number.EPSILON:
            # // angle != 180 deg.
            other2toAngle        = otherPtX * legToPtY - otherPtY * legToPtX
            # // console.log( "from2to: " + from2toAngle + ", from2other: " + from2otherAngle + ", other2to: " + other2toAngle )

            if from2toAngle > 0:
                # // main angle < 180 deg.
                return    ( ( from2otherAngle >= 0 ) and ( other2toAngle >= 0 ) )

            else:
                # // main angle > 180 deg.
                return    ( ( from2otherAngle >= 0 ) or ( other2toAngle >= 0 ) )

        else:
            # // angle == 180 deg.
            # // console.log( "from2to: 180 deg., from2other: " + from2otherAngle  )
            return    ( from2otherAngle > 0 )


    def removeHoles( contour, holes ):
        shape = contour[:]     # // work on this shape

        def isCutLineInsideAngles( inShapeIdx, inHoleIdx ):
            # // Check if hole point lies within angle around shape point
            lastShapeIdx = len(shape) - 1

            prevShapeIdx = inShapeIdx - 1
            if prevShapeIdx < 0:
                prevShapeIdx = lastShapeIdx

            nextShapeIdx = inShapeIdx + 1
            if nextShapeIdx > lastShapeIdx:
                nextShapeIdx = 0

            insideAngle = isPointInsideAngle( shape[ inShapeIdx ], shape[ prevShapeIdx ], shape[ nextShapeIdx ], hole[ inHoleIdx ] )
            if not insideAngle:
                # // console.log( "Vertex (Shape): " + inShapeIdx + ", Point: " + hole[inHoleIdx].x + "/" + hole[inHoleIdx].y )
                return    False

            # // Check if shape point lies within angle around hole point
            lastHoleIdx = len(hole) - 1

            prevHoleIdx = inHoleIdx - 1
            if prevHoleIdx < 0:
                prevHoleIdx = lastHoleIdx

            nextHoleIdx = inHoleIdx + 1
            if nextHoleIdx > lastHoleIdx:
                nextHoleIdx = 0

            insideAngle = isPointInsideAngle( hole[ inHoleIdx ], hole[ prevHoleIdx ], hole[ nextHoleIdx ], shape[ inShapeIdx ] )
            if not insideAngle:
                # // console.log( "Vertex (Hole): " + inHoleIdx + ", Point: " + shape[inShapeIdx].x + "/" + shape[inShapeIdx].y )
                return    False

            return    True

        def intersectsShapeEdge( inShapePt, inHolePt ):
            # // checks for intersections with shape edges
            for sIdx in range(len(shape)):
                nextIdx = sIdx + 1; nextIdx %= len(shape)
                intersection = intersect_segments_2D( inShapePt, inHolePt, shape[ sIdx ], shape[ nextIdx ], True )
                if len(intersection) > 0:
                    return    True

            return    False

        indepHoles = []

        def intersectsHoleEdge( inShapePt, inHolePt ):
            # // checks for intersections with hole edges
            for ihIdx in range(len(indepHoles)):
                chkHole = holes[ indepHoles[ ihIdx ] ]
                for hIdx in range(len(chkHole)):
                    nextIdx = hIdx + 1; nextIdx %= len(chkHole)
                    intersection = intersect_segments_2D( inShapePt, inHolePt, chkHole[ hIdx ], chkHole[ nextIdx ], True )
                    if len(intersection) > 0:
                        return    True

            return    False

        failedCuts = []

        for h in range(len(holes)):
            indepHoles.append( h )

        minShapeIndex = 0
        counter = len(indepHoles) * 2
        while len(indepHoles) > 0:
            counter -= 1
            if counter < 0:
                raise RuntimeError( 'THREE.ShapeUtils: Infinite Loop! Holes left:" + indepHoles.length + ", Probably Hole outside Shape!' )

            # // search for shape-vertex and hole-vertex,
            # // which can be connected without intersections
            for shapeIndex in range(minShapeIndex, len(shape)):
                shapePt = shape[ shapeIndex ]
                holeIndex    = - 1

                # // search for hole which can be reached without intersections
                for h in range(len(indepHoles)):
                    holeIdx = indepHoles[ h ]

                    # // prevent multiple checks
                    cutKey = "%f:%f:%d" % (shapePt.x, shapePt.y, holeIdx)
                    if cutKey in failedCuts:
                        continue

                    hole = holes[ holeIdx ]
                    for h2 in range(len(hole)):
                        holePt = hole[ h2 ]
                        if not isCutLineInsideAngles( shapeIndex, h2 ):
                            continue
                        if intersectsShapeEdge( shapePt, holePt ):
                            continue
                        if intersectsHoleEdge( shapePt, holePt ):
                            continue

                        holeIndex = h2
                        del indepHoles[h]

                        tmpShape1 = shape[0:shapeIndex + 1]
                        tmpShape2 = shape[shapeIndex:]
                        tmpHole1 = hole[holeIndex:]
                        tmpHole2 = hole[0:holeIndex + 1]

                        shape = tmpShape1 + tmpHole1 + tmpHole2 + tmpShape2

                        minShapeIndex = shapeIndex

                        # // Debug only, to show the selected cuts
                        # // glob_CutLines.push( [ shapePt, holePt ] )

                        break

                    if holeIndex >= 0:
                        break        # // hole-vertex found

                    failedCuts[ cutKey ] = True            # // remember failure

                if holeIndex >= 0:
                    break        # // hole-vertex found

        return shape             # /* shape with no holes */

    allPointsMap = {}

    # // To maintain reference to old shape, one must match coordinates, or offset the indices from original arrays. It's probably easier to do the first.

    allpoints = contour[:]

    for h in range(len(holes)):
        allpoints.extend(holes[h])

    # //console.log( "allpoints",allpoints, allpoints.length )

    # // prepare all points map

    for i in range(len(allpoints)):
        key = "%f:%f" % (allpoints[ i ].x, allpoints[ i ].y)

        if key in allPointsMap:
            print( 'THREE.ShapeUtils: Duplicate point', key, i )

        allPointsMap[ key ] = i

    # // remove holes by cutting paths to holes and adding them to the shape
    shapeWithoutHoles = removeHoles( contour, holes )

    triangles = triangulate( shapeWithoutHoles, False )     # // True returns indices for points of spooled shape
    # //console.log( "triangles",triangles, triangles.length )

    # // check all face vertices against all points map

    for i in range(len(triangles)):
        face = triangles[ i ]

        for f in range(3):
            key = "%f:%f" % (face[ f ].x, face[ f ].y)

            index = allPointsMap[ key ]

            if index is not None:
                face[ f ] = index

    return triangles[:]


def isClockWise( pts ):
    return area( pts ) < 0
