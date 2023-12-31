"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""

from THREE.loaders.FileLoader import *
from THREE.materials.ShadowMaterial import *
from THREE.materials.SpriteMaterial import *
from THREE.materials.RawShaderMaterial import *
from THREE.materials.ShaderMaterial import *
from THREE.materials.PointsMaterial import *
from THREE.materials.MeshPhysicalMaterial import *
from THREE.materials.MeshStandardMaterial import *
from THREE.materials.MeshToonMaterial import *
from THREE.materials.MeshNormalMaterial import *
from THREE.materials.MeshLambertMaterial import *
from THREE.materials.MeshDepthMaterial import *
from THREE.materials.MeshDistanceMaterial import *
from THREE.materials.MeshBasicMaterial import *
from THREE.materials.LineDashedMaterial import *
from THREE.materials.LineBasicMaterial import *
from THREE.materials.Material import *


Materials = {
    'ShadowMaterial': ShadowMaterial,
    'SpriteMaterial': SpriteMaterial,
    'RawShaderMaterial': RawShaderMaterial,
    'ShaderMaterial': ShaderMaterial,
    'PointsMaterial': PointsMaterial,
    'MeshPhysicalMaterial': MeshPhysicalMaterial,
    'MeshStandardMaterial': MeshStandardMaterial,
    'MeshPhongMaterial': MeshPhongMaterial,
    'MeshToonMaterial': MeshToonMaterial,
    'MeshNormalMaterial': MeshNormalMaterial,
    'MeshLambertMaterial': MeshLambertMaterial,
    'MeshDepthMaterial': MeshDepthMaterial,
    'MeshDistanceMaterial': MeshDistanceMaterial,
    'MeshBasicMaterial': MeshBasicMaterial,
    'LineDashedMaterial': LineDashedMaterial,
    'LineBasicMaterial': LineBasicMaterial,
    'Material': Material
}


