"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author bhouston / https://clara.io
 * @author WestLangley / http://github.com/WestLangley
 *
 * parameters = {
 *
 *  opacity: <float>,
 *
 *  map: new THREE.Texture( <Image> ),
 *
 *  alphaMap: new THREE.Texture( <Image> ),
 *
 *  displacementMap: new THREE.Texture( <Image> ),
 *  displacementScale: <float>,
 *  displacementBias: <float>,
 *
 *  wireframe: <boolean>,
 *  wireframeLinewidth: <float>
 * }
 */
"""
from THREE.Material import *


class MeshDepthMaterial(Material):
    isMeshDepthMaterial = True
    
    def __init__(self, parameters ):
        super().__init__()

        self.type = 'MeshDepthMaterial'

        self.depthPacking = BasicDepthPacking

        self.skinning = False
        self.morphTargets = False

        self.map = None

        self.alphaMap = None

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.wireframe = False
        self.wireframeLinewidth = 1

        self.fog = False
        self.lights = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.depthPacking = source.depthPacking

        self.skinning = source.skinning
        self.morphTargets = source.morphTargets

        self.map = source.map

        self.alphaMap = source.alphaMap

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth

        return self
