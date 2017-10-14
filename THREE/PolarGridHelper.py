"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author Mugen87 / http:# //github.com/Mugen87
 * @author Hectate / http:# //www.github.com/Hectate
 */
"""
from THREE.LineSegments import *


class PolarGridHelper(LineSegments):
    def __init__(self, radius=10, radials=16, circles=8, divisions=64, color1=0x444444, color2=0x888888 ):
        color1 = Color( color1 )
        color2 = Color( color2 )

        vertices = []
        colors = []

        # // create the radials

        for i in range(radials+1):
            v = ( i / radials ) * ( math.pi * 2 )

            x = math.sin( v ) * radius
            z = math.cos( v ) * radius

            vertices.extend([ 0, 0, 0 ])
            vertices.extend([ x, 0, z ])

            color = color1 if ( i & 1 ) else color2

            colors.extend([ color.r, color.g, color.b ])
            colors.extend([ color.r, color.g, color.b ])

        # // create the circles

        for i in range(circles+1):
            color = color1 if ( i & 1 ) else color2

            r = radius - ( radius / circles * i )

            for j in range(divisions):
                # // first vertex

                v = ( j / divisions ) * ( math.pi * 2 )

                x = math.sin( v ) * r
                z = math.cos( v ) * r

                vertices.extend([ x, 0, z ])
                colors.extend([ color.r, color.g, color.b ])

                # // second vertex

                v = ( ( j + 1 ) / divisions ) * ( math.pi * 2 )

                x = math.sin( v ) * r
                z = math.cos( v ) * r

                vertices.extend([ x, 0, z ])
                colors.extend([ color.r, color.g, color.b ])

        geometry = BufferGeometry()
        geometry.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.addAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        material = LineBasicMaterial( { 'vertexColors': VertexColors } )

        super().__init__( geometry, material )
