"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 * @author Mugen87 / https://github.com/Mugen87
 * @author hughes
 */
"""
from THREE.core.Geometry import *
from THREE.core.BufferGeometry import *


# // CircleGeometry


class CircleGeometry(Geometry):
    def __init__(self, radius, segments, thetaStart, thetaLength ):
        super().__init__(  )

        self.type = 'CircleGeometry'

        self.parameters = {
            'radius': radius,
            'segments': segments,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        self.fromBufferGeometry( CircleBufferGeometry( radius, segments, thetaStart, thetaLength ) )
        self.mergeVertices()


# // CircleBufferGeometry

class CircleBufferGeometry(BufferGeometry):
    def __init__(self, radius=50, segments=8, thetaStart=0, thetaLength=math.pi*2 ):
        super().__init__(  )

        self.type = 'CircleBufferGeometry'

        self.parameters = {
            'radius': radius,
            'segments': segments,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }


        # // buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # // helper variables

        vertex = Vector3()
        uv = Vector2()

        # // center point

        vertices.extend([ 0, 0, 0 ])
        normals.extend([ 0, 0, 1 ])
        uvs.extend([ 0.5, 0.5 ])

        i = 3
        for s in range(segments+1):
            segment = thetaStart + s / segments * thetaLength

            # // vertex

            vertex.x = radius * math.cos( segment )
            vertex.y = radius * math.sin( segment )

            vertices.extend([ vertex.x, vertex.y, vertex.z ])

            # // normal

            normals.extend([ 0, 0, 1 ])

            # // uvs

            uv.x = ( vertices[ i ] / radius + 1 ) / 2
            uv.y = ( vertices[ i + 1 ] / radius + 1 ) / 2

            uvs.extend([ uv.x, uv.y ])

            i += 3

        # // indices

        for i in range(1, segments+1):
            indices.extend([ i, i + 1, 0 ])

        # // build geometry

        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )
