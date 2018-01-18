""""
/**
 * @author alteredq / http://alteredqualia.com/
 * @author mrdoob / http://mrdoob.com/
 * @author mikael emtinger / http://gomo.se/
 */
"""

import THREE.UniformsUtils as UniformsUtils
from THREE.ShaderChunk import *
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Vector4 import *
from THREE.Color import *
from THREE.Javascript import *


global ShaderLib
global ShaderChunk

"""
/**
 * Uniforms library for shared webgl shaders
 */
"""


class _uniform_lib:
    def __init__(self, value, properties=None):
        self.value = value
        self.properties = properties


UniformsLib = {

    'common': {

        'diffuse': _uniform_lib(Color(0xeeeeee)),
        'opacity': _uniform_lib(1.0),

        'map': _uniform_lib(None),
        'offsetRepeat': _uniform_lib(Vector4( 0, 0, 1, 1 ) ),

        'alphaMap': _uniform_lib(None),

    },

    'specularmap': {

        'specularMap': _uniform_lib(None ),

    },

    'envmap': {

        'envMap': _uniform_lib(None),
        'flipEnvMap': _uniform_lib(- 1 ),
        'reflectivity': _uniform_lib(1.0 ),
        'refractionRatio': _uniform_lib(0.98 )

    },

    'aomap': {

        'aoMap': _uniform_lib(None),
        'aoMapIntensity': _uniform_lib(1 )

    },

    'lightmap': {

        'lightMap': _uniform_lib(None ),
        'lightMapIntensity': _uniform_lib(1)

    },

    'emissivemap': {

        'emissiveMap': _uniform_lib(None)

    },

    'bumpmap': {

        'bumpMap': _uniform_lib(None),
        'bumpScale': _uniform_lib(1)

    },

    'normalmap': {

        'normalMap': _uniform_lib(None),
        'normalScale': _uniform_lib(Vector2( 1, 1 ) )

    },

    'displacementmap': {

        'displacementMap': _uniform_lib(None),
        'displacementScale': _uniform_lib(1),
        'displacementBias': _uniform_lib(0)

    },

    'roughnessmap': {

        'roughnessMap': _uniform_lib(None)

    },

    'metalnessmap': {

        'metalnessMap': _uniform_lib(None)

    },

    'gradientmap': {

        'gradientMap': _uniform_lib(None)

    },

    'fog': {

        'fogDensity': _uniform_lib(0.00025),
        'fogNear': _uniform_lib(1),
        'fogFar': _uniform_lib(2000),
        'fogColor': _uniform_lib(Color( 0xffffff ) )

    },

    'lights': {

        'ambientLightColor': _uniform_lib(None),

        'directionalLights': _uniform_lib(
            [],
           {
                'direction': {},
                'color': {},

                'shadow': {},
                'shadowBias': {},
                'shadowRadius': {},
                'shadowMapSize': {}
        } ),

        'directionalShadowMap': _uniform_lib([]),
        'directionalShadowMatrix': _uniform_lib([]),

        'spotLights': _uniform_lib([],
            {
            'color': {},
            'position': {},
            'direction': {},
            'distance': {},
            'coneCos': {},
            'penumbraCos': {},
            'decay': {},

            'shadow': {},
            'shadowBias': {},
            'shadowRadius': {},
            'shadowMapSize': {}
        } ),

        'spotShadowMap': _uniform_lib([]),
        'spotShadowMatrix': _uniform_lib([]),

        'pointLights': _uniform_lib([],
            {
            'color': {},
            'position': {},
            'decay': {},
            'distance': {},

            'shadow': {},
            'shadowBias': {},
            'shadowRadius': {},
            'shadowMapSize': {},
            'shadowCameraNear': {},
            'shadowCameraFar': {}
        } ),

        'pointShadowMap': _uniform_lib([]),
        'pointShadowMatrix': _uniform_lib([]),

        'hemisphereLights': _uniform_lib([],
            {
            'direction': {},
            'skyColor': {},
            'groundColor': {}
        } ),

        # // TODO (abelnation): RectAreaLight BRDF data needs to be moved from example to main src
        'rectAreaLights': _uniform_lib([],
            {
            'color': {},
            'position': {},
            'width': {},
            'height': {}
        } )

    },

    'points': {

        'diffuse': _uniform_lib(Color( 0xeeeeee ) ),
        'opacity': _uniform_lib(1.0 ),
        'size': _uniform_lib(1.0 ),
        'scale': _uniform_lib(1.0 ),
        'map': _uniform_lib(None),
        'offsetRepeat': _uniform_lib(Vector4( 0, 0, 1, 1 ) )

    }
}


class _shaders:
    def __init__(self, uniforms, vertexShader, fragmentShader):
        self.uniforms = uniforms
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader


