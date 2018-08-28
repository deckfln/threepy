"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.LineSegments import *


class GridHelper(LineSegments):
    def __init__(self, size=10, divisions=10, color1=0x444444, color2=0x888888):
        center = divisions / 2
        step = size / divisions
        halfSize = size / 2
        color1 = Color(color1)
        color2 = Color(color2)

        vertices = []
        colors = [0 for i in range(divisions*12+12)]

        j = 0
        k = -halfSize
        for i in range(divisions+1):
            vertices.extend([- halfSize, 0, k, halfSize, 0, k])
            vertices.extend([k, 0, - halfSize, k, 0, halfSize])

            color = color1 if i == center else color2

            color.toArray(colors, j); j += 3
            color.toArray(colors, j); j += 3
            color.toArray(colors, j); j += 3
            color.toArray(colors, j); j += 3

            k += step

        geometry = BufferGeometry()
        geometry.addAttribute('position', Float32BufferAttribute(vertices, 3))
        geometry.addAttribute('color', Float32BufferAttribute(colors, 3))

        material = LineBasicMaterial({'vertexColors': VertexColors})

        super().__init__(geometry, material)
