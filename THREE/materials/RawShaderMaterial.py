"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
from THREE.materials.ShaderMaterial import *


class RawShaderMaterial(ShaderMaterial):
    isRawShaderMaterial = True

    def __init__(self,  parameters ):
        super().__init__(parameters )

        self.set_class(isRawShaderMaterial)

        self.type = 'RawShaderMaterial'
