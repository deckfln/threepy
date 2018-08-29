"""
/**
 * @author oosmoxiecode
 * @author mrdoob / http:# //mrdoob.com/
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""
from THREE.core.Geometry import *
from THREE.core.BufferGeometry import *


# // TorusGeometry

class TorusGeometry(Geometry):
    def __init__(self, radius=400, tube=40, radialSegments=8, tubularSegments=6, arc=math.pi ):
        super().__init__()

        self.type = 'TorusGeometry'

        self.parameters = {
            'radius': radius,
            'tube': tube,
            'radialSegments': radialSegments,
            'tubularSegments': tubularSegments,
            'arc': arc
        }

        self.fromBufferGeometry( TorusBufferGeometry( radius, tube, radialSegments, tubularSegments, arc ) )
        self.mergeVertices()


# // TorusBufferGeometry

class TorusBufferGeometry(BufferGeometry):
    def __init__(self, radius=400, tube=40, radialSegments=8, tubularSegments=6, arc=math.pi ):
        super().__init__()

        self.type = 'TorusBufferGeometry'

        self.parameters = {
            'radius': radius,
            'tube': tube,
            'radialSegments': radialSegments,
            'tubularSegments': tubularSegments,
            'arc': arc
        }

        radialSegments = int( radialSegments )
        tubularSegments = int( tubularSegments )

        # // buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # // helper variables

        center = Vector3()
        vertex = Vector3()
        normal = Vector3()

        # // generate vertices, normals and uvs

        for j in range(radialSegments+1):
            for i in range(tubularSegments+1):
                u = i / tubularSegments * arc
                v = j / radialSegments * math.pi * 2

                # // vertex

                vertex.np[0] = ( radius + tube * math.cos( v ) ) * math.cos( u )
                vertex.np[1] = ( radius + tube * math.cos( v ) ) * math.sin( u )
                vertex.np[2] = tube * math.sin( v )

                vertices.extend([ vertex.np[0], vertex.np[1], vertex.np[2] ])

                # // normal

                center.np[0] = radius * math.cos( u )
                center.np[1] = radius * math.sin( u )
                normal.subVectors( vertex, center ).normalize()

                normals.extend([ normal.np[0], normal.np[1], normal.np[2] ])

                # // uv

                uvs.append( i / tubularSegments )
                uvs.append( j / radialSegments )

        # // generate indices

        for j in range(1, radialSegments+1):
            for i in range(1, tubularSegments+1):
                # // indices

                a = ( tubularSegments + 1 ) * j + i - 1
                b = ( tubularSegments + 1 ) * ( j - 1 ) + i - 1
                c = ( tubularSegments + 1 ) * ( j - 1 ) + i
                d = ( tubularSegments + 1 ) * j + i

                # // faces

                indices.extend([ a, b, d ])
                indices.extend([ b, c, d ])

        # // build geometry

        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )
