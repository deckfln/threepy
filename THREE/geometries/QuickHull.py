"""
/**
 * @author Mugen87 / https:# //github.com/Mugen87
 *
 * Ported from: https:# //github.com/maurizzzio/quickhull3d/ by Mauricio Poppe (https:# //github.com/maurizzzio)
 *
 */
"""
import numpy

from THREE.math.Vector3 import *
from THREE.Constants import *


Visible = 0
Deleted = 1


class QuickHull:
    def __init__(self):
        self.tolerance = - 1

        self.faces = []     # // the generated faces of the convex hull
        self.newFaces = []     # // self array holds the faces that are generated within a single iteration

        # // the vertex lists work as follows:
        # //
        # // let 'a' and 'b' be 'Face' instances
        # // let 'v' be points wrapped as instance of 'Vertex'
        # //
        # //     [v, v, ..., v, v, v, ...]
        # //      ^             ^
        # //      |             |
        # //  a.outside     b.outside
        # //
        self.assigned = VertexList()
        self.unassigned = VertexList()

        self.vertices = []    # // vertices of the hull (internal representation of given geometry data)

    def setFromPoints(self, points ):

        if not isinstance(points, list) and not isinstance(points, numpy.ndarray):
            raise RuntimeError( 'THREE.QuickHull: Points parameter is not an array.' )

        if len(points) < 4:
            raise RuntimeError( 'THREE.QuickHull: The algorithm needs at least four points.' )

        self.makeEmpty()

        for point in points:
            self.vertices.append( VertexNode( point ) )

        self.compute()

        return self

    def setFromObject(self, object ):
        points = []

        object.updateMatrixWorld( True )

        def _traverse(node):
            geometry = node.geometry

            if geometry is not None:
                if geometry.my_class(isGeometry):
                    vertices = geometry.vertices

                    for i in range(len(vertices)):
                        point = vertices[ i ].clone()
                        point.applyMatrix4( node.matrixWorld )

                        points.append( point )

                elif geometry.my_class(isBufferGeometry):
                    attribute = geometry.attributes.position
                    if attribute is not None:
                        for i in range(attribute.count):
                            point = THREE.Vector3()
                            point.fromBufferAttribute( attribute, i ).applyMatrix4( node.matrixWorld )
                            points.append( point )

        object.traverse( _traverse )

        return self.setFromPoints( points )

    def makeEmpty(self):
        self.faces = []
        self.vertices = []

        return self

    # // Adds a vertex to the 'assigned' list of vertices and assigns it to the given face

    def addVertexToFace(self, vertex, face ):
        vertex.face = face

        if face.outside is None:
            self.assigned.append( vertex )
        else:
            self.assigned.insertBefore( face.outside, vertex )

        face.outside = vertex

        return self

    # // Removes a vertex from the 'assigned' list of vertices and from the given face

    def removeVertexFromFace(self, vertex, face ):
        if vertex == face.outside:
            # // fix face.outside link
            if vertex.next is not None and vertex.next.face == face:
                # // face has at least 2 outside vertices, move the 'outside' reference
                face.outside = vertex.next
            else:
                # // vertex was the only outside vertex that face had
                face.outside = None

        self.assigned.remove( vertex )

        return self

    # // Removes all the visible vertices that a given face is able to see which are stored in the 'assigned' vertext list

    def removeAllVerticesFromFace(self, face ):
        if face.outside is not None:
            # // reference to the first and last vertex of self face
            start = face.outside
            end = face.outside

            while end.next is not None and end.next.face == face:
                end = end.next

            self.assigned.removeSubList( start, end )

            # // fix references

            start.prev = end.next = None
            face.outside = None

            return start

    # // Removes all the visible vertices that 'face' is able to see

    def deleteFaceVertices(self, face, absorbingFace=None ):
        faceVertices = self.removeAllVerticesFromFace( face )

        if faceVertices is not None:
            if absorbingFace is None:
                # // mark the vertices to be reassigned to some other face
                self.unassigned.appendChain( faceVertices )
            else:
                # // if there's an absorbing face try to assign as many vertices as possible to it
                vertex = faceVertices

                flag = True
                while flag:
                    # // we need to buffer the subsequent vertex at self point because the 'vertex.next' reference
                    # // will be changed by upcoming method calls

                    nextVertex = vertex.next

                    distance = absorbingFace.distanceToPoint( vertex.point )

                    # // check if 'vertex' is able to see 'absorbingFace'

                    if distance > self.tolerance:
                        self.addVertexToFace( vertex, absorbingFace )
                    else:
                        self.unassigned.append( vertex )

                    # // now assign next vertex

                    vertex = nextVertex
                    flag = vertex

        return self

    # // Reassigns as many vertices as possible from the unassigned list to the faces

    def resolveUnassignedPoints(self, newFaces ):
        if self.unassigned.isEmpty() == False:
            vertex = self.unassigned.first()
            flag = True

            while flag:
                # // buffer 'next' reference, see .deleteFaceVertices()

                nextVertex = vertex.next

                maxDistance = self.tolerance

                maxFace = None

                for i in range(len(newFaces)):

                    face = newFaces[ i ]

                    if face.mark == Visible:
                        distance = face.distanceToPoint( vertex.point )

                        if distance > maxDistance:
                            maxDistance = distance
                            maxFace = face

                        if maxDistance > 1000 * self.tolerance:
                            break

                # // 'maxFace' can be None e.g. if there are identical vertices

                if maxFace is not None:
                    self.addVertexToFace( vertex, maxFace )

                flag = vertex = nextVertex

        return self

    # // Computes the extremes of a simplex which will be the initial hull

    def computeExtremes(self):
        mi = THREE.Vector3()
        ma = THREE.Vector3()

        # // initially assume that the first vertex is the min/max

        minVertices = [self.vertices[ 0 ] for i in range(3)]
        maxVertices = [self.vertices[ 0 ] for i in range(3)]

        mi.copy( self.vertices[ 0 ].point )
        ma.copy( self.vertices[ 0 ].point )

        # // compute the min/max vertex on all six directions

        for i in range(len(self.vertices)):
            vertex = self.vertices[ i ]
            point = vertex.point

            # // update the min coordinates

            for j in range(3):
                if point.getComponent( j ) < mi.getComponent( j ):
                    mi.setComponent( j, point.getComponent( j ) )
                    minVertices[ j ] = vertex

            # // update the max coordinates

            for j in range(3):
                if point.getComponent( j ) > ma.getComponent( j ):
                    ma.setComponent( j, point.getComponent( j ) )
                    maxVertices[ j ] = vertex

        # // use min/max vectors to compute an optimal epsilon

        self.tolerance = 3 * Number.EPSILON * (
            max( abs( mi.x ), abs( ma.x ) ) +
            max( abs( mi.y ), abs( ma.y ) ) +
            max( abs( mi.z ), abs( ma.z ) )
        )

        return { 'min': minVertices, 'max': maxVertices }

    # // Computes the initial simplex assigning to its faces all the points
    # // that are candidates to form part of the hull

    def computeInitialHull(self):
        line3 = THREE.Line3()
        plane = THREE.Plane()
        closestPoint = THREE.Vector3()

        vertices = self.vertices
        extremes = self.computeExtremes()
        min = extremes['min']
        max = extremes['max']

        # // 1. Find the two vertices 'v0' and 'v1' with the greatest 1d separation
        # // (max.x - min.x)
        # // (max.y - min.y)
        # // (max.z - min.z)

        maxDistance = 0
        index = 0

        for i in range(3):
            distance = max[ i ].point.getComponent( i ) - min[ i ].point.getComponent( i )

            if distance > maxDistance:
                maxDistance = distance
                index = i

        v0 = min[ index ]
        v1 = max[ index ]

        # // 2. The next vertex 'v2' is the one farthest to the line formed by 'v0' and 'v1'

        maxDistance = 0
        line3.set( v0.point, v1.point )

        for i in range(len(self.vertices)):

            vertex = vertices[ i ]

            if vertex != v0 and vertex != v1:
                line3.closestPointToPoint( vertex.point, True, closestPoint )

                distance = closestPoint.distanceToSquared( vertex.point )

                if distance > maxDistance:
                    maxDistance = distance
                    v2 = vertex

        # // 3. The next vertex 'v3' is the one farthest to the plane 'v0', 'v1', 'v2'

        maxDistance = 0
        plane.setFromCoplanarPoints( v0.point, v1.point, v2.point )

        for i in range(len(self.vertices)):
            vertex = vertices[ i ]

            if vertex != v0 and vertex != v1 and vertex != v2:
                distance = abs( plane.distanceToPoint( vertex.point ) )

                if distance > maxDistance:
                    maxDistance = distance
                    v3 = vertex

        faces = []

        if plane.distanceToPoint( v3.point ) < 0:
            # // the face is not able to see the point so 'plane.normal' is pointing outside the tetrahedron

            faces.extend([
                Face.create( v0, v1, v2 ),
                Face.create( v3, v1, v0 ),
                Face.create( v3, v2, v1 ),
                Face.create( v3, v0, v2 )
            ])

            # // set the twin edge

            for i in range(3):
                j = ( i + 1 ) % 3

                # // join face[ i ] i > 0, with the first face

                faces[ i + 1 ].getEdge( 2 ).setTwin( faces[ 0 ].getEdge( j ) )

                # // join face[ i ] with face[ i + 1 ], 1 <= i <= 3

                faces[ i + 1 ].getEdge( 1 ).setTwin( faces[ j + 1 ].getEdge( 0 ) )

        else:
            # // the face is able to see the point so 'plane.normal' is pointing inside the tetrahedron

            faces.extend([
                Face.create( v0, v2, v1 ),
                Face.create( v3, v0, v1 ),
                Face.create( v3, v1, v2 ),
                Face.create( v3, v2, v0 )
            ])

            # // set the twin edge

            for i in range(3):
                j = ( i + 1 ) % 3

                # // join face[ i ] i > 0, with the first face

                faces[ i + 1 ].getEdge( 2 ).setTwin( faces[ 0 ].getEdge( ( 3 - i ) % 3 ) )

                # // join face[ i ] with face[ i + 1 ]

                faces[ i + 1 ].getEdge( 0 ).setTwin( faces[ j + 1 ].getEdge( 1 ) )

        # // the initial hull is the tetrahedron

        for i in range(4):
            self.faces.append( faces[ i ] )

        # // initial assignment of vertices to the faces of the tetrahedron

        for i in range(len(vertices)):
            vertex = vertices[i]

            if vertex != v0 and vertex != v1 and vertex != v2 and vertex != v3:
                maxDistance = self.tolerance
                maxFace = None

                for j in range(4):
                    distance = self.faces[ j ].distanceToPoint( vertex.point )

                    if distance > maxDistance:
                        maxDistance = distance
                        maxFace = self.faces[ j ]

                if maxFace is not None:
                    self.addVertexToFace( vertex, maxFace )

        return self

    # // Removes inactive faces

    def reindexFaces(self):

        activeFaces = []

        for i in range(len(self.faces)):

            face = self.faces[ i ]

            if face.mark == Visible:
                activeFaces.append( face )

        self.faces = activeFaces

        return self

    # // Finds the next vertex to create faces with the current hull

    def nextVertexToAdd(self):
        # // if the 'assigned' list of vertices is empty, no vertices are left. return with 'undefined'

        if self.assigned.isEmpty() == False:
            maxDistance = 0

            # // grap the first available face and start with the first visible vertex of that face

            eyeFace = self.assigned.first().face
            vertex = eyeFace.outside

            # // now calculate the farthest vertex that face can see

            flag = True
            while flag:
                distance = eyeFace.distanceToPoint( vertex.point )

                if distance > maxDistance:
                    maxDistance = distance
                    eyeVertex = vertex

                vertex = vertex.next
                flag = vertex is not None and vertex.face == eyeFace

            return eyeVertex

    # // Computes a chain of half edges in CCW order called the 'horizon'.
    # // For an edge to be part of the horizon it must join a face that can see
    # // 'eyePoint' and a face that cannot see 'eyePoint'.

    def computeHorizon(self, eyePoint, crossEdge, face, horizon ):

        # // moves face's vertices to the 'unassigned' vertex list

        self.deleteFaceVertices( face )

        face.mark = Deleted

        if crossEdge is None:
            edge = crossEdge = face.getEdge( 0 )

        else:
            # // start from the next edge since 'crossEdge' was already analyzed
            # // (actually 'crossEdge.twin' was the edge who called self method recursively)
            edge = crossEdge.next

        flag = True
        while flag:
            twinEdge = edge.twin
            oppositeFace = twinEdge.face

            if oppositeFace.mark == Visible:
                if oppositeFace.distanceToPoint( eyePoint ) > self.tolerance:
                    # // the opposite face can see the vertex, so proceed with next edge
                    self.computeHorizon( eyePoint, twinEdge, oppositeFace, horizon )

                else:
                    # // the opposite face can't see the vertex, so self edge is part of the horizon
                    horizon.append( edge )

            edge = edge.next
            flag = (edge != crossEdge)

        return self

    # // Creates a face with the vertices 'eyeVertex.point', 'horizonEdge.tail' and 'horizonEdge.head' in CCW order

    def addAdjoiningFace(self, eyeVertex, horizonEdge ):
        # // all the half edges are created in ccw order thus the face is always pointing outside the hull
        face = Face.create( eyeVertex, horizonEdge.tail(), horizonEdge.head() )

        self.faces.append( face )

        # // join face.getEdge( - 1 ) with the horizon's opposite edge face.getEdge( - 1 ) = face.getEdge( 2 )

        face.getEdge( - 1 ).setTwin( horizonEdge.twin )

        return face.getEdge( 0 )     # // the half edge whose vertex is the eyeVertex

    # //  Adds 'horizon.length' faces to the hull, each face will be linked with the
    # //  horizon opposite face and the face on the left/right

    def addNewFaces(self, eyeVertex, horizon ):
        self.newFaces = []

        firstSideEdge = None
        previousSideEdge = None

        for i in range(len(horizon)):
            horizonEdge = horizon[ i ]

            # // returns the right side edge

            sideEdge = self.addAdjoiningFace( eyeVertex, horizonEdge )

            if firstSideEdge is None:
                firstSideEdge = sideEdge
            else:
                # // joins face.getEdge( 1 ) with previousFace.getEdge( 0 )
                sideEdge.next.setTwin( previousSideEdge )

            self.newFaces.append( sideEdge.face )
            previousSideEdge = sideEdge

        # // perform final join of faces

        firstSideEdge.next.setTwin( previousSideEdge )

        return self

    # // Adds a vertex to the hull

    def addVertexToHull(self, eyeVertex ):
        horizon = []

        self.unassigned.clear()

        # // remove 'eyeVertex' from 'eyeVertex.face' so that it can't be added to the 'unassigned' vertex list

        self.removeVertexFromFace( eyeVertex, eyeVertex.face )

        self.computeHorizon( eyeVertex.point, None, eyeVertex.face, horizon )

        self.addNewFaces( eyeVertex, horizon )

        # // reassign 'unassigned' vertices to the faces

        self.resolveUnassignedPoints( self.newFaces )

        return    self

    def cleanup(self):
        self.assigned.clear()
        self.unassigned.clear()
        self.newFaces = []

        return self

    def compute(self):
        self.computeInitialHull()

        # // add all available vertices gradually to the hull
        vertex = self.nextVertexToAdd()
        while  vertex is not None:
            self.addVertexToHull( vertex )
            vertex = self.nextVertexToAdd()

        self.reindexFaces()
        self.cleanup()
        return self


