"""
/**
 * @author timothypratley / https://github.com/timothypratley
 * @author Mugen87 / https://github.com/Mugen87
 */
"""
from THREE.Geometry import *
from THREE.PolyhedronBufferGeometry import *


# // TetrahedronGeometry

class TetrahedronGeometry(Geometry):
    def __init__(self, radius, detail ):
        super().__init__(  )

        self.type = 'TetrahedronGeometry'

        self.parameters = {
            'radius': radius,
            'detail': detail
        }

        self.fromBufferGeometry( TetrahedronBufferGeometry( radius, detail ) )
        self.mergeVertices()


# // TetrahedronBufferGeometry

class TetrahedronBufferGeometry(PolyhedronBufferGeometry):
    def __init__(self, radius, detail ):
        vertices = [
            1,  1,  1,   - 1, - 1,  1,   - 1,  1, - 1,    1, - 1, - 1
        ]

        indices = [
            2,  1,  0,    0,  3,  2,    1,  3,  0,    2,  3,  1
        ]

        super().__init__( vertices, indices, radius, detail )

        self.type = 'TetrahedronBufferGeometry'

        self.parameters = {
            'radius': radius,
            'detail': detail
        }
