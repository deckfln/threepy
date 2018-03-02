"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 *
 * parameters = {
 *  defines: { "label" : "value" },
 *  uniforms: { "parameter1": { value: 1.0 }, "parameter2": { value2: 2 } },
 *
 *  fragmentShader: <string>,
 *  vertexShader: <string>,
 *
 *  wireframe: <boolean>,
 *  wireframeLinewidth: <float>,
 *
 *  lights: <bool>,
 *
 *  skinning: <bool>,
 *  morphTargets: <bool>,
 *  morphNormals: <bool>
 * }
 */
"""
from THREE.Material import *
import THREE.UniformsUtils as UniformsUtils


class ShaderMaterial(Material):
    isShaderMaterial = True

    def __init__(self, parameters=None ):
        super().__init__()
        self.set_class(isShaderMaterial)

        self.type = 'ShaderMaterial'

        self.defines = {}
        self.uniforms = {}

        self.vertexShader = 'void main() {\n\tgl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );\n}'
        self.fragmentShader = 'void main() {\n\tgl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );\n}'

        self.linewidth = 1

        self.wireframe = False
        self.wireframeLinewidth = 1

        self.fog = False	 # // set to use scene fog
        self.lights = False 	# // set to use scene lights
        self.clipping = False 	# // set to use user-defined clipping planes

        self.skinning = False 	# // set to use skinning attribute streams
        self.morphTargets = False 	# // set to use morph targets
        self.morphNormals = False 	# // set to use morph normals

        self.extensions = {
            'derivatives': False, 	# // set to use derivatives
            'fragDepth': False, 	# // set to use fragment depth values
            'drawBuffers': False, 	# // set to use draw buffers
            'shaderTextureLOD': False 	# // set to use shader texture LOD
        }

        # // When rendered geometry doesn't include these attributes but the material does,
        # // use these default values in WebGL. self avoids errors when buffer data is missing.
        self.defaultAttributeValues = {
            'color': [ 1, 1, 1 ],
            'uv': [ 0, 0 ],
            'uv2': [ 0, 0 ]
        }

        self.index0AttributeName = None

        if parameters is not None:
            if 'attributes' in parameters is not None:
                raise RuntimeError( 'THREE.ShaderMaterial: attributes should now be defined in THREE.BufferGeometry instead.' )

            self.setValues( parameters )

    def copy(self, source ):
        super().copy( source )

        self.fragmentShader = source.fragmentShader
        self.vertexShader = source.vertexShader

        self.uniforms = UniformsUtils.clone( source.uniforms )

        self.defines = source.defines

        self.wireframe = source.wireframe
        self.wireframeLinewidth = source.wireframeLinewidth

        self.lights = source.lights
        self.clipping = source.clipping

        self.skinning = source.skinning

        self.morphTargets = source.morphTargets
        self.morphNormals = source.morphNormals

        self.extensions = source.extensions

        return self

    def toJSON(self, meta=None ):
        data = Material.toJSON( meta )

        data.uniforms = self.uniforms
        data.vertexShader = self.vertexShader
        data.fragmentShader = self.fragmentShader

        return data