"""
/**
 * @author mrdoob / http://mrdoob.com/
 *
 * parameters = {
 *  color: <THREE.Color>,
 *  opacity: <float>
 * }
 */
"""
from THREE.Material import *
from THREE.Color import *


class ShadowMaterial(Material):
    isShadowMaterial = True
    
    def __init__(self, parameters ):
        super().__init__()
        self.set_class(isShadowMaterial)

        self.type = 'ShadowMaterial'

        self.color = Color( 0x000000 )
        self.opacity = 1.0

        self.lights = True
        self.transparent = True

        self.setValues( parameters )