# //

class Face:
    def __init__(self):
        self.normal = THREE.Vector3()
        self.midpoint = THREE.Vector3()
        self.area = 0

        self.constant = 0     # // signed distance from face to the origin
        self.outside = None     # // reference to a vertex in a vertex list self face can see
        self.mark = Visible
        self.edge = None

    def create(a, b, c ):
        face = Face()

        e0 = HalfEdge( a, face )
        e1 = HalfEdge( b, face )
        e2 = HalfEdge( c, face )

        # // join edges

        e0.next = e2.prev = e1
        e1.next = e0.prev = e2
        e2.next = e1.prev = e0

        # // main half edge reference

        face.edge = e0

        return face.compute()

    def getEdge(self, i ):
        edge = self.edge

        while i > 0:
            edge = edge.next
            i -= 1

        while i < 0:
            edge = edge.prev
            i += 1

        return edge

    def compute(self):
        triangle = THREE.Triangle()

        a = self.edge.tail()
        b = self.edge.head()
        c = self.edge.next.head()

        triangle.set( a.point, b.point, c.point )

        triangle.normal( self.normal )
        triangle.midpoint( self.midpoint )
        self.area = triangle.area()

        self.constant = self.normal.dot( self.midpoint )

        return self

    def distanceToPoint(self, point ):
        return self.normal.dot( point ) - self.constant

