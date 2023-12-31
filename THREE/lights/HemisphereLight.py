"""
***
 * @author alteredq / http://alteredqualia.com/
 */
"""
from THREE.lights.Light import *


class HemisphereLight(Light):
    isHemisphereLight = True
    
    def __init__(self, skyColor, groundColor, intensity=1 ):
            super().__init__(skyColor, intensity )

            self.type = 'HemisphereLight'
            self.set_class(isHemisphereLight)

            self.castShadow = None

            self.position.copy( Object3D.DefaultUp )
            self.updateMatrix()

            self.groundColor = Color( groundColor )

    def copy(self, source ):
        super().copy( source )

        self.groundColor.copy( source.groundColor )

        return self
