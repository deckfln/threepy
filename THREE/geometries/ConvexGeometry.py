"""
/**
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""
from THREE.core.Geometry import *
from THREE.core.BufferGeometry import *
from examples.js.QuickHull import *


#    # // ConvexGeometry

class ConvexGeometry(Geometry):
    def __init__(self, points ):
        super().__init__()
        self.type = 'ConvexGeometry'

        self.fromBufferGeometry( ConvexBufferGeometry( points ) )
        self.mergeVertices()


# // ConvexBufferGeometry

class ConvexBufferGeometry(BufferGeometry):
    def __init__(self, points ):
        super().__init__()

        self.type = 'ConvexBufferGeometry'

        # // buffers

        vertices = []
        normals = []

        # // execute QuickHull

        if QuickHull is None:
            raise RuntimeError( 'THREE.ConvexBufferGeometry: ConvexBufferGeometry relies on THREE.QuickHull' )

        quickHull = QuickHull().setFromPoints( points )

        # // generate vertices and normals

        faces = quickHull.faces

        for i in range(len(faces)):
            face = faces[ i ]
            edge = face.edge

            # // we move along a doubly-connected edge list to access all face points (see HalfEdge docs)

            flag = True
            while flag:
                point = edge.head().point

                vertices.extend([ point.x, point.y, point.z ])
                normals.extend([ face.normal.x, face.normal.y, face.normal.z ])

                edge = edge.next
                flag = (edge != face.edge)

            # // build geometry

            self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
            self.addAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
