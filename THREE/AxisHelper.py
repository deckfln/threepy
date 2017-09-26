"""
/**
 * @author sroucheray / http://sroucheray.org/
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.LineSegments import *


class AxisHelper(LineSegments):
    def __init__(self, size=1 ):
        vertices = [
            0, 0, 0,  size, 0, 0,
            0, 0, 0,  0, size, 0,
            0, 0, 0,  0, 0, size
            ]

        colors = [
            1, 0, 0,  1, 0.6, 0,
            0, 1, 0,  0.6, 1, 0,
            0, 0, 1,  0, 0.6, 1
            ]

        geometry = BufferGeometry()
        geometry.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.addAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': VertexColors } )

        super().__init__( geometry, material )
