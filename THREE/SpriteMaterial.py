"""
/**
 * @author alteredq / http://alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  opacity: <float>,
 *  map: new THREE.Texture( <Image> ),
 *
 *    uvOffset: new THREE.Vector2(),
 *    uvScale: new THREE.Vector2()
 * }
 */
"""
from THREE.Material import *
from THREE.Color import *


class SpriteMaterial(Material):
    isSpriteMaterial = True
    
    def __init__(self, parameters ):
        super().__init__()

        self.type = 'SpriteMaterial'

        self.color = Color( 0xffffff )
        self.map = None

        self.rotation = 0

        self.fog = False
        self.lights = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )
        self.map = source.map

        self.rotation = source.rotation

        return self
