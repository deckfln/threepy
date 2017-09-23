"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
from THREE.ShaderMaterial import *


class RawShaderMaterial(ShaderMaterial):
    isRawShaderMaterial = True

    def __init__(self,  parameters ):
        super().__init__(parameters )
        self.type = 'RawShaderMaterial'
