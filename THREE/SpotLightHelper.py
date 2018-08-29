"""
 * @author alteredq / http://alteredqualia.com/
 * @author mrdoob / http://mrdoob.com/
 * @author WestLangley / http://github.com/WestLangley
"""
from THREE.core.Object3D import *


class SpotLightHelper(Object3D):
    def __init__(self, light, color ):
        super().__init__()

        self.light = light
        self.light.updateMatrixWorld()

        self.matrix = light.matrixWorld
        self.matrixAutoUpdate = False

        self.color = color

        geometry = BufferGeometry()

        positions = [
            0, 0, 0,   0,   0,   1,
            0, 0, 0,   1,   0,   1,
            0, 0, 0, - 1,   0,   1,
            0, 0, 0,   0,   1,   1,
            0, 0, 0,   0, - 1,   1
        ]

        j = 1
        l = 32
        for i in range(0, l):
            p1 = ( i / l ) * math.pi * 2
            p2 = ( j / l ) * math.pi * 2

            positions.append(
                math.cos( p1 ), math.sin( p1 ), 1,
                math.cos( p2 ), math.sin( p2 ), 1
            )

            j += 1

        geometry.addAttribute( 'position', Float32BufferAttribute( positions, 3 ) )

        material = LineBasicMaterial( { 'fog': False } )

        self.cone = LineSegments( geometry, material )
        self.add( self.cone )

        self.update()

    def dispose(self):
        self.cone.geometry.dispose()
        self.cone.material.dispose()

    def update(self):
        vector = Vector3()
        vector2 = Vector3()

        self.light.updateMatrixWorld()

        coneLength = self.light.distance if self.light.distance else 1000
        coneWidth = coneLength * math.tan( self.light.angle )

        self.cone.scale.set( coneWidth, coneWidth, coneLength )

        vector.setFromMatrixPosition( self.light.matrixWorld )
        vector2.setFromMatrixPosition( self.light.target.matrixWorld )

        self.cone.lookAt( vector2.sub( vector ) )

        if self.color:
            self.cone.material.color.set( self.color )
        else:
            self.cone.material.color.copy( self.light.color )
