"""
/**
 * @author WestLangley / http://github.com/WestLangley
 *
 * parameters = {
 *
 *  referencePosition: <float>,
 *  nearDistance: <float>,
 *  farDistance: <float>,
 *
 *  skinning: <bool>,
 *  morphTargets: <bool>,
 *
 *  map: THREE.Texture( <Image> ),
 *
 *  alphaMap: THREE.Texture( <Image> ),
 *
 *  displacementMap: THREE.Texture( <Image> ),
 *  displacementScale: <float>,
 *  displacementBias: <float>
 *
 * }
 */
"""
from THREE.Material import *
from THREE.Vector3 import *


class MeshDistanceMaterial(Material):
    isMeshDistanceMaterial = True
    
    def __init__(self, parameters=None ):
        super().__init__()
        self.set_class(isMeshDistanceMaterial)

        self.type = 'MeshDistanceMaterial'

        self.referencePosition = Vector3()
        self.nearDistance = 1
        self.farDistance = 1000

        self.skinning = False
        self.morphTargets = False

        self.map = None

        self.alphaMap = None

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.fog = False
        self.lights = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.referencePosition.copy( source.referencePosition )
        self.nearDistance = source.nearDistance
        self.farDistance = source.farDistance

        self.skinning = source.skinning
        self.morphTargets = source.morphTargets

        self.map = source.map

        self.alphaMap = source.alphaMap

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        return self
