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
from THREE.UniformValue import *


global ShaderLib
global ShaderChunk

"""
/**
 * Uniforms library for shared webgl shaders
 */
"""

UniformsLib = {

    'common': {

        'diffuse': UniformValue(Color(0xeeeeee)),
        'opacity': UniformValue(1.0),

        'map': UniformValue(None),
        'offsetRepeat': UniformValue(Vector4(0, 0, 1, 1)),

        'alphaMap': UniformValue(None),

    },

    'specularmap': {

        'specularMap': UniformValue(None),

    },

    'envmap': {

        'envMap': UniformValue(None),
        'flipEnvMap': UniformValue(- 1),
        'reflectivity': UniformValue(1.0),
        'refractionRatio': UniformValue(0.98)

    },

    'aomap': {

        'aoMap': UniformValue(None),
        'aoMapIntensity': UniformValue(1)

    },

    'lightmap': {

        'lightMap': UniformValue(None),
        'lightMapIntensity': UniformValue(1)

    },

    'emissivemap': {

        'emissiveMap': UniformValue(None)

    },

    'bumpmap': {

        'bumpMap': UniformValue(None),
        'bumpScale': UniformValue(1)

    },

    'normalmap': {

        'normalMap': UniformValue(None),
        'normalScale': UniformValue(Vector2(1, 1))

    },

    'displacementmap': {

        'displacementMap': UniformValue(None),
        'displacementScale': UniformValue(1),
        'displacementBias': UniformValue(0)

    },

    'roughnessmap': {

        'roughnessMap': UniformValue(None)

    },

    'metalnessmap': {

        'metalnessMap': UniformValue(None)

    },

    'gradientmap': {

        'gradientMap': UniformValue(None)

    },

    'fog': {

        'fogDensity': UniformValue(0.00025),
        'fogNear': UniformValue(1),
        'fogFar': UniformValue(2000),
        'fogColor': UniformValue(Color(0xffffff))

    },

    'lights': {

        'ambientLightColor': UniformValue(None),

        'directionalLights': UniformValue(
            [],
           {
                'direction': {},
                'color': {},

                'shadow': {},
                'shadowBias': {},
                'shadowRadius': {},
                'shadowMapSize': {}
        } ),

        'directionalShadowMap': UniformValue([]),
        'directionalShadowMatrix': UniformValue([]),

        'spotLights': UniformValue([],
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
        }),

        'spotShadowMap': UniformValue([]),
        'spotShadowMatrix': UniformValue([]),

        'pointLights': UniformValue([],
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
        }),

        'pointShadowMap': UniformValue([]),
        'pointShadowMatrix': UniformValue([]),

        'hemisphereLights': UniformValue([],
                                         {
            'direction': {},
            'skyColor': {},
            'groundColor': {}
        }),

        # // TODO (abelnation): RectAreaLight BRDF data needs to be moved from example to main src
        'rectAreaLights': UniformValue([],
                                       {
            'color': {},
            'position': {},
            'width': {},
            'height': {}
        })

    },

    'points': {

        'diffuse': UniformValue(Color(0xeeeeee)),
        'opacity': UniformValue(1.0),
        'size': UniformValue(1.0),
        'scale': UniformValue(1.0),
        'map': UniformValue(None),
        'offsetRepeat': UniformValue(Vector4(0, 0, 1, 1))

    }
}


class _shader_lib:
    def __init__(self, uniforms, vertexShader, fragmentShader):
        self.uniforms = uniforms
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader


ShaderLib = {
        'basic':  _shader_lib(
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

        'lambert': _shader_lib(
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
                    'emissive': UniformValue(Color(0x000000))
                }
            ] ),
            ShaderChunk['meshlambert_vert'],
            ShaderChunk['meshlambert_frag']
        ),

        'phong': _shader_lib(
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
                    'emissive': UniformValue(Color(0x000000)),
                    'specular': UniformValue(Color(0x111111)),
                    'shininess': UniformValue(30)
                }
            ] ),
            ShaderChunk['meshphong_vert'],
            ShaderChunk['meshphong_frag']
        ),

        'standard': _shader_lib(
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
                    'emissive': UniformValue(Color(0x000000)),
                    'roughness': UniformValue(0.5),
                    'metalness': UniformValue(0.5),
                    'envMapIntensity': UniformValue(1) # // temporary
                }
            ] ),
            ShaderChunk['meshphysical_vert'],
            ShaderChunk['meshphysical_frag']
        ),

        'points': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['points'],
                UniformsLib['fog']
            ] ),
            ShaderChunk['points_vert'],
            ShaderChunk['points_frag']
        ),

        'dashed': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['fog'],
                {
                    'scale': UniformValue(1),
                    'dashSize': UniformValue(1),
                    'totalSize': UniformValue(2)
                }
            ] ),
            ShaderChunk['linedashed_vert'],
            ShaderChunk['linedashed_frag']
        ),

        'depth': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['displacementmap']
            ] ),
            ShaderChunk['depth_vert'],
            ShaderChunk['depth_frag']
        ),

        'normal': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['bumpmap'],
                UniformsLib['normalmap'],
                UniformsLib['displacementmap'],
                {
                    'opacity': UniformValue(1.0)
                }
            ] ),
            ShaderChunk['normal_vert'],
            ShaderChunk['normal_frag']
        ),

    # /* -------------------------------------------------------------------------
    # //    Cube map shader
    #  ------------------------------------------------------------------------- */

        'cube': _shader_lib(
            {
                'tCube': UniformValue(None),
                'tFlip': UniformValue(- 1),
                'opacity': UniformValue(1.0)
            },
            ShaderChunk['cube_vert'],
            ShaderChunk['cube_frag']
        ),

        'equirect': _shader_lib(
            {
                'tEquirect': UniformValue(None),
            },
            ShaderChunk['equirect_vert'],
            ShaderChunk['equirect_frag']
        ),

        'distanceRGBA': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['displacementmap'],
                {
                    'referencePosition': UniformValue(Vector3()),
                    'nearDistance': UniformValue(1),
                    'farDistance': UniformValue(1000)
                }
            ] ),
            ShaderChunk['distanceRGBA_vert'],
            ShaderChunk['distanceRGBA_frag']
        ),

        'shadow': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['lights'],
                {
                    'color': UniformValue(Color(0x00000)),
                    'opacity': UniformValue(1.0)
                },
            ] ),
            ShaderChunk['shadow_vert'],
            ShaderChunk['shadow_frag']
        ),

        'physical': _shader_lib(
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
                    'emissive': UniformValue(Color(0x000000)),
                    'roughness': UniformValue(0.5),
                    'metalness': UniformValue(0.5),
                    'envMapIntensity': UniformValue(1), # // temporary
                    'clearCoat': UniformValue(0),
                    'clearCoatRoughness': UniformValue(0)
                }
            ] ),
            ShaderChunk['meshphysical_vert'],
            ShaderChunk['meshphysical_frag']
        )
}