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

UniformsLib = {

    'common': {

        'diffuse': {'value': Color(0xeeeeee)},
        'opacity': {'value': 1.0},

        'map': { 'value': None },
        'offsetRepeat': { 'value': Vector4( 0, 0, 1, 1 ) },

        'alphaMap': { 'value': None},

    },

    'specularmap': {

        'specularMap': { 'value': None },

    },

    'envmap': {

        'envMap': { 'value': None},
        'flipEnvMap': { 'value': - 1 },
        'reflectivity': { 'value': 1.0 },
        'refractionRatio': { 'value': 0.98 }

    },

    'aomap': {

        'aoMap': { 'value': None },
        'aoMapIntensity': { 'value': 1 }

    },

    'lightmap': {

        'lightMap': { 'value': None },
        'lightMapIntensity': { 'value': 1 }

    },

    'emissivemap': {

        'emissiveMap': { 'value': None }

    },

    'bumpmap': {

        'bumpMap': { 'value': None },
        'bumpScale': { 'value': 1 }

    },

    'normalmap': {

        'normalMap': { 'value': None },
        'normalScale': { 'value': Vector2( 1, 1 ) }

    },

    'displacementmap': {

        'displacementMap': { 'value': None },
        'displacementScale': { 'value': 1 },
        'displacementBias': { 'value': 0 }

    },

    'roughnessmap': {

        'roughnessMap': { 'value': None }

    },

    'metalnessmap': {

        'metalnessMap': { 'value': None }

    },

    'gradientmap': {

        'gradientMap': { 'value': None }

    },

    'fog': {

        'fogDensity': { 'value': 0.00025 },
        'fogNear': { 'value': 1 },
        'fogFar': { 'value': 2000 },
        'fogColor': { 'value': Color( 0xffffff ) }

    },

    'lights': {

        'ambientLightColor': { 'value': None },

        'directionalLights': { 'value': [],
           'properties': {
            'direction': {},
            'color': {},

            'shadow': {},
            'shadowBias': {},
            'shadowRadius': {},
            'shadowMapSize': {}
        } },

        'directionalShadowMap': { 'value': [] },
        'directionalShadowMatrix': { 'value': [] },

        'spotLights': { 'value': [],
                         'properties': {
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
        } },

        'spotShadowMap': { 'value': [] },
        'spotShadowMatrix': { 'value': [] },

        'pointLights': { 'value': [],
                        'properties': {
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
        } },

        'pointShadowMap': { 'value': [] },
        'pointShadowMatrix': { 'value': [] },

        'hemisphereLights': {'value': [],
                            'properties': {
            'direction': {},
            'skyColor': {},
            'groundColor': {}
        } },

        # // TODO (abelnation): RectAreaLight BRDF data needs to be moved from example to main src
        'rectAreaLights': { 'value': [],
                            'properties': {
            'color': {},
            'position': {},
            'width': {},
            'height': {}
        } }

    },

    'points': {

        'diffuse': { 'value': Color( 0xeeeeee ) },
        'opacity': { 'value': 1.0 },
        'size': { 'value': 1.0 },
        'scale': { 'value': 1.0 },
        'map': { 'value': None },
        'offsetRepeat': { 'value': Vector4( 0, 0, 1, 1 ) }

    }
}

