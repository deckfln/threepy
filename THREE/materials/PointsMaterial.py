"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  opacity: <float>,
 *  map: new THREE.Texture( <Image> ),
 *
 *  size: <float>,
 *  sizeAttenuation: <bool>
 *
 *  morphTargets: <bool>
 * }
 */
"""
from THREE.materials.Material import *
from THREE.math.Color import *


class PointsMaterial(Material):
    isPointsMaterial = True
    
    def __init__(self, parameters ):
        super().__init__()

        self.type = 'PointsMaterial'

        self.color = Color( 0xffffff )

        self.map = None

        self.size = 1
        self.sizeAttenuation = True

        self.lights = False
        self.morphTargets = False
        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )

        self.map = source.map

        self.size = source.size
        self.sizeAttenuation = source.sizeAttenuation

        self.morphTargets = source.morphTargets

        return self
