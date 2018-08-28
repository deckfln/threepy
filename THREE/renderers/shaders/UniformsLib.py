"""
/**
 * Uniforms library for shared webgl shaders
 */
"""
from THREE.math.Color import *
from THREE.math.Vector2 import *
from THREE.math.Vector4 import *
from THREE.math.Matrix3 import *
from THREE.UniformValue import *

UniformsLib = {

    'common': {

        'diffuse': UniformValue(Color(0xeeeeee)),
        'opacity': UniformValue(1.0),

        'map': UniformValue(None),
        'uvTransform': UniformValue(Matrix3()),
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
        'refractionRatio': UniformValue(0.98),
        'maxMipLevel': UniformValue(0)
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

    },

    'sprite': {

        'diffuse': UniformValue(Color(0xeeeeee)),
        'opacity': UniformValue(1.0),
        'center': UniformValue(Vector2(0.5, 0.5)),
        'rotation': UniformValue(0.0),
        'map': UniformValue(None),
        'uvTransform': UniformValue(Matrix3())
    }
}

