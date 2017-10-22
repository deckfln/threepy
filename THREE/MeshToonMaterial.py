"""
/**
 * @author takahirox / http://github.com/takahirox
 *
 * parameters = {
 *  gradientMap: new THREE.Texture( <Image> )
 * }
 */
"""
from THREE.MeshPhongMaterial import *


class MeshToonMaterial(MeshPhongMaterial):
    isMeshToonMaterial = True
    
    def __init__(self, parameters=None ):
        super().__init__()
        self.set_class(isMeshToonMaterial)

        self.defines = { 'TOON': '' }

        self.type = 'MeshToonMaterial'

        self.gradientMap = None

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.gradientMap = source.gradientMap

        return self
