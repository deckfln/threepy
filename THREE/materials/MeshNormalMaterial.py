"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author WestLangley / http://github.com/WestLangley
 *
 * parameters = {
 *  opacity: <float>,
 *
 *  bumpMap: new THREE.Texture( <Image> ),
 *  bumpScale: <float>,
 *
 *  normalMap: new THREE.Texture( <Image> ),
 *  normalScale: <Vector2>,
 *
 *  displacementMap: new THREE.Texture( <Image> ),
 *  displacementScale: <float>,
 *  displacementBias: <float>,
 *
 *  wireframe: <boolean>,
 *  wireframeLinewidth: <float>
 *
 *  skinning: <bool>,
 *  morphTargets: <bool>,
 *  morphNormals: <bool>
 * }
 */
"""
from THREE.Constants import *
from THREE.materials.Material import *


class MeshNormalMaterial(Material):
    isMeshNormalMaterial = True
    
    def __init__(self, parameters=None ):
        super().__init__( )
        self.set_class(isMeshNormalMaterial)

        self.type = 'MeshNormalMaterial'

        self.bumpMap = None
        self.bumpScale = 1

        self.normalMap = None
        self.normalMapType = TangentSpaceNormalMap
        self.normalScale = Vector2( 1, 1 )

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.wireframe = False
        self.wireframeLinewidth = 1

        self.fog = False
        self.lights = False

        self.skinning = False
        self.morphTargets = False
        self.morphNormals = False

        self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.bumpMap = source.bumpMap
        self.bumpScale = source.bumpScale

        self.normalMap = source.normalMap
        self.normalMapType = source.normalMapType
        self.normalScale.copy( source.normalScale )

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth

        self.skinning = source.skinning
        self.morphTargets = source.morphTargets
        self.morphNormals = source.morphNormals

        return self
