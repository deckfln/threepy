"""
/**
 * @author WestLangley / http://github.com/WestLangley
 *
 * parameters = {
 *  reflectivity: <float>
 * }
 */
"""
from THREE.MeshStandardMaterial import *


class MeshPhysicalMaterial(MeshStandardMaterial):
    isMeshPhysicalMaterial = True
    
    def __init__(self, parameters=None ):
        super().__init__()

        self.defines = { 'PHYSICAL': '' }

        self.type = 'MeshPhysicalMaterial'
        
        self.reflectivity = 0.5    # // maps to F0 = 0.04

        self.clearCoat = 0.0
        self.clearCoatRoughness = 0.0

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.defines = { 'PHYSICAL': '' }
        self.reflectivity = source.reflectivity

        self.clearCoat = source.clearCoat
        self.clearCoatRoughness = source.clearCoatRoughness

        return self