# // Entity for a Doubly-Connected Edge List (DCEL).

class HalfEdge:
    def __init__(self, vertex, face ):
        self.vertex = vertex
        self.prev = None
        self.next = None
        self.twin = None
        self.face = face

    def head(self):
        return self.vertex

    def tail(self):
        return self.prev.vertex if self.prev else None

    def length(self):
        head = self.head()
        tail = self.tail()

        if tail is not None:
            return tail.point.distanceTo( head.point )

        return - 1

    def lengthSquared(self):
        head = self.head()
        tail = self.tail()

        if tail is not None:
            return tail.point.distanceToSquared( head.point )

        return - 1

    def setTwin(self, edge ):
        self.twin = edge
        edge.twin = self

        return self

# // A vertex as a double linked list node.

class VertexNode:
    def __init__(self, point ):
        self.point = point
        self.prev = None
        self.next = None
        self.face = None     # // the face that is able to see self vertex

# // A double linked list that contains vertex nodes.

class VertexList:
    def __init__(self):
        self.head = None
        self.tail = None

    def first(self):
        return self.head

    def last(self):
        return self.tail

    def clear(self):
        self.head = self.tail = None

        return self

    # // Inserts a vertex before the target vertex

    def insertBefore(self, target, vertex ):
        vertex.prev = target.prev
        vertex.next = target

        if vertex.prev is None:
            self.head = vertex
        else:
            vertex.prev.next = vertex

        target.prev = vertex

        return self

    # // Inserts a vertex after the target vertex

    def insertAfter(self, target, vertex ):
        vertex.prev = target
        vertex.next = target.next

        if vertex.next is None:
            self.tail = vertex
        else:
            vertex.next.prev = vertex

        target.next = vertex

        return self

    # // Appends a vertex to the end of the linked list

    def append(self, vertex ):
        if self.head is None:
            self.head = vertex
        else:
            self.tail.next = vertex

        vertex.prev = self.tail
        vertex.next = None     # // the tail has no subsequent vertex

        self.tail = vertex

        return self

    # // Appends a chain of vertices where 'vertex' is the head.

    def appendChain(self, vertex ):
        if self.head is None:
            self.head = vertex
        else:
            self.tail.next = vertex

        vertex.prev = self.tail

        # // ensure that the 'tail' reference points to the last vertex of the chain

        while vertex.next is not None:
            vertex = vertex.next

        self.tail = vertex

        return self

    # // Removes a vertex from the linked list

    def remove(self, vertex ):
        if vertex.prev is None:
            self.head = vertex.next
        else:
            vertex.prev.next = vertex.next

        if vertex.next is None:
            self.tail = vertex.prev
        else:
            vertex.next.prev = vertex.prev

        return self

    # // Removes a list of vertices whose 'head' is 'a' and whose 'tail' is b

    def removeSubList(self, a, b ):
        if a.prev is None:
            self.head = b.next
        else:
            a.prev.next = b.next

        if b.next is None:
            self.tail = a.prev
        else:
            b.next.prev = a.prev

        return self

    def isEmpty(self):
        return self.head is None
