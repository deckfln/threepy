"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author benaadams / https:# //twitter.com/ben_a_adams
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""
from THREE.core.Geometry import *
from THREE.core.BufferGeometry import *


# // SphereGeometry

class SphereGeometry(Geometry):
    def __init__(self, radius=50, widthSegments=8, heightSegments=6, phiStart=0, phiLength=math.pi*2, thetaStart=0, thetaLength=math.pi ):
        super().__init__()

        self.type = 'SphereGeometry'

        self.parameters = {
            'radius': radius,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments,
            'phiStart': phiStart,
            'phiLength': phiLength,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        self.fromBufferGeometry( SphereBufferGeometry( radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength ) )
        self.mergeVertices()

# // SphereBufferGeometry


class SphereBufferGeometry(BufferGeometry):
    def __init__(self, radius=50, widthSegments=8, heightSegments=6, phiStart=0, phiLength=math.pi*2, thetaStart=0, thetaLength=math.pi ):
        super().__init__( )

        self.type = 'SphereBufferGeometry'

        self.parameters = {
            'radius': radius,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments,
            'phiStart': phiStart,
            'phiLength': phiLength,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        widthSegments = max( 3, math.floor( widthSegments )  )
        heightSegments = max( 2, math.floor( heightSegments )  )

        thetaEnd = thetaStart + thetaLength

        index = 0
        grid = []

        vertex = Vector3()
        normal = Vector3()

        # // buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # // generate vertices, normals and uvs

        for iy in range(heightSegments+1):
            verticesRow = []

            v = iy / heightSegments

            for ix in range(widthSegments+1):
                u = ix / widthSegments

                # // vertex

                vertex.np[0] = - radius * math.cos( phiStart + u * phiLength ) * math.sin( thetaStart + v * thetaLength )
                vertex.np[1] = radius * math.cos( thetaStart + v * thetaLength )
                vertex.np[2] = radius * math.sin( phiStart + u * phiLength ) * math.sin( thetaStart + v * thetaLength )

                vertices.extend([ vertex.np[0], vertex.np[1], vertex.np[2] ])

                # // normal

                normal.set( vertex.np[0], vertex.np[1], vertex.np[2] ).normalize()
                normals.extend([ normal.np[0], normal.np[1], normal.np[2] ])

                # // uv

                uvs.extend([ u, 1 - v ])

                verticesRow.append( index )
                index += 1

            grid.append( verticesRow )

        # // indices

        for iy in range(heightSegments):
            for ix in range(widthSegments):
                a = grid[ iy ][ ix + 1 ]
                b = grid[ iy ][ ix ]
                c = grid[ iy + 1 ][ ix ]
                d = grid[ iy + 1 ][ ix + 1 ]

                if iy != 0 or thetaStart > 0:
                    indices.extend([ a, b, d ])
                if iy != heightSegments - 1 or thetaEnd < math.pi:
                    indices.extend([ b, c, d ])

        # // build geometry

        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )
