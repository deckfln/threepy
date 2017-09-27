"""
/**
 * @author astrodud / http:# //astrodud.isgreat.org/
 * @author zz85 / https:# //github.com/zz85
 * @author bhouston / http:# //clara.io
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""
from THREE.Geometry import *
from THREE.BufferGeometry import *
import THREE._Math as _Math


# // LatheGeometry

class LatheGeometry(Geometry):
    def __init__(self, points,segments=12, phiStart=0, phiLength=math.pi*2 ):
        super().__init__(  )

        self.type = 'LatheGeometry'

        self.parameters = {
            'points': points,
            'segments': segments,
            'phiStart': phiStart,
            'phiLength': phiLength
        }

        self.fromBufferGeometry( LatheBufferGeometry( points, segments, phiStart, phiLength ) )
        self.mergeVertices()


# // LatheBufferGeometry

class LatheBufferGeometry(BufferGeometry):
    def __init__(self, points, segments=12, phiStart=0, phiLength=math.pi*2 ):
        super().__init__(  )

        self.type = 'LatheBufferGeometry'

        self.parameters = {
            'points': points,
            'segments': segments,
            'phiStart': phiStart,
            'phiLength': phiLength
        }


        # // clamp phiLength so it's in range of [ 0, 2PI ]

        phiLength = _Math.clamp( phiLength, 0, math.pi * 2 )

        # // buffers

        indices = []
        vertices = []
        uvs = []

        # // helper variables

        inverseSegments = 1.0 / segments
        vertex = Vector3()
        uv = Vector2()

        # // generate vertices and uvs

        for i in range(segments+1):
            phi = phiStart + i * inverseSegments * phiLength

            sin = math.sin( phi )
            cos = math.cos( phi )

            for j in range(len(points)):
                # // vertex

                vertex.x = points[ j ].x * sin
                vertex.y = points[ j ].y
                vertex.z = points[ j ].x * cos

                vertices.extend([ vertex.x, vertex.y, vertex.z ])

                # // uv

                uv.x = i / segments
                uv.y = j / ( len(points) - 1 )

                uvs.extend([ uv.x, uv.y ])

        # // indices

        for i in range(segments):
            for j in range(len(points) - 1 ):
                base = j + i * len(points)

                a = base
                b = base + len(points)
                c = base + len(points) + 1
                d = base + 1

                # // faces

                indices.extend([ a, b, d ])
                indices.extend([ b, c, d ])

        # // build geometry

        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )

        # // generate normals

        self.computeVertexNormals()

        # // if the geometry is closed, we need to average the normals along the seam.
        # // because the corresponding vertices are identical (but still have different UVs).

        if phiLength == math.pi * 2:
            normals = self.attributes.normal.array
            n1 = Vector3()
            n2 = Vector3()
            n = Vector3()

            # // self is the buffer offset for the last line of vertices

            base = segments * len(points) * 3

            j = 0
            for i in range(len(points)):
                # // select the normal of the vertex in the first line

                n1.x = normals[ j + 0 ]
                n1.y = normals[ j + 1 ]
                n1.z = normals[ j + 2 ]

                # // select the normal of the vertex in the last line

                n2.x = normals[ base + j + 0 ]
                n2.y = normals[ base + j + 1 ]
                n2.z = normals[ base + j + 2 ]

                # // average normals

                n.addVectors( n1, n2 ).normalize()

                # // assign the values to both normals

                normals[ j + 0 ] = normals[ base + j + 0 ] = n.x
                normals[ j + 1 ] = normals[ base + j + 1 ] = n.y
                normals[ j + 2 ] = normals[ base + j + 2 ] = n.z

                j += 3
