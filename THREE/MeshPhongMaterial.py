"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 *
 * parameters = {
 *  color: <hex>,
 *  specular: <hex>,
 *  shininess: <float>,
 *  opacity: <float>,
 *
 *  map: THREE.Texture( <Image> ),
 *
 *  lightMap: THREE.Texture( <Image> ),
 *  lightMapIntensity: <float>
 *
 *  aoMap: THREE.Texture( <Image> ),
 *  aoMapIntensity: <float>
 *
 *  emissive: <hex>,
 *  emissiveIntensity: <float>
 *  emissiveMap: THREE.Texture( <Image> ),
 *
 *  bumpMap: THREE.Texture( <Image> ),
 *  bumpScale: <float>,
 *
 *  normalMap: THREE.Texture( <Image> ),
 *  normalScale: <Vector2>,
 *
 *  displacementMap: THREE.Texture( <Image> ),
 *  displacementScale: <float>,
 *  displacementBias: <float>,
 *
 *  specularMap: THREE.Texture( <Image> ),
 *
 *  alphaMap: THREE.Texture( <Image> ),
 *
 *  envMap: THREE.TextureCube( [posx, negx, posy, negy, posz, negz] ),
 *  combine: THREE.Multiply,
 *  reflectivity: <float>,
 *  refractionRatio: <float>,
 *
 *  wireframe: <boolean>,
 *  wireframeLinewidth: <float>,
 *
 *  skinning: <bool>,
 *  morphTargets: <bool>,
 *  morphNormals: <bool>
 * }
 */
"""
from THREE.Material import *
from THREE.Color import *
from THREE.Vector2 import *


class MeshPhongMaterial(Material):
    isMeshPhongMaterial = True
    
    def  __init__(self, parameters ):
        super().__init__()

        self.type = 'MeshPhongMaterial'

        self.color = Color( 0xffffff )    # // diffuse
        self.specular = Color( 0x111111 )
        self.shininess = 30

        self.map = None

        self.lightMap = None
        self.lightMapIntensity = 1.0

        self.aoMap = None
        self.aoMapIntensity = 1.0

        self.emissive = Color( 0x000000 )
        self.emissiveIntensity = 1.0
        self.emissiveMap = None

        self.bumpMap = None
        self.bumpScale = 1

        self.normalMap = None
        self.normalScale = Vector2( 1, 1 )

        self.displacementMap = None
        self.displacementScale = 1
        self.displacementBias = 0

        self.specularMap = None

        self.alphaMap = None

        self.envMap = None
        self.combine = MultiplyOperation
        self.reflectivity = 1
        self.refractionRatio = 0.98

        self.wireframe = False
        self.wireframeLinewidth = 1
        self.wireframeLinecap = 'round'
        self.wireframeLinejoin = 'round'

        self.skinning = False
        self.morphTargets = False
        self.morphNormals = False

        self.setValues( parameters )


    def copy(self, source ):
        super().copy( source )

        self.color.copy( source.color )
        self.specular.copy( source.specular )
        self.shininess = source.shininess

        self.map = source.map

        self.lightMap = source.lightMap
        self.lightMapIntensity = source.lightMapIntensity

        self.aoMap = source.aoMap
        self.aoMapIntensity = source.aoMapIntensity

        self.emissive.copy( source.emissive )
        self.emissiveMap = source.emissiveMap
        self.emissiveIntensity = source.emissiveIntensity

        self.bumpMap = source.bumpMap
        self.bumpScale = source.bumpScale

        self.normalMap = source.normalMap
        self.normalScale.copy( source.normalScale )

        self.displacementMap = source.displacementMap
        self.displacementScale = source.displacementScale
        self.displacementBias = source.displacementBias

        self.specularMap = source.specularMap

        self.alphaMap = source.alphaMap

        self.envMap = source.envMap
        self.combine = source.combine
        self.reflectivity = source.reflectivity
        self.refractionRatio = source.refractionRatio

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth
        self.wireframeLinecap = source.wireframeLinecap
        self.wireframeLinejoin = source.wireframeLinejoin

        self.skinning = source.skinning
        self.morphTargets = source.morphTargets
        self.morphNormals = source.morphNormals

        return self