class MaterialLoader:
    def __init__(self, manager=None ):
        self.manager = manager if manager is not None else DefaultLoadingManager
        self.textures = {}

    def load(self, url, onLoad, onProgress=None, onError=None ):
        loader = FileLoader( self.manager )

        def _onLoad(text):
            onLoad( self.parse( json.loads( text ) ) )
            
        loader.load( url, _onLoad, onProgress, onError )

    def setTextures(self, value ):
        self.textures = value

    def parse(self, json):
        global Materials

        textures = self.textures

        def getTexture( name ):
            if name not in textures:
                print( 'THREE.MaterialLoader: Undefined texture', name )

            return textures[ name ]

        material = Materials[ json['type'] ]()

        if 'uuid' in json:
            material.uuid = json['uuid']
        if 'name' in json:
            material.name = json['name']
        if 'color' in json:
            material.color.setHex( json['color'] )
        if 'roughness' in json:
            material.roughness = json['roughness']
        if 'metalness' in json:
            material.metalness = json['metalness']
        if 'emissive' in json:
            material.emissive.setHex( json['emissive'] )
        if 'specular' in json:
            material.specular.setHex( json['specular'] )
        if 'shininess' in json:
            material.shininess = json['shininess']
        if 'clearCoat' in json :
            material.clearCoat = json['clearCoat']
        if 'clearCoatRoughness' in json:
            material.clearCoatRoughness = json['clearCoatRoughness']
        if 'uniforms'in json:
            material.uniforms = json['uniforms']
        if 'vertexShader'in json:
            material.vertexShader = json['vertexShader']
        if 'fragmentShader'in json:
            material.fragmentShader = json['fragmentShader']
        if 'vertexColors' in json:
            material.vertexColors = json['vertexColors']
        if 'fog' in json:
            material.fog = json['fog']
        if 'flatShading' in json:
            material.flatShading = json['flatShading']
        if 'blending'in json:
            material.blending = json['blending']
        if 'side' in json:
            material.side = json['side']
        if 'opacity' in json:
            material.opacity = json['opacity']
        if 'transparent' in json:
            material.transparent = json['transparent']
        if 'alphaTest' in json:
            material.alphaTest = json['alphaTest']
        if 'depthTest' in json:
            material.depthTest = json['depthTest']
        if 'depthWrite' in json:
            material.depthWrite = json['depthWrite']
        if 'colorWrite' in json:
            material.colorWrite = json['colorWrite']
        if 'wireframe' in json:
            material.wireframe = json['wireframe']
        if 'wireframeLinewidth' in json:
            material.wireframeLinewidth = json['wireframeLinewidth']
        if 'wireframeLinecap' in json:
            material.wireframeLinecap = json['wireframeLinecap']
        if 'wireframeLinejoin' in json:
            material.wireframeLinejoin = json['wireframeLinejoin']
        if 'rotation' in json:
            material.rotation = json['rotation']
        if 'linewidth' in json and json['linewidth'] != 1:
            material.linewidth = json['linewidth']
        if 'dashSize' in json:
            material.dashSize = json['dashSize']
        if 'gapSize' in json:
            material.gapSize = json['gapSize']
        if 'scale' in json:
            material.scale = json['scale']

        if 'polygonOffset' in json:
            material.polygonOffset = json['polygonOffset']
        if 'polygonOffsetFactor' in json:
            material.polygonOffsetFactor = json['polygonOffsetFactor']
        if 'polygonOffsetUnits' in json:
            material.polygonOffsetUnits = json['polygonOffsetUnits']

        if 'skinning' in json:
            material.skinning = json['skinning']
        if 'morphTargets' in json:
            material.morphTargets = json['morphTargets']

        # // Deprecated

        if 'shading' in json:
            material.shading = json['shading']

        # // for PointsMaterial

        if 'size' in json:
            material.size = json['size']
        if 'sizeAttenuation' in json:
            material.sizeAttenuation = json['sizeAttenuation']

        # // maps

        if 'map' in json:
            material.map = getTexture( json['map'] )
        if 'normalMapType' in json:
            material.normalMapType = json['normalMapType']

        if 'alphaMap' in json:
            material.alphaMap = getTexture( json['alphaMap'] )
            material.transparent = True

        if 'bumpMap' in json:
            material.bumpMap = getTexture( json['bumpMap'] )
        if 'bumpScale' in json:
            material.bumpScale = json['bumpScale']

        if 'normalMap' in json:
            material.normalMap = getTexture( json['normalMap'] )
        if 'normalScale' in json:
            normalScale = json['normalScale']

            if not isinstance(normalScale, list):
                # // Blender exporter used to export a scalar. See #7459
                normalScale = [ normalScale, normalScale ]

            material.normalScale = Vector2().fromArray( normalScale )

        if 'displacementMap' in json:
            material.displacementMap = getTexture( json['displacementMap'] )
        if 'displacementScale'in json:
            material.displacementScale = json['displacementScale']
        if 'displacementBias' in json:
            material.displacementBias = json['displacementBias']

        if 'roughnessMap' in json:
            material.roughnessMap = getTexture( json['roughnessMap'] )
        if 'metalnessMap' in json:
            material.metalnessMap = getTexture( json['metalnessMap'] )

        if 'emissiveMap' in json:
            material.emissiveMap = getTexture( json['emissiveMap'] )
        if 'emissiveIntensity' in json:
            material.emissiveIntensity = json['emissiveIntensity']

        if 'specularMap' in json:
            material.specularMap = getTexture( json['specularMap'] )

        if 'envMap' in json:
            material.envMap = getTexture( json['envMap'] )

        if 'reflectivity' in json:
            material.reflectivity = json['reflectivity']

        if 'lightMap' in json:
            material.lightMap = getTexture( json['lightMap'] )
        if 'lightMapIntensity' in json:
            material.lightMapIntensity = json['lightMapIntensity']

        if 'aoMap' in json:
            material.aoMap = getTexture( json['aoMap'] )
        if 'aoMapIntensity' in json:
            material.aoMapIntensity = json['aoMapIntensity']

        if 'gradientMap' in json:
            material.gradientMap = getTexture( json['gradientMap'] )

        return material
