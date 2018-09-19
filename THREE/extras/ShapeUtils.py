"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 */
"""
from THREE.Constants import *
import THREE.extras.Earcut as Earcut

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


def triangulateShape( contour, holes ):
    vertices = []   # flat array of vertices like [ x0,y0, x1,y1, x2,y2, ... ]
    holeIndices = []    # array of hole indices
    faces = []  # final array of vertex indices like [ [ a,b,d ], [ b,c,d ] ]

    removeDupEndPts( contour )
    addContour( vertices, contour )

    #

    holeIndex = len(contour)

    for hole in holes:
        removeDupEndPts(hole)

    for hole in holes:
        holeIndices.append( holeIndex )
        holeIndex += len(hole)
        addContour( vertices, hole )

    #

    triangles = Earcut.triangulate( vertices, holeIndices )

    #

    for i in range(0, len(triangles), 3):
        faces.append( triangles[i: i + 3] )

    return faces


def removeDupEndPts( points ):
    l = len(points)

    if l > 2 and points[ l - 1 ].equals( points[ 0 ] ):
        points.pop()


def addContour( vertices, contour ):
    for c in contour:
        vertices.append( c.x )
        vertices.append( c.y )
