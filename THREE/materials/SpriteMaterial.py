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
from THREE.materials.Material import *
from THREE.math.Color import *


class SpriteMaterial(Material):
    isSpriteMaterial = True
    
    def __init__(self, parameters=None):
        super().__init__()

        self.type = 'SpriteMaterial'

        self.color = Color(0xffffff)
        self.map = None

        self.rotation = 0

        self.lights = False
        self.transparent = True

        self.setValues(parameters)

    def copy(self, source):
        super().copy(source)

        self.color.copy(source.color)
        self.map = source.map

        self.rotation = source.rotation

        return self
