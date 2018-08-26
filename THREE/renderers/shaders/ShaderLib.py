""""
/**
 * @author alteredq / http://alteredqualia.com/
 * @author mrdoob / http://mrdoob.com/
 * @author mikael emtinger / http://gomo.se/
 */
"""

from THREE.renderers.shaders.ShaderChunk import *
from THREE.renderers.shaders.UniformsLib import *


global ShaderChunk
global UniformsLib

_currentModule = os.path.dirname(__file__)


class _shader_lib:
    def __init__(self, uniforms, vertexShader, fragmentShader):
        self.uniforms = uniforms
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader

    def getVertexShader(self):
        if self.vertexShader[0] == '_':
            loader = THREE.FileLoader()
            self.vertexShader = loader.load('%s/ShaderLib/%s.glsl' % (_currentModule, self.vertexShader[1:]))
        return self.vertexShader

    def getFragmentShader(self):
        if self.fragmentShader[0] == '_':
            loader = THREE.FileLoader()
            self.fragmentShader = loader.load('%s/ShaderLib/%s.glsl' % (_currentModule, self.fragmentShader[1:]))
        return self.fragmentShader


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
            '_meshbasic_vert',
            '_meshbasic_frag'
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
            '_meshlambert_vert',
            '_meshlambert_frag'
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
            '_meshphong_vert',
            '_meshphong_frag'
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
            '_meshphysical_vert',
            '_meshphysical_frag'
        ),

        'points': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['points'],
                UniformsLib['fog']
            ] ),
            '_points_vert',
            '_points_frag'
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
            '_linedashed_vert',
            '_linedashed_frag'
        ),

        'depth': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['common'],
                UniformsLib['displacementmap']
            ] ),
            '_depth_vert',
            '_depth_frag'
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
            '_normal_vert',
            '_normal_frag'
        ),

        'sprite': _shader_lib(
            UniformsUtils.merge([
                UniformsLib['sprite'],
                UniformsLib['fog']
            ]),

            '_sprite_vert',
            '_sprite_frag'
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
            '_cube_vert',
            '_cube_frag'
        ),

        'equirect': _shader_lib(
            {
                'tEquirect': UniformValue(None),
            },
            '_equirect_vert',
            '_equirect_frag'
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
            '_distanceRGBA_vert',
            '_distanceRGBA_frag'
        ),

        'shadow': _shader_lib(
            UniformsUtils.merge( [
                UniformsLib['lights'],
                UniformsLib['fog'],
                {
                    'color': UniformValue(Color(0x00000)),
                    'opacity': UniformValue(1.0)
                },
            ] ),
            '_shadow_vert',
            '_shadow_frag'
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
            '_meshphysical_vert',
            '_meshphysical_frag'
        )
}


def getShaderLib(shaderID):
    global ShaderLib

    shader = ShaderLib[shaderID]

    shader.vertexShader = shader.getVertexShader()
    shader.fragmentShader = shader.getFragmentShader()

    return shader