_ShaderLib = {

    'basic': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['specularmap'],
            UniformsLib['envmap'],
            UniformsLib['aomap'],
            UniformsLib['lightmap'],
            UniformsLib['fog']
        ] ),

        'vertexShader': ShaderChunk['meshbasic_vert'],
        'fragmentShader': ShaderChunk['meshbasic_frag']

    },

    'lambert': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['specularmap'],
            UniformsLib['envmap'],
            UniformsLib['aomap'],
            UniformsLib['lightmap'],
            UniformsLib['emissivemap'],
            UniformsLib['fog'],
            UniformsLib['lights'],
            {
                'emissive': { 'value': Color( 0x000000 ) }
            }
        ] ),

        'vertexShader': ShaderChunk['meshlambert_vert'],
        'fragmentShader': ShaderChunk['meshlambert_frag']

    },

    'phong': {

        'uniforms': UniformsUtils.merge( [
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
                'emissive': { 'value': Color( 0x000000 ) },
                'specular': { 'value': Color( 0x111111 ) },
                'shininess': { 'value': 30 }
            }
        ] ),

        'vertexShader': ShaderChunk['meshphong_vert'],
        'fragmentShader': ShaderChunk['meshphong_frag']

    },

    'standard': {

        'uniforms': UniformsUtils.merge( [
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
                'emissive': { 'value': Color( 0x000000 ) },
                'roughness': { 'value': 0.5 },
                'metalness': { 'value': 0.5 },
                'envMapIntensity': { 'value': 1 } # // temporary
            }
        ] ),

        'vertexShader': ShaderChunk['meshphysical_vert'],
        'fragmentShader': ShaderChunk['meshphysical_frag']

    },

    'points': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['points'],
            UniformsLib['fog']
        ] ),

        'vertexShader': ShaderChunk['points_vert'],
        'fragmentShader': ShaderChunk['points_frag']

    },

    'dashed': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['fog'],
            {
                'scale': { 'value': 1 },
                'dashSize': { 'value': 1 },
                'totalSize': { 'value': 2 }
            }
        ] ),

        'vertexShader': ShaderChunk['linedashed_vert'],
        'fragmentShader': ShaderChunk['linedashed_frag']

    },

    'depth': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['displacementmap']
        ] ),

        'vertexShader': ShaderChunk['depth_vert'],
        'fragmentShader': ShaderChunk['depth_frag']

    },

    'normal': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['bumpmap'],
            UniformsLib['normalmap'],
            UniformsLib['displacementmap'],
            {
                'opacity': { 'value': 1.0 }
            }
        ] ),

        'vertexShader': ShaderChunk['normal_vert'],
        'fragmentShader': ShaderChunk['normal_frag']

    },

    # /* -------------------------------------------------------------------------
    # //    Cube map shader
    #  ------------------------------------------------------------------------- */

    'cube': {

        'uniforms': {
            'tCube': { 'value': None },
            'tFlip': { 'value': - 1 },
            'opacity': { 'value': 1.0 }
        },

        'vertexShader': ShaderChunk['cube_vert'],
        'fragmentShader': ShaderChunk['cube_frag']

    },

    'equirect': {

        'uniforms': {
            'tEquirect': { 'value': None },
        },

        'vertexShader': ShaderChunk['equirect_vert'],
        'fragmentShader': ShaderChunk['equirect_frag']

    },

    'distanceRGBA': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['common'],
            UniformsLib['displacementmap'],
            {
                'referencePosition': { 'value': Vector3() },
                'nearDistance': { 'value': 1 },
                'farDistance': { 'value': 1000 }
            }
        ] ),

        'vertexShader': ShaderChunk['distanceRGBA_vert'],
        'fragmentShader': ShaderChunk['distanceRGBA_frag']

    },

    'shadow': {

        'uniforms': UniformsUtils.merge( [
            UniformsLib['lights'],
            {
                'color': { 'value': Color( 0x00000 ) },
                'opacity': { 'value': 1.0 }
            },
        ] ),

        'vertexShader': ShaderChunk['shadow_vert'],
        'fragmentShader': ShaderChunk['shadow_frag']

    }

}

_ShaderLib['physical'] = {

    'uniforms': UniformsUtils.merge( [
        _ShaderLib['standard']['uniforms'],
        {
            'clearCoat': { 'value': 0 },
            'clearCoatRoughness': { 'value': 0 }
        }
    ] ),

    'vertexShader': ShaderChunk['meshphysical_vert'],
    'fragmentShader': ShaderChunk['meshphysical_frag']

}

ShaderLib = javascriptObject(_ShaderLib)