ShaderLib = {
        'basic':  _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['specularmap'],
                UniformsLib['envmap'],
                UniformsLib['aomap'],
                UniformsLib['lightmap'],
                UniformsLib['fog']
            ] ),
            ShaderChunk['meshbasic_vert'],
            ShaderChunk['meshbasic_frag']
        ),

        'lambert': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['specularmap'],
                UniformsLib['envmap'],
                UniformsLib['aomap'],
                UniformsLib['lightmap'],
                UniformsLib['emissivemap'],
                UniformsLib['fog'],
                UniformsLib['lights'],
                {
                    'emissive': _uniform_lib(Color( 0x000000 ))
                }
            ] ),
            ShaderChunk['meshlambert_vert'],
            ShaderChunk['meshlambert_frag']
        ),

        'phong': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['specularmap'],
                UniformsLib['envmap'],
                UniformsLib['aomap'],
                UniformsLib['lightmap'],
                UniformsLib['emissivemap'],
                UniformsLib['bumpmap'],
                UniformsLib['normalmap'],
                UniformsLib['displacementmap'],
                UniformsLib['gradientmap'],
                UniformsLib['fog'],
                UniformsLib['lights'],
                {
                    'emissive': _uniform_lib(Color( 0x000000 )),
                    'specular': _uniform_lib(Color( 0x111111 )),
                    'shininess': _uniform_lib(30)
                }
            ] ),
            ShaderChunk['meshphong_vert'],
            ShaderChunk['meshphong_frag']
        ),

        'standard': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['envmap'],
                UniformsLib['aomap'],
                UniformsLib['lightmap'],
                UniformsLib['emissivemap'],
                UniformsLib['bumpmap'],
                UniformsLib['normalmap'],
                UniformsLib['displacementmap'],
                UniformsLib['roughnessmap'],
                UniformsLib['metalnessmap'],
                UniformsLib['fog'],
                UniformsLib['lights'],
                {
                    'emissive': _uniform_lib(Color( 0x000000 )),
                    'roughness': _uniform_lib(0.5),
                    'metalness': _uniform_lib(0.5),
                    'envMapIntensity': _uniform_lib(1) # // temporary
                }
            ] ),
            ShaderChunk['meshphysical_vert'],
            ShaderChunk['meshphysical_frag']
        ),

        'points': _shaders(
            UniformsUtils.merge( [
                UniformsLib['points'],
                UniformsLib['fog']
            ] ),
            ShaderChunk['points_vert'],
            ShaderChunk['points_frag']
        ),

        'dashed': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['fog'],
                {
                    'scale': _uniform_lib(1),
                    'dashSize': _uniform_lib(1),
                    'totalSize': _uniform_lib(2)
                }
            ] ),
            ShaderChunk['linedashed_vert'],
            ShaderChunk['linedashed_frag']
        ),

        'depth': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['displacementmap']
            ] ),
            ShaderChunk['depth_vert'],
            ShaderChunk['depth_frag']
        ),

        'normal': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['bumpmap'],
                UniformsLib['normalmap'],
                UniformsLib['displacementmap'],
                {
                    'opacity': _uniform_lib(1.0)
                }
            ] ),
            ShaderChunk['normal_vert'],
            ShaderChunk['normal_frag']
        ),

    # /* -------------------------------------------------------------------------
    # //    Cube map shader
    #  ------------------------------------------------------------------------- */

        'cube': _shaders(
            {
                'tCube': _uniform_lib(None),
                'tFlip': _uniform_lib(- 1),
                'opacity': _uniform_lib(1.0)
            },
            ShaderChunk['cube_vert'],
            ShaderChunk['cube_frag']
        ),

        'equirect': _shaders(
            {
                'tEquirect': _uniform_lib(None),
            },
            ShaderChunk['equirect_vert'],
            ShaderChunk['equirect_frag']
        ),

        'distanceRGBA': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['displacementmap'],
                {
                    'referencePosition': _uniform_lib(Vector3()),
                    'nearDistance': _uniform_lib(1),
                    'farDistance': _uniform_lib(1000)
                }
            ] ),
            ShaderChunk['distanceRGBA_vert'],
            ShaderChunk['distanceRGBA_frag']
        ),

        'shadow': _shaders(
            UniformsUtils.merge( [
                UniformsLib['lights'],
                {
                    'color': _uniform_lib(Color( 0x00000 )),
                    'opacity': _uniform_lib(1.0)
                },
            ] ),
            ShaderChunk['shadow_vert'],
            ShaderChunk['shadow_frag']
        ),

        'physical': _shaders(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['envmap'],
                UniformsLib['aomap'],
                UniformsLib['lightmap'],
                UniformsLib['emissivemap'],
                UniformsLib['bumpmap'],
                UniformsLib['normalmap'],
                UniformsLib['displacementmap'],
                UniformsLib['roughnessmap'],
                UniformsLib['metalnessmap'],
                UniformsLib['fog'],
                UniformsLib['lights'],
                {
                    'emissive': _uniform_lib(Color( 0x000000 )),
                    'roughness': _uniform_lib(0.5),
                    'metalness': _uniform_lib(0.5),
                    'envMapIntensity': _uniform_lib(1), # // temporary
                    'clearCoat': _uniform_lib(0),
                    'clearCoatRoughness': _uniform_lib(0)
                }
            ] ),
            ShaderChunk['meshphysical_vert'],
            ShaderChunk['meshphysical_frag']
        )
}