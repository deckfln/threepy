"""
 * @author Rich Tibbett / https:#github.com/richtr
 * @author mrdoob / http:#mrdoob.com/
 * @author Tony Parisi / http:#www.tonyparisi.com/
 * @author Takahiro / https:#github.com/takahirox
 * @author Don McCurdy / https:#www.donmccurdy.com
 */
"""
import json as JSON

from THREE.loaders.FileLoader import *
from THREE.javascriparray import *
from THREE.loaders.DDSLoader import *
from THREE.loaders.TextureLoader import *
from THREE.math.Interpolant import *
from THREE._Math import *
from THREE.loaders.LoaderUtils import *
from THREE.objects.SkinnedMesh import *
from THREE.objects.Bone import *


class Gltf:
    def __init__(self, scene, scenes, cameras, animations, asset, parser, userdata):
        self.scene = scene
        self.scenes = scenes
        self.cameras = cameras
        self.animations = animations
        self.asset = asset
        self.parser = parser
        self.userData = userdata


"""
/*********************************/
/********** EXTENSIONS ***********/
/*********************************/
"""

_KHR_BINARY_GLTF = 'KHR_binary_glTF',
_KHR_DRACO_MESH_COMPRESSION = 'KHR_draco_mesh_compression'
_KHR_LIGHTS_PUNCTUAL = 'KHR_lights_punctual'
_KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS = 'KHR_materials_pbrSpecularGlossiness'
_KHR_MATERIALS_UNLIT = 'KHR_materials_unlit'
_MSFT_TEXTURE_DDS = 'MSFT_texture_dds'

"""
/* BINARY EXTENSION */
"""

_BINARY_EXTENSION_BUFFER_NAME = 'binary_glTF'
_BINARY_EXTENSION_HEADER_MAGIC = 'glTF'
_BINARY_EXTENSION_HEADER_LENGTH = 12
_BINARY_EXTENSION_CHUNK_TYPES = { 'JSON': 0x4E4F534A, 'BIN': 0x004E4942 }


class GLTFLoader:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else THREE.DefaultLoadingManager
        self.dracoLoader = None
        self.crossOrigin = None
        self.path = None

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        scope = self
        path = self.path  if self.path is not None else extractUrlBase(url)
        loader = FileLoader(scope.manager)
        loader.setResponseType('arraybuffer')

        def _load(data):
            scope.parse(data, path, onLoad, onError)

        loader.load(url, _load, onProgress, onError)

    def setCrossOrigin(self, value):
        self.crossOrigin = value
        return self

    def setPath(self, value):
        self.path = value
        return self

    def setDRACOLoader(self, dracoLoader):
        self.dracoLoader = dracoLoader
        return self

    def parse(self, data, path, onLoad, onError):
        extensions = {}

        if isinstance(data, str):
            content = data
        else:
            magic = data[0:4]

            if magic == _BINARY_EXTENSION_HEADER_MAGIC:
                extensions[_KHR_BINARY_GLTF] = GLTFBinaryExtension(data)

                content = extensions[_KHR_BINARY_GLTF].content
            else:
                content = data.decode("utf-8")

        json = JSON.loads(content)

        if 'asset' not in json or float(json['asset']['version']) < 2:
            if onError:
                raise RuntimeError('THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported. Use LegacyGLTFLoader instead.')

        if 'extensionsUsed' in json:
            for i in range(len(json['extensionsUsed'])):
                extensionName = json['extensionsUsed'][i]
                extensionsRequired = json['extensionsRequired'] or []

                if extensionName == _KHR_LIGHTS_PUNCTUAL:
                        extensions[extensionName] = GLTFLightsExtension(json)

                elif extensionName == _KHR_MATERIALS_UNLIT:
                        extensions[extensionName] = GLTFMaterialsUnlitExtension(json)

                elif extensionName == _KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS:
                        extensions[extensionName] = GLTFMaterialsPbrSpecularGlossinessExtension()

                elif extensionName == _KHR_DRACO_MESH_COMPRESSION:
                        extensions[extensionName] = GLTFDracoMeshCompressionExtension(json, self.dracoLoader)

                elif extensionName == _MSFT_TEXTURE_DDS:
                        extensions[_MSFT_TEXTURE_DDS] = GLTFTextureDDSExtension()

                elif extensionsRequired.indexOf(extensionName) >= 0:
                        print('THREE.GLTFLoader: Unknown extension "' + extensionName + '".')

        parser = GLTFParser(json, extensions, {
            'path': path or self.path or '',
            'crossOrigin': self.crossOrigin,
            'manager': self.manager
        })

        def _parse (scene, scenes, cameras, animations, json):
            glTF = Gltf(scene, scenes, cameras, animations, json['asset'], parser, {})

            addUnknownExtensionsToUserData(extensions, glTF, json)

            onLoad(glTF)

        parser.parse(_parse , onError)


"""
/* GLTFREGISTRY */
"""


class GLTFRegistry:
    def add(self, key, object):
        self.__dict__[key] = object

    def get(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        return None

    def removeAll(self):
        self.__dict__.clear()


"""
 * DDS Texture Extension
 *
 * Specification:
 * https:#github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Vendor/MSFT_texture_dds
 *
"""


class GLTFTextureDDSExtension:
    def __init__(self):
        self.name = _MSFT_TEXTURE_DDS
        self.ddsLoader = DDSLoader()


"""
 * Lights Extension
 *
 * Specification: PENDING
"""


class GLTFLightsExtension:
    def __init__(self, json):
        self.name = _KHR_LIGHTS_PUNCTUAL

        self.lights = []

        extension = (json.extensions and json.extensions[_KHR_LIGHTS_PUNCTUAL]) or {}
        lightDefs = extension.lights or []

        for i in range(len(lightDefs)):
            lightDef = lightDefs[i]

            color = THREE.Color(0xffffff)
            if lightDef.color is not None:
                color.fromArray(lightDef.color)

            range = lightDef.range if lightDef.range is not None else 0

            if lightDef.type == 'directional':
                    lightNode = THREE.DirectionalLight(color)
                    lightNode.target.position.set(0, 0, 1)
                    lightNode.add(lightNode.target)

            elif lightDef.type == 'point':
                    lightNode = THREE.PointLight(color)
                    lightNode.distance = range

            elif lightDef.type == 'spot':
                    lightNode = THREE.SpotLight(color)
                    lightNode.distance = range
                    # Handle spotlight properties.
                    lightDef.spot = lightDef.spot or {}
                    lightDef.spot.innerConeAngle = lightDef.spot.innerConeAngle if lightDef.spot.innerConeAngle is not None else 0
                    lightDef.spot.outerConeAngle = lightDef.spot.outerConeAngle if lightDef.spot.outerConeAngle is not None else math.pi / 4.0
                    lightNode.angle = lightDef.spot.outerConeAngle
                    lightNode.penumbra = 1.0 - lightDef.spot.innerConeAngle / lightDef.spot.outerConeAngle
                    lightNode.target.position.set(0, 0, 1)
                    lightNode.add(lightNode.target)

            else:
                    raise RuntimeError('THREE.GLTFLoader: Unexpected light type, "' + lightDef.type + '".')

            lightNode.decay = 2

            if lightDef.intensity is not None:
                lightNode.intensity = lightDef.intensity

            lightNode.name = lightDef.name or ('light_%d' % i)

            self.lights.append(lightNode)


"""
 * Unlit Materials Extension (pending)
 *
 * PR: https:#github.com/KhronosGroup/glTF/pull/1163
"""


class GLTFMaterialsUnlitExtension:
    def __init__(self, json):
        self.name = _KHR_MATERIALS_UNLIT


    def getMaterialType(self, material):
        return THREE.MeshBasicMaterial

    def extendParams(self, materialParams, material, parser):
        pending = []

        materialParams.color = THREE.Color(1.0, 1.0, 1.0)
        materialParams.opacity = 1.0

        metallicRoughness = material.pbrMetallicRoughness

        if metallicRoughness:
            if Array.isArray(metallicRoughness.baseColorFactor):
                array = metallicRoughness.baseColorFactor

                materialParams.color.fromArray(array)
                materialParams.opacity = array[3]

            if metallicRoughness.baseColorTexture is not None:
                pending.append(parser.assignTexture(materialParams, 'map', metallicRoughness.baseColorTexture.index))

        return Promise.all(pending)


class GLTFBinaryExtension:
    def __init__(self, data):
        self.name = _KHR_BINARY_GLTF
        self.content = None
        self.body = None

        headerView = DataView(data, 0, _BINARY_EXTENSION_HEADER_LENGTH)

        self.header = {
            'magic': THREE.LoaderUtils.decodeText(Uint8Array(data.slice(0, 4))),
            'version': headerView.getUint32(4, True),
            'length': headerView.getUint32(8, True)
        }

        if self.header.magic != _BINARY_EXTENSION_HEADER_MAGIC:
            raise RuntimeError('THREE.GLTFLoader: Unsupported glTF-Binary header.')

        elif self.header.version < 2.0:
            raise RuntimeError('THREE.GLTFLoader: Legacy binary file detected. Use LegacyGLTFLoader instead.')

        chunkView = DataView(data, _BINARY_EXTENSION_HEADER_LENGTH)
        chunkIndex = 0

        while chunkIndex < chunkView.byteLength:
            chunkLength = chunkView.getUint32(chunkIndex, True)
            chunkIndex += 4

            chunkType = chunkView.getUint32(chunkIndex, True)
            chunkIndex += 4

            if chunkType == _BINARY_EXTENSION_CHUNK_TYPES['JSON']:
                contentArray = Uint8Array(data, _BINARY_EXTENSION_HEADER_LENGTH + chunkIndex, chunkLength)
                self.content = THREE.LoaderUtils.decodeText(contentArray)

            elif chunkType == _BINARY_EXTENSION_CHUNK_TYPES['BIN']:
                byteOffset = _BINARY_EXTENSION_HEADER_LENGTH + chunkIndex
                self.body = data.slice(byteOffset, byteOffset + chunkLength)

            # Clients must ignore chunks with unknown types.
            chunkIndex += chunkLength

        if self.content is None:
            raise RuntimeError('THREE.GLTFLoader: JSON content not found.')


"""
 * DRACO Mesh Compression Extension
 *
 * Specification: https:#github.com/KhronosGroup/glTF/pull/874
"""


class GLTFDracoMeshCompressionExtension:
    def __init__(self, json, dracoLoader):
        if not dracoLoader:
            raise RuntimeError('THREE.GLTFLoader: No DRACOLoader instance provided.')

        self.name = _KHR_DRACO_MESH_COMPRESSION
        self.json = json
        self.dracoLoader = dracoLoader

    def decodePrimitive(self, primitive, parser):
        json = self.json
        dracoLoader = self.dracoLoader
        bufferViewIndex = primitive.extensions[self.name].bufferView
        gltfAttributeMap = primitive.extensions[self.name].attributes
        threeAttributeMap = {}
        attributeNormalizedMap = {}
        attributeTypeMap = {}

        for attributeName in gltfAttributeMap:
            if not (attributeName in ATTRIBUTES):
                continue
            threeAttributeMap[ATTRIBUTES[attributeName]] = gltfAttributeMap[attributeName]

        for attributeName in primitive.attributes:
            if ATTRIBUTES[attributeName] is not None and gltfAttributeMap[attributeName] is not None:
                accessorDef = json.accessors[primitive.attributes[attributeName]]
                componentType = WEBGL_COMPONENT_TYPES[accessorDef.componentType]

                attributeTypeMap[ATTRIBUTES[attributeName]] = componentType
                attributeNormalizedMap[ATTRIBUTES[attributeName]] = accessorDef.normalized == True

        dependencies = parser.getDependency('bufferView', bufferViewIndex)

        for d in dependencies:
            def _geometry(geometry):
                for attributeName in geometry.attributes:
                    attribute = geometry.attributes[attributeName]
                    normalized = attributeNormalizedMap[attributeName]

                    if normalized is not None:
                        attribute.normalized = normalized

                resolve(geometry)

            dracoLoader.decodeDracoFile(bufferView, _geometry, threeAttributeMap, attributeTypeMap)


"""
* Specular-Glossiness Extension
*
* Specification: https:#github.com/KhronosGroup/glTF/tree/master/extensions/2.0/Khronos/KHR_materials_pbrSpecularGlossiness
"""


class GLTFMaterialsPbrSpecularGlossinessExtension:
    def __init__(self):
        self.name = _KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS

        self.specularGlossinessParams = [
            'color',
            'map',
            'lightMap',
            'lightMapIntensity',
            'aoMap',
            'aoMapIntensity',
            'emissive',
            'emissiveIntensity',
            'emissiveMap',
            'bumpMap',
            'bumpScale',
            'normalMap',
            'displacementMap',
            'displacementScale',
            'displacementBias',
            'specularMap',
            'specular',
            'glossinessMap',
            'glossiness',
            'alphaMap',
            'envMap',
            'envMapIntensity',
            'refractionRatio',
        ]

    def getMaterialType(self):
        return THREE.ShaderMaterial

    def extendParams(self, params, material, parser):
        pbrSpecularGlossiness = material.extensions[self.name]

        shader = THREE.ShaderLib['standard']

        uniforms = THREE.UniformsUtils.clone(shader.uniforms)

        specularMapParsFragmentChunk = '\n'.join([
            '#ifdef USE_SPECULARMAP',
            '    uniform sampler2D specularMap;',
            '#endif'
        ])

        glossinessMapParsFragmentChunk = '\n'.join([
            '#ifdef USE_GLOSSINESSMAP',
            '    uniform sampler2D glossinessMap;',
            '#endif'
        ])

        specularMapFragmentChunk = '\n'.join([
            'vec3 specularFactor = specular;',
            '#ifdef USE_SPECULARMAP',
            '    vec4 texelSpecular = texture2D(specularMap, vUv);',
            '    texelSpecular = sRGBToLinear(texelSpecular);',
            '    # reads channel RGB, compatible with a glTF Specular-Glossiness (RGBA) texture',
            '    specularFactor *= texelSpecular.rgb;',
            '#endif'
        ])

        glossinessMapFragmentChunk = '\n'.join([
            'float glossinessFactor = glossiness;',
            '#ifdef USE_GLOSSINESSMAP',
            '    vec4 texelGlossiness = texture2D(glossinessMap, vUv);',
            '    # reads channel A, compatible with a glTF Specular-Glossiness (RGBA) texture',
            '    glossinessFactor *= texelGlossiness.a;',
            '#endif'
        ])

        lightPhysicalFragmentChunk = '\n'.join([
            'PhysicalMaterial material;',
            'material.diffuseColor = diffuseColor.rgb;',
            'material.specularRoughness = clamp(1.0 - glossinessFactor, 0.04, 1.0);',
            'material.specularColor = specularFactor.rgb;',
        ])

        fragmentShader = shader.fragmentShader.replace('uniform float roughness;', 'uniform vec3 specular;').replace('uniform float metalness;', 'uniform float glossiness;').replace('#include <roughnessmap_pars_fragment>', specularMapParsFragmentChunk).replace('#include <metalnessmap_pars_fragment>', glossinessMapParsFragmentChunk).replace('#include <roughnessmap_fragment>', specularMapFragmentChunk).replace('#include <metalnessmap_fragment>', glossinessMapFragmentChunk).replace('#include <lights_physical_fragment>', lightPhysicalFragmentChunk)

        del uniforms.roughness
        del uniforms.metalness
        del uniforms.roughnessMap
        del uniforms.metalnessMap

        uniforms.specular = { 'value': THREE.Color().setHex(0x111111) }
        uniforms.glossiness = { 'value': 0.5 }
        uniforms.specularMap = { 'value': None }
        uniforms.glossinessMap = { 'value': None }

        params.vertexShader = shader.vertexShader
        params.fragmentShader = fragmentShader
        params.uniforms = uniforms
        params.defines = { 'STANDARD': '' }

        params.color = THREE.Color(1.0, 1.0, 1.0)
        params.opacity = 1.0

        pending = []

        if Array.isArray(pbrSpecularGlossiness.diffuseFactor):
            array = pbrSpecularGlossiness.diffuseFactor

            params.color.fromArray(array)
            params.opacity = array[3]

        if pbrSpecularGlossiness.diffuseTexture is not None:
            pending.append(parser.assignTexture(params, 'map', pbrSpecularGlossiness.diffuseTexture.index))

        params.emissive = THREE.Color(0.0, 0.0, 0.0)
        params.glossiness = pbrSpecularGlossiness.glossinessFactor if pbrSpecularGlossiness.glossinessFactor is not None else 1.0
        params.specular = THREE.Color(1.0, 1.0, 1.0)

        if Array.isArray(pbrSpecularGlossiness.specularFactor):
            params.specular.fromArray(pbrSpecularGlossiness.specularFactor)

        if pbrSpecularGlossiness.specularGlossinessTexture is not None:
            specGlossIndex = pbrSpecularGlossiness.specularGlossinessTexture.index
            pending.append(parser.assignTexture(params, 'glossinessMap', specGlossIndex))
            pending.append(parser.assignTexture(params, 'specularMap', specGlossIndex))

        return pending

    def createMaterial(self, params):
        """
        setup material properties based on MeshStandardMaterial for Specular-Glossiness
        """
        material = THREE.ShaderMaterial({
            'defines': params.defines,
            'vertexShader': params.vertexShader,
            'fragmentShader': params.fragmentShader,
            'uniforms': params.uniforms,
            'fog': True,
            'lights': True,
            'opacity': params.opacity,
            'transparent': params.transparent
        })

        material.isGLTFSpecularGlossinessMaterial = True

        material.color = params.color

        material.map = None if params.map is None else params.map

        material.lightMap = None
        material.lightMapIntensity = 1.0

        material.aoMap = None if params.aoMap is None else params.aoMap
        material.aoMapIntensity = 1.0

        material.emissive = params.emissive
        material.emissiveIntensity = 1.0
        material.emissiveMap = None if params.emissiveMap is None else params.emissiveMap

        material.bumpMap = None if params.bumpMap is None else params.bumpMap
        material.bumpScale = 1

        material.normalMap = None if params.normalMap is None else params.normalMap
        if params.normalScale:
            material.normalScale = params.normalScale

        material.displacementMap = None
        material.displacementScale = 1
        material.displacementBias = 0

        material.specularMap = None if params.specularMap is None else params.specularMap
        material.specular = params.specular

        material.glossinessMap = None if params.glossinessMap is None else params.glossinessMap
        material.glossiness = params.glossiness

        material.alphaMap = None

        material.envMap = None if params.envMap is None else params.envMap
        material.envMapIntensity = 1.0

        material.refractionRatio = 0.98

        material.extensions.derivatives = True

        return material


    def cloneMaterial(self, source):
        """
         * Clones a GLTFSpecularGlossinessMaterial instance. The ShaderMaterial.copy() method can
         * copy only properties it knows about or inherits, and misses many properties that would
         * normally be defined by MeshStandardMaterial.
         *
         * self method allows GLTFSpecularGlossinessMaterials to be cloned in the process of
         * loading a glTF model, but cloning later (e.g. by the user) would require these changes
         * AND also updating `.onBeforeRender` on the parent mesh.
         *
         * @param  {THREE.ShaderMaterial} source
         * @return {THREE.ShaderMaterial}
        """
        target = source.clone()

        target.isGLTFSpecularGlossinessMaterial = True

        params = self.specularGlossinessParams

        for i in range(len(params)):
            target[params[i]] = source[params[i]]

        return target

    def refreshUniforms(self, renderer, scene, camera, geometry, material, group):
        """
        Here's based on refreshUniformsCommon() and refreshUniformsStandard() in WebGLRenderer.
        """
        if material.isGLTFSpecularGlossinessMaterial is not True:
            return

        uniforms = material.uniforms
        defines = material.defines

        uniforms.opacity.value = material.opacity

        uniforms.diffuse.value.copy(material.color)
        uniforms.emissive.value.copy(material.emissive).multiplyScalar(material.emissiveIntensity)

        uniforms.map.value = material.map
        uniforms.specularMap.value = material.specularMap
        uniforms.alphaMap.value = material.alphaMap

        uniforms.lightMap.value = material.lightMap
        uniforms.lightMapIntensity.value = material.lightMapIntensity

        uniforms.aoMap.value = material.aoMap
        uniforms.aoMapIntensity.value = material.aoMapIntensity

        """
        # uv repeat and offset setting priorities
        # 1. color map
        # 2. specular map
        # 3. normal map
        # 4. bump map
        # 5. alpha map
        # 6. emissive map
        """
        if material.map:
            uvScaleMap = material.map

        elif material.specularMap:
            uvScaleMap = material.specularMap

        elif material.displacementMap:
            uvScaleMap = material.displacementMap

        elif material.normalMap:
            uvScaleMap = material.normalMap

        elif material.bumpMap:
            uvScaleMap = material.bumpMap

        elif material.glossinessMap:
            uvScaleMap = material.glossinessMap

        elif material.alphaMap:
            uvScaleMap = material.alphaMap

        elif material.emissiveMap:
            uvScaleMap = material.emissiveMap

        if uvScaleMap is not None:
            # backwards compatibility
            if uvScaleMap.isWebGLRenderTarget:
                uvScaleMap = uvScaleMap.texture

            if uvScaleMap.matrixAutoUpdate == True:
                uvScaleMap.updateMatrix()

            uniforms.uvTransform.value.copy(uvScaleMap.matrix)

        uniforms.envMap.value = material.envMap
        uniforms.envMapIntensity.value = material.envMapIntensity
        uniforms.flipEnvMap.value = -1 if material.envMap and material.envMap.isCubeTexture else 1

        uniforms.refractionRatio.value = material.refractionRatio

        uniforms.specular.value.copy(material.specular)
        uniforms.glossiness.value = material.glossiness

        uniforms.glossinessMap.value = material.glossinessMap

        uniforms.emissiveMap.value = material.emissiveMap
        uniforms.bumpMap.value = material.bumpMap
        uniforms.normalMap.value = material.normalMap

        uniforms.displacementMap.value = material.displacementMap
        uniforms.displacementScale.value = material.displacementScale
        uniforms.displacementBias.value = material.displacementBias

        if uniforms.glossinessMap.value is not None and defines.USE_GLOSSINESSMAP is None:
            defines.USE_GLOSSINESSMAP = ''
            # set USE_ROUGHNESSMAP to enable vUv
            defines.USE_ROUGHNESSMAP = ''

        if uniforms.glossinessMap.value is None and defines.USE_GLOSSINESSMAP is not None:
            del defines.USE_GLOSSINESSMAP
            del defines.USE_ROUGHNESSMAP


"""
/*********************************/
/********** INTERPOLATION ********/
/*********************************/
"""
"""
# Spline Interpolation
# Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#appendix-c-spline-interpolation
"""


class GLTFCubicSplineInterpolant(Interpolant):
    def __init__(self, parameterPositions, sampleValues, sampleSize, resultBuffer):
        super().__init__(parameterPositions, sampleValues, sampleSize, resultBuffer)

    def interpolate_(self, i1, t0, t, t1):
        result = self.resultBuffer
        values = self.sampleValues
        stride = self.valueSize

        stride2 = stride * 2
        stride3 = stride * 3

        td = t1 - t0

        p = (t - t0) / td
        pp = p * p
        ppp = pp * p

        offset1 = i1 * stride3
        offset0 = offset1 - stride3

        s0 = 2 * ppp - 3 * pp + 1
        s1 = ppp - 2 * pp + p
        s2 = - 2 * ppp + 3 * pp
        s3 = ppp - pp

        # Layout of keyframe output values for CUBICSPLINE animations:
        #   [inTangent_1, splineVertex_1, outTangent_1, inTangent_2, splineVertex_2, ...]
        for i in range(stride - 1):
            p0 = values[offset0 + i + stride]            # splineVertex_k
            m0 = values[offset0 + i + stride2] * td    # outTangent_k * (t_k+1 - t_k)
            p1 = values[offset1 + i + stride]            # splineVertex_k+1
            m1 = values[offset1 + i] * td; # inTangent_k+1 * (t_k+1 - t_k)

            result[i] = s0 * p0 + s1 * m0 + s2 * p1 + s3 * m1

        return result


"""
/*********************************/
/********** INTERNALS ************/
/*********************************/
"""
# CONSTANTS */


_WEBGL_CONSTANTS = {
    'FLOAT': 5126,
    #'FLOAT_MAT2': 35674,
    'FLOAT_MAT3': 35675,
    'FLOAT_MAT4': 35676,
    'FLOAT_VEC2': 35664,
    'FLOAT_VEC3': 35665,
    'FLOAT_VEC4': 35666,
    'LINEAR': 9729,
    'REPEAT': 10497,
    'SAMPLER_2D': 35678,
    'POINTS': 0,
    'LINES': 1,
    'LINE_LOOP': 2,
    'LINE_STRIP': 3,
    'TRIANGLES': 4,
    'TRIANGLE_STRIP': 5,
    'TRIANGLE_FAN': 6,
    'UNSIGNED_BYTE': 5121,
    'UNSIGNED_SHORT': 5123
}

_WEBGL_TYPE = {
    5126: Number,
    #35674: THREE.Matrix2,
    35675: THREE.Matrix3,
    35676: THREE.Matrix4,
    35664: THREE.Vector2,
    35665: THREE.Vector3,
    35666: THREE.Vector4,
    35678: THREE.Texture
}

_WEBGL_COMPONENT_TYPES = {
    5120: Int8Array,
    5121: Uint8Array,
    5122: Int16Array,
    5123: Uint16Array,
    5125: Uint32Array,
    5126: Float32Array
}

_WEBGL_COMPONENT_TYPES_bytes = {
    5120: 1,
    5121: 1,
    5122: 2,
    5123: 2,
    5125: 4,
    5126: 4
}

_WEBGL_FILTERS = {
    9728: THREE.NearestFilter,
    9729: THREE.LinearFilter,
    9984: THREE.NearestMipMapNearestFilter,
    9985: THREE.LinearMipMapNearestFilter,
    9986: THREE.NearestMipMapLinearFilter,
    9987: THREE.LinearMipMapLinearFilter
}

_WEBGL_WRAPPINGS = {
    33071: THREE.ClampToEdgeWrapping,
    33648: THREE.MirroredRepeatWrapping,
    10497: THREE.RepeatWrapping
}

_WEBGL_SIDES = {
    1028: THREE.BackSide, # Culling front
    1029: THREE.FrontSide # Culling back
    ##1032: THREE.NoSide   # Culling front and back, what to do?
}

_WEBGL_DEPTH_FUNCS = {
    512: THREE.NeverDepth,
    513: THREE.LessDepth,
    514: THREE.EqualDepth,
    515: THREE.LessEqualDepth,
    516: THREE.GreaterEqualDepth,
    517: THREE.NotEqualDepth,
    518: THREE.GreaterEqualDepth,
    519: THREE.AlwaysDepth
}

_WEBGL_BLEND_EQUATIONS = {
    32774: THREE.AddEquation,
    32778: THREE.SubtractEquation,
    32779: THREE.ReverseSubtractEquation
}

_WEBGL_BLEND_FUNCS = {
    0: THREE.ZeroFactor,
    1: THREE.OneFactor,
    768: THREE.SrcColorFactor,
    769: THREE.OneMinusSrcColorFactor,
    770: THREE.SrcAlphaFactor,
    771: THREE.OneMinusSrcAlphaFactor,
    772: THREE.DstAlphaFactor,
    773: THREE.OneMinusDstAlphaFactor,
    774: THREE.DstColorFactor,
    775: THREE.OneMinusDstColorFactor,
    776: THREE.SrcAlphaSaturateFactor
    # The followings are not supported by Three.js yet
    #32769: CONSTANT_COLOR,
    #32770: ONE_MINUS_CONSTANT_COLOR,
    #32771: CONSTANT_ALPHA,
    #32772: ONE_MINUS_CONSTANT_COLOR
}

_WEBGL_TYPE_SIZES = {
    'SCALAR': 1,
    'VEC2': 2,
    'VEC3': 3,
    'VEC4': 4,
    'MAT2': 4,
    'MAT3': 9,
    'MAT4': 16
}

_ATTRIBUTES = {
    'POSITION': 'position',
    'NORMAL': 'normal',
    'TEXCOORD_0': 'uv',
    'TEXCOORD0': 'uv', # deprecated
    'TEXCOORD': 'uv', # deprecated
    'TEXCOORD_1': 'uv2',
    'COLOR_0': 'color',
    'COLOR0': 'color', # deprecated
    'COLOR': 'color', # deprecated
    'WEIGHTS_0': 'skinWeight',
    'WEIGHT': 'skinWeight', # deprecated
    'JOINTS_0': 'skinIndex',
    'JOINT': 'skinIndex' # deprecated
}

_PATH_PROPERTIES = {
    'scale': 'scale',
    'translation': 'position',
    'rotation': 'quaternion',
    'weights': 'morphTargetInfluences'
}

_INTERPOLATION = {
    'CUBICSPLINE': THREE.InterpolateSmooth, # We use custom interpolation GLTFCubicSplineInterpolation for CUBICSPLINE.
                                          # KeyframeTrack.optimize() can't handle glTF Cubic Spline output values layout,
                                          # using THREE.InterpolateSmooth for KeyframeTrack instantiation to prevent optimization.
                                          # See KeyframeTrack.optimize() for the detail.
    'LINEAR': THREE.InterpolateLinear,
    'STEP': THREE.InterpolateDiscrete
}

_STATES_ENABLES = {
    2884: 'CULL_FACE',
    2929: 'DEPTH_TEST',
    3042: 'BLEND',
    3089: 'SCISSOR_TEST',
    32823: 'POLYGON_OFFSET_FILL',
    32926: 'SAMPLE_ALPHA_TO_COVERAGE'
}

_ALPHA_MODES = {
    'OPAQUE': 'OPAQUE',
    'MASK': 'MASK',
    'BLEND': 'BLEND'
}

"""
/* UTILITY FUNCTIONS */
"""


def resolveURL(url, path):
    # Invalid URL
    if not isinstance(url, str) or url == '':
        return ''

    # Relative URL
    return path + url


"""
 * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#default-material
"""


def createDefaultMaterial():
    return THREE.MeshStandardMaterial({
        'color': 0xFFFFFF,
        'emissive': 0x000000,
        'metalness': 1,
        'roughness': 1,
        'transparent': False,
        'depthTest': True,
        'side': THREE.FrontSide
    })


def addUnknownExtensionsToUserData(knownExtensions, object, objectDef):
    # Add unknown glTF extensions to an object's userData.

    ext = objectDef['extensions'] if 'extensions' in objectDef else []

    for name in ext:
        if name in knownExtensions:
            object['userData']['gltfExtensions'] = object['userData']['gltfExtensions'] or {}
            object['userData']['gltfExtensions'][name] = ext[name]


"""
 * @param {THREE.Object3D|THREE.Material|THREE.BufferGeometry} object
 * @param {GLTF.definition} def
"""


def assignExtrasToUserData(obj, gltfDef):
    if 'extras' in gltfDef:
        if isinstance(gltfDef.extras, object):
            object.userData = gltfDef['extras']

        else:
            print('THREE.GLTFLoader: Ignoring primitive type .extras, ' + gltfDef.extras)


"""
 * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#morph-targets
 *
 * @param {THREE.BufferGeometry} geometry
 * @param {Array<GLTF.Target>} targets
 * @param {Array<THREE.BufferAttribute>} accessors
"""


def addMorphTargets(geometry, targets, accessors):
    hasMorphPosition = False
    hasMorphNormal = False

    for i in range(len(targets)):
        target = targets[i]

        if target.POSITION is not None:
            hasMorphPosition = True
        if target.NORMAL is not None:
            hasMorphNormal = True

        if hasMorphPosition and hasMorphNormal:
            break

    if not hasMorphPosition and not hasMorphNormal:
        return

    morphPositions = []
    morphNormals = []

    for i in range(len(targets)):
        target = targets[i]
        attributeName = 'morphTarget%d' % i

        if hasMorphPosition:
            # Three.js morph position is absolute value. The formula is
            #   basePosition
            #     + weight0 * (morphPosition0 - basePosition)
            #     + weight1 * (morphPosition1 - basePosition)
            #     ...
            # while the glTF one is relative
            #   basePosition
            #     + weight0 * glTFmorphPosition0
            #     + weight1 * glTFmorphPosition1
            #     ...
            # then we need to convert from relative to absolute here.

            if target.POSITION is not None:
                # Cloning not to pollute original accessor
                positionAttribute = cloneBufferAttribute(accessors[target.POSITION])
                positionAttribute.name = attributeName

                position = geometry.attributes.position

                for j in range(positionAttribute.count):
                    positionAttribute.setXYZ(
                        j,
                        positionAttribute.getX(j) + position.getX(j),
                        positionAttribute.getY(j) + position.getY(j),
                        positionAttribute.getZ(j) + position.getZ(j)
                    )

            else:
                positionAttribute = geometry.attributes.position

            morphPositions.append(positionAttribute)

        if hasMorphNormal:
            # see target.POSITION's comment

            if target.NORMAL is not None:
                normalAttribute = cloneBufferAttribute(accessors[target.NORMAL])
                normalAttribute.name = attributeName

                normal = geometry.attributes.normal

                for j in range(normalAttribute.count):
                    normalAttribute.setXYZ(
                        j,
                        normalAttribute.getX(j) + normal.getX(j),
                        normalAttribute.getY(j) + normal.getY(j),
                        normalAttribute.getZ(j) + normal.getZ(j)
                    )

            else:
                normalAttribute = geometry.attributes.normal

            morphNormals.append(normalAttribute)

    if hasMorphPosition:
        geometry.morphAttributes.position = morphPositions
    if hasMorphNormal:
        geometry.morphAttributes.normal = morphNormals


"""
* @param {THREE.Mesh} mesh
* @param {GLTF.Mesh} meshDef
"""


def updateMorphTargets(mesh, meshDef):
    mesh.updateMorphTargets()

    if meshDef.weights is not None:
        for i in range(len(meshDef.weights)):
            mesh.morphTargetInfluences[i] = meshDef.weights[i]

    # .extras has user-defined data, so check that .extras.targetNames is an array.
    if meshDef.extras and Array.isArray(meshDef.extras.targetNames):
        targetNames = meshDef.extras.targetNames

        if mesh.morphTargetInfluences.length == len(targetNames):
            mesh.morphTargetDictionary = {}

            for i in range(len(targetNames)):
                mesh.morphTargetDictionary[targetNames[i]] = i

        else:
            print('THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.')


def isPrimitiveEqual(a, b):
    if a.indices != b.indices :
        return False

    return isObjectEqual(a.attributes, b.attributes)


def isObjectEqual(a, b):
    if len(a.__dict__) != len(b.__dict__):
        return False

    for key in a.__dict__:
        if a.__dict__[key] != b.__dict__[key]:
            return False

    return True


def isArrayEqual(a, b):
    if len(a) != len(b):
        return False

    for i in range(len(a)):
        if a[i] != b[i]:
            return False

    return True


def getCachedGeometry(cache, newPrimitive):
    for i in range(len(cache)):
        cached = cache[i]

        if isPrimitiveEqual(cached.primitive, newPrimitive):
            return cached.promise

    return None


def getCachedCombinedGeometry(cache, geometries):
    for i in range(len(cache)):
        cached = cache[i]

        if isArrayEqual(geometries, cached.baseGeometries):
            return cached.geometry

    return None


def getCachedMultiPassGeometry(cache, geometry, primitives):
    for i in range(len(cache)):
        cached = cache[i]

        if geometry == cached.baseGeometry and isArrayEqual(primitives, cached.primitives):
            return cached.geometry

    return None


def cloneBufferAttribute(attribute):
    if attribute.isInterleavedBufferAttribute:
        count = attribute.count
        itemSize = attribute.itemSize
        array = attribute.array.slice(0, count * itemSize)

        for i in range(count):
            array[i] = attribute.getX(i)
            if itemSize >= 2:
                array[i + 1] = attribute.getY(i)
            if itemSize >= 3:
                array[i + 2] = attribute.getZ(i)
            if itemSize >= 4:
                array[i + 3] = attribute.getW(i)

        return THREE.BufferAttribute(array, itemSize, attribute.normalized)

    return attribute.clone()


"""
 * Checks if we can build a single Mesh with MultiMaterial from multiple primitives.
 * Returns True if all primitives use the same attributes/morphAttributes/mode
 * and also have index. Otherwise returns False.
 *
 * @param {Array<GLTF.Primitive>} primitives
 * @return {Boolean}
"""


def isMultiPassGeometry(primitives):
    if len(primitives) < 2:
        return False

    primitive0 = primitives[0]
    targets0 = primitive0.targets or []

    if primitive0.indices is None:
        return False

    for i in range(len(primitives)):
        primitive = primitives[i]

        if primitive0.mode != primitive.mode:
            return False
        if primitive.indices is None:
            return False
        if not isObjectEqual(primitive0.attributes, primitive.attributes):
            return False

        targets = primitive.targets or []

        if len(targets0) != len(targets):
            return False

        for j in range(len(targets0)):
            if not isObjectEqual(targets0[j], targets[j]):
                return False

    return True


"""
/* GLTF PARSER */
"""
class GLTFParser:
    def __init__(self, json, extensions, options):
        self.json = json or {}
        self.extensions = extensions or {}
        self.options = options or {}

        # loader object cache
        self.cache = GLTFRegistry()

        # BufferGeometry caching
        self.primitiveCache = []
        self.multiplePrimitivesCache = []
        self.multiPassGeometryCache = []

        self.textureLoader = TextureLoader(self.options['manager'])
        self.textureLoader.setCrossOrigin(self.options['crossOrigin'])

        self.fileLoader = FileLoader(self.options['manager'])
        self.fileLoader.setResponseType('arraybuffer')

    def parse(self, onLoad, onError):
        json = self.json

        # Clear the loader cache
        self.cache.removeAll()

        # Mark the special nodes/meshes in json for efficient parse
        self.markDefs()

        # Fire the callback on complete
        dependencies = self.getMultiDependencies([
            'scene',
            'animation',
            'camera'
        ])

        scenes = dependencies['scenes'] if 'scenes' in dependencies else []
        scene = scenes[json['scene'] if 'scene' in json else 0]
        animations = dependencies['animations'] if 'animations' in dependencies else []
        cameras = dependencies['cameras'] if 'cameras' in dependencies else []

        onLoad(scene, scenes, cameras, animations, json)

    def markDefs(self):
        """
         * Marks the special nodes/meshes in json for efficient parse.
        """
        json = self.json
        nodeDefs = json['nodes'] if 'nodes' in json else []
        skinDefs = json['skins'] if 'skins' in json else []
        meshDefs = json['meshes'] if 'meshes' in json else []

        meshReferences = {}
        meshUses = {}

        # Nothing in the node definition indicates whether it is a Bone or an
        # Object3D. Use the skins' joint references to mark bones.
        for skinIndex in range(len(skinDefs)):
            joints = skinDefs[skinIndex].joints

            for i in range(len(joints)):
                nodeDefs[joints[i]].isBone = True

        # Meshes can (and should) be reused by multiple nodes in a glTF asset. To
        # avoid having more than one THREE.Mesh with the same name, count
        # references and rename instances below.
        #
        # Example: CesiumMilkTruck sample model reuses "Wheel" meshes.
        for nodeIndex in range(len(nodeDefs)):
            nodeDef = nodeDefs[nodeIndex]

            if 'mesh' in nodeDef:
                nd = nodeDef['mesh']
                if nd not in meshReferences:
                    meshReferences[nd] = 0
                    meshUses[nd] = 0

                meshReferences[nd] += 1

                # Nothing in the mesh definition indicates whether it is
                # a SkinnedMesh or Mesh. Use the node's mesh reference
                # to mark SkinnedMesh if node has skin.
                if 'skin' in nodeDef:
                    meshDefs[nd].isSkinnedMesh = True

        json['meshReferences'] = meshReferences
        json['meshUses'] = meshUses


    def getDependency(self, type, index):
        """
         * Requests the specified dependency asynchronously, with caching.
         * @param {string} type
         * @param {number} index
         * @return {Promise<Object>}
        """
        cacheKey = '%s:%d' % (type, index)
        dependency = self.cache.get(cacheKey)

        if not dependency:
            if type == 'scene':
                    dependency = self.loadScene(index)

            elif type == 'node':
                    dependency = self.loadNode(index)

            elif type == 'mesh':
                    dependency = self.loadMesh(index)

            elif type == 'accessor':
                    dependency = self.loadAccessor(index)

            elif type == 'bufferView':
                    dependency = self.loadBufferView(index)

            elif type == 'buffer':
                    dependency = self.loadBuffer(index)

            elif type == 'material':
                    dependency = self.loadMaterial(index)

            elif type == 'texture':
                    dependency = self.loadTexture(index)

            elif type == 'skin':
                    dependency = self.loadSkin(index)

            elif type == 'animation':
                    dependency = self.loadAnimation(index)

            elif type == 'camera':
                    dependency = self.loadCamera(index)

            else:
                    raise RuntimeError('Unknown type: ' + type)

            self.cache.add(cacheKey, dependency)

        return dependency

    def getDependencies(self, type):
        """
         * Requests all dependencies of the specified type asynchronously, with caching.
         * @param {string} type
         * @return {Promise<Array<Object>>}
        """
        dependencies = self.cache.get(type)

        if not dependencies:
            parser = self
            k = type + ('es' if type == 'mesh' else 's')
            defs = self.json[k] if k in self.json else []

            dependencies = []
            index = 0
            for d in defs:
                dependencies.append(parser.getDependency(type, index))
                index += 1

            self.cache.add(type, dependencies)

        return dependencies

    def getMultiDependencies(self, types):
        """
         * Requests all multiple dependencies of the specified types asynchronously, with caching.
         * @param {Array<string>} types
         * @return {Promise<Object<Array<Object>>>}
        """
        results = {}
        pendings = []

        for i in range(len(types)):
            type = types[i]
            values = self.getDependencies(type)

            for v in values:
                key = type + ('es' if type == 'mesh' else 's')
                if key in results:
                    results[key].append(v)
                else:
                    results[key] = [v]

        return results

    def loadBuffer(self,bufferIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#buffers-and-buffer-views
         * @param {number} bufferIndex
         * @return {Promise<ArrayBuffer>}
        """

        bufferDef = self.json['buffers'][bufferIndex]
        loader = self.fileLoader

        if 'type' in bufferDef and bufferDef['type'] != 'arraybuffer':
            raise RuntimeError('THREE.GLTFLoader: ' + bufferDef.type + ' buffer type is not supported.')

        # If present, GLB container is required to be the first buffer.
        if 'uri' not in bufferDef and bufferIndex == 0:
            return self.extensions[_.KHR_BINARY_GLTF].body

        options = self.options

        d = loader.load(resolveURL(bufferDef['uri'], options['path']), None, None)
        if d is None:
            raise RuntimeError('THREE.GLTFLoader: Failed to load buffer "' + bufferDef.uri + '".')

        return d

    def loadBufferView(self,bufferViewIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#buffers-and-buffer-views
         * @param {number} bufferViewIndex
         * @return {Promise<ArrayBuffer>}
        """
        bufferViewDef = self.json['bufferViews'][bufferViewIndex]

        buffer = self.getDependency('buffer', bufferViewDef['buffer'])
        byteLength = bufferViewDef['byteLength'] if 'byteLength' in bufferViewDef else 0
        byteOffset = bufferViewDef['byteOffset'] if 'byteOffset' in bufferViewDef else 0
        return buffer[byteOffset:byteOffset + byteLength]

    def loadAccessor(self, accessorIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#accessors
         * @param {number} accessorIndex
         * @return {Promise<THREE.BufferAttribute|THREE.InterleavedBufferAttribute>}
        """
        parser = self
        json = self.json

        accessorDef = json['accessors'][accessorIndex]

        if 'bufferView' not in accessorDef and 'sparse' not in accessorDef is None:
            # Ignore empty accessors, which may be used to declare runtime
            # information about attributes coming from another source (e.g. Draco
            # compression extension).
            return None

        bufferViews = []

        if 'bufferView' in accessorDef:
            bufferViews.append(self.getDependency('bufferView', accessorDef['bufferView']))

        else:
            bufferViews.append(None)

        if 'sparse' in accessorDef:
            bufferViews.append(self.getDependency('bufferView', accessorDef['sparse']['indices']['bufferView']))
            bufferViews.append(self.getDependency('bufferView', accessorDef['sparse']['values']['bufferView']))

        bufferAttributes = []

        bufferView = bufferViews[0]

        itemSize = _WEBGL_TYPE_SIZES[accessorDef['type']]
        TypedArray = _WEBGL_COMPONENT_TYPES[accessorDef['componentType']]

        # For VEC3: itemSize is 3, elementBytes is 4, itemBytes is 12.
        elementBytes = _WEBGL_COMPONENT_TYPES_bytes[accessorDef['componentType']]
        itemBytes = elementBytes * itemSize
        byteOffset = accessorDef['byteOffset'] if 'byteOffset' in accessorDef else 0

        bv = json['bufferViews'][accessorDef['bufferView']]
        byteStride = bv['byteStride'] if 'byteStride' in bv else None
        normalized = accessorDef['normalized'] if 'normalized' in accessorDef else False

        # The buffer is not interleaved if the stride is the item size in bytes.
        if byteStride and byteStride != itemBytes:
            ibCacheKey = 'InterleavedBuffer:' + accessorDef['bufferView'] + ':' + accessorDef['componentType']
            ib = parser.cache.get(ibCacheKey)

            if not ib:
                # Use the full buffer if it's interleaved.
                array = TypedArray(bufferView)

                # Integer parameters to IB/IBA are in array elements, not bytes.
                ib = THREE.InterleavedBuffer(array, byteStride / elementBytes)

                parser.cache.add(ibCacheKey, ib)

            bufferAttribute = THREE.InterleavedBufferAttribute(ib, itemSize, byteOffset / elementBytes, normalized)

        else:
            if bufferView is None:
                array = TypedArray(accessorDef['count'] * itemSize)

            else:
                array = TypedArray(bufferView, byteOffset, accessorDef['count'] * itemSize)

            bufferAttribute = THREE.BufferAttribute(array, itemSize, normalized)

        # https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#sparse-accessors
        if 'sparse' in accessorDef:
            itemSizeIndices = _WEBGL_TYPE_SIZES['SCALAR']
            TypedArrayIndices = _WEBGL_COMPONENT_TYPES[accessorDef['sparse']['indices']['componentType']]

            byteOffsetIndices = accessorDef['sparse']['indices']['byteOffset'] or 0
            byteOffsetValues = accessorDef['sparse']['values']['byteOffset'] or 0

            sparseIndices = TypedArrayIndices(bufferViews[1], byteOffsetIndices,
                                              accessorDef['sparse']['count'] * itemSizeIndices)
            sparseValues = TypedArray(bufferViews[2], byteOffsetValues, accessorDef['sparse']['count'] * itemSize)

            if bufferView is None:
                # Avoid modifying the original ArrayBuffer, if the bufferView wasn't initialized with zeroes.
                bufferAttribute.setArray(bufferAttribute.array[:])

            for i in range(len(sparseIndices)):
                index = sparseIndices[i]

                bufferAttribute.setX(index, sparseValues[i * itemSize])
                if itemSize >= 2:
                    bufferAttribute.setY(index, sparseValues[i * itemSize + 1])
                if itemSize >= 3:
                    bufferAttribute.setZ(index, sparseValues[i * itemSize + 2])
                if itemSize >= 4:
                    bufferAttribute.setW(index, sparseValues[i * itemSize + 3])
                if itemSize >= 5:
                    raise RuntimeError('THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.')

        return bufferAttribute

    def loadTexture(self, textureIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#textures
         * @param {number} textureIndex
         * @return {Promise<THREE.Texture>}
        """
        parser = self
        json = self.json
        options = self.options
        textureLoader = self.textureLoader

        textureDef = json['textures'][textureIndex]

        textureExtensions = textureDef['extensions'] if 'extensions' in textureDef else {}

        if _MSFT_TEXTURE_DDS in textureExtensions:
            source = json['images'][ textureExtensions[_MSFT_TEXTURE_DDS]]['source']

        else:
            source = json['images'][textureDef['source']]

        sourceURI = source['uri']
        isObjectURL = False

        if 'bufferView' in source:
            # Load binary image data from bufferView, if provided.

            dependencies = parser.getDependency('bufferView', source['bufferView'])
            for bufferView in dependencies:
                isObjectURL = True
                blob = Blob([bufferView], { type: source.mimeType })
                sourceURI = URL.createObjectURL(blob)
                raise RuntimeError(sourceURI)

        # Load Texture resource.
        loader = THREE.Loader.Handlers.get(sourceURI)

        if not loader:
            loader = parser.extensions[_MSFT_TEXTURE_DDS].ddsLoader if _MSFT_TEXTURE_DDS in textureExtensions else textureLoader

        texture = loader.load(resolveURL(sourceURI, options['path']), None, None, None)

        # Clean up resources and configure Texture.

        texture.flipY = False
        texture.flip_image()

        if 'name' in textureDef:
            texture.name = textureDef['name']

        samplers = json['samplers'] if 'samplers' in json else {}
        sampler = samplers[textureDef['sampler']] if 'sampler' in textureDef else {}

        texture.magFilter = _WEBGL_FILTERS[sampler['magFilter']] if 'magFilter' in sampler else THREE.LinearFilter
        texture.minFilter = _WEBGL_FILTERS[sampler['minFilter']] if 'minFilter' in sampler else THREE.LinearMipMapLinearFilter
        texture.wrapS = _WEBGL_WRAPPINGS[sampler['wrapS']] if 'wrapS' in sampler else THREE.RepeatWrapping
        texture.wrapT = _WEBGL_WRAPPINGS[sampler['wrapT']] if 'wrapT' in sampler else THREE.RepeatWrapping

        return texture

    def assignTexture(self, materialParams, textureName, textureIndex):
        """
         * Asynchronously assigns a texture to the given material parameters.
         * @param {Object} materialParams
         * @param {string} textureName
         * @param {number} textureIndex
         * @return {Promise}
        """
        texture = self.getDependency('texture', textureIndex)
        materialParams[textureName] = texture

    def loadMaterial(self, materialIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#materials
         * @param {number} materialIndex
         * @return {Promise<THREE.Material>}
        """
        parser = self
        json = self.json
        extensions = self.extensions
        materialDef = json['materials'][materialIndex]

        materialParams = {}
        materialExtensions = materialDef['extensions'] if 'extensions' in materialDef else {}

        pending = []

        if _KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS in materialExtensions:
            sgExtension = extensions[_KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS]
            materialType = sgExtension.getMaterialType(materialDef)
            pending.append(sgExtension.extendParams(materialParams, materialDef, parser))

        elif _KHR_MATERIALS_UNLIT in materialExtensions:
            kmuExtension = extensions[_KHR_MATERIALS_UNLIT]
            materialType = kmuExtension.getMaterialType(materialDef)
            pending.append(kmuExtension.extendParams(materialParams, materialDef, parser))

        else:
            # Specification:
            # https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#metallic-roughness-material

            materialType = THREE.MeshStandardMaterial

            metallicRoughness = materialDef['pbrMetallicRoughness'] if 'pbrMetallicRoughness' in materialDef else {}

            materialParams['color'] = THREE.Color(1.0, 1.0, 1.0)
            materialParams['opacity'] = 1.0

            if 'baseColorFactor' in metallicRoughness and isinstance(metallicRoughness['baseColorFactor'], list):
                array = metallicRoughness['baseColorFactor']

                materialParams['color'].fromArray(array)
                materialParams['opacity'] = array[3]

            if 'baseColorTexture' in metallicRoughness:
                parser.assignTexture(materialParams, 'map', metallicRoughness['baseColorTexture']['index'])

            materialParams['metalness'] = metallicRoughness['metallicFactor'] if 'metallicFactor' in metallicRoughness else 1.0
            materialParams['roughness'] = metallicRoughness['roughnessFactor'] if 'roughnessFactor' in metallicRoughness else 1.0

            if 'metallicRoughnessTexture' in metallicRoughness:
                textureIndex = metallicRoughness['metallicRoughnessTexture']['index']
                parser.assignTexture(materialParams, 'metalnessMap', textureIndex)
                parser.assignTexture(materialParams, 'roughnessMap', textureIndex)

        if 'doubleSided' in materialDef and materialDef['doubleSided'] is True:
            materialParams['side'] = THREE.DoubleSide

        alphaMode = materialDef['alphaMode'] if 'alphaMode' in materialDef else _ALPHA_MODES['OPAQUE']

        if alphaMode == _ALPHA_MODES['BLEND']:
            materialParams['transparent'] = True

        else:
            materialParams['transparent'] = False

            if alphaMode == _ALPHA_MODES['MASK']:
                materialParams['alphaTest'] = materialDef['alphaCutoff'] if 'alphaCutoff' in materialDef else 0.5

        if 'normalTexture' in materialDef and materialType != THREE.MeshBasicMaterial:
            parser.assignTexture(materialParams, 'normalMap', materialDef['normalTexture']['index'])

            materialParams['normalScale'] = THREE.Vector2(1, 1)

            if 'scale' in materialDef['normalTexture']:
                materialParams['normalScale'].set(materialDef['normalTexture']['scale'], materialDef['normalTexture']['scale'])

        if 'occlusionTexture' in materialDef and materialType != THREE.MeshBasicMaterial:
            parser.assignTexture(materialParams, 'aoMap', materialDef['occlusionTexture']['index'])

            if 'strength' in materialDef['occlusionTexture']:
                materialParams['aoMapIntensity'] = materialDef['occlusionTexture']['strength']

        if 'emissiveFactor' in materialDef and materialType != THREE.MeshBasicMaterial:
            materialParams['emissive'] = THREE.Color().fromArray(materialDef['emissiveFactor'])

        if 'emissiveTexture' in materialDef and materialType != THREE.MeshBasicMaterial:
            parser.assignTexture(materialParams, 'emissiveMap', materialDef['emissiveTexture']['index'])

        if materialType == THREE.ShaderMaterial:
            material = extensions[_KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS].createMaterial(materialParams)

        else:
            material = materialType(materialParams)

        if 'name' in materialDef:
            material.name = materialDef['name']

        # Normal map textures use OpenGL conventions:
        # https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#materialnormaltexture
        if material.normalScale:
            material.normalScale.y = - material.normalScale.y

        # baseColorTexture, emissiveTexture, and specularGlossinessTexture use sRGB encoding.
        if material.map:
            material.map.encoding = THREE.sRGBEncoding
        if material.emissiveMap:
            material.emissiveMap.encoding = THREE.sRGBEncoding
        if material.specularMap:
            material.specularMap.encoding = THREE.sRGBEncoding

        assignExtrasToUserData(material, materialDef)

        if 'extensions' in materialDef:
            addUnknownExtensionsToUserData(extensions, material, materialDef)

        return material

    @staticmethod
    def addPrimitiveAttributes(geometry, primitiveDef, accessors):
        """
         * @param  {THREE.BufferGeometry} geometry
         * @param  {GLTF.Primitive} primitiveDef
         * @param  {Array<THREE.BufferAttribute>} accessors
        """

        attributes = primitiveDef['attributes']

        for gltfAttributeName in attributes:
            threeAttributeName = _ATTRIBUTES[gltfAttributeName]
            bufferAttribute = accessors[attributes[gltfAttributeName]]

            # Skip attributes already provided by e.g. Draco extension.
            if not threeAttributeName:
                continue

            if threeAttributeName in geometry.attributes:
                if geometry.attributes[threeAttributeName] is not None:
                    continue

                geometry.attributes[threeAttributeName] = bufferAttribute

            else:
                geometry.addAttribute(threeAttributeName, bufferAttribute)

        if 'indices' in primitiveDef and not geometry.index:
            geometry.setIndex(accessors[primitiveDef['indices']])

        if 'targets' in primitiveDef:
            addMorphTargets(geometry, primitiveDef['targets'], accessors)

        assignExtrasToUserData(geometry, primitiveDef)

    def loadGeometries(self, primitives):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#geometry
         *
         * Creates BufferGeometries from primitives.
         * If we can build a single BufferGeometry with .groups from multiple primitives, returns one BufferGeometry.
         * Otherwise, returns BufferGeometries without .groups as many as primitives.
         *
         * @param {Array<Object>} primitives
         * @return {Promise<Array<THREE.BufferGeometry>>}
        """
        parser = self
        extensions = self.extensions
        cache = self.primitiveCache

        isMultiPass = isMultiPassGeometry(primitives)

        if isMultiPass:
            originalPrimitives = primitives     # save original primitives and use later

            # We build a single BufferGeometry with .groups from multiple primitives
            # because all primitives share the same attributes/morph/mode and have indices.

            primitives = [primitives[0]]

            # Sets .groups and combined indices to a geometry later in self method.

        accessors = self.getDependencies('accessor')
        geometries = []

        for i in range(len(primitives)):
            primitive = primitives[i]

            # See if we've already created self geometry
            cached = getCachedGeometry(cache, primitive)

            if cached:
                # Use the cached geometry if it exists
                geometries.append(cached)

            elif 'extensions' in primitive and '_KHR_DRACO_MESH_COMPRESSION' in primitive['extensions']:
                # Use DRACO geometry if available
                geometries1 = extensions[_KHR_DRACO_MESH_COMPRESSION].decodePrimitive(primitive, parser)
                for geometry in geometries1:
                    self.addPrimitiveAttributes(geometry, primitive, accessors)

                cache.append({ 'primitive': primitive, 'promise': geometries })

                geometries.append(geometries1)

            else:
                # Otherwise create a geometry
                geometry = THREE.BufferGeometry()

                self.addPrimitiveAttributes(geometry, primitive, accessors)

                # Cache self geometry
                cache.append({ 'primitive': primitive, 'promise': geometry })

                geometries.append(geometry)

        if isMultiPass:
            baseGeometry = geometries[0]

            # See if we've already created self combined geometry
            cache = parser.multiPassGeometryCache
            cached = getCachedMultiPassGeometry(cache, baseGeometry, originalPrimitives)

            if cached is not None:
                return [cached.geometry]

            # Cloning geometry because of index override.
            # Attributes can be reused so cloning by myself here.
            geometry = THREE.BufferGeometry()

            geometry.name = baseGeometry.name
            geometry.userData = baseGeometry.userData

            for key in baseGeometry.attributes:
                geometry.addAttribute(key, baseGeometry.attributes[key])
            for key in baseGeometry.morphAttributes:
                geometry.morphAttributes[key] = baseGeometry.morphAttributes[key]

            indices = []
            offset = 0

            for i in range(len(originalPrimitives)):
                accessor = accessors[originalPrimitives[i].indices]

                for j in range(accessor.count):
                    indices.append(accessor.array[j])

                geometry.addGroup(offset, accessor.count, i)

                offset += accessor.count

            geometry.setIndex(indices)

            cache.append({ geometry: geometry, baseGeometry: baseGeometry, primitives: originalPrimitives })

            return [geometry]

        elif len(geometries) > 1 and THREE.BufferGeometryUtils is not None:
            # Tries to merge geometries with BufferGeometryUtils if possible

            for i in range(1, len(primitives)):
                # can't merge if draw mode is different
                if primitives[0].mode != primitives[i].mode:
                    return geometries

            # See if we've already created self combined geometry
            cache = parser.multiplePrimitivesCache
            cached = getCachedCombinedGeometry(cache, geometries)

            if cached:
                if cached.geometry is not None:
                    return [cached.geometry]

            else:
                geometry = THREE.BufferGeometryUtils.mergeBufferGeometries(geometries, True)

                cache.append({ 'geometry': geometry, 'baseGeometries': geometries })

                if geometry is not None:
                    return [geometry]

        return geometries

    def loadMesh(self, meshIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/blob/master/specification/2.0/README.md#meshes
         * @param {number} meshIndex
         * @return {Promise<THREE.Group|THREE.Mesh|THREE.SkinnedMesh>}
        """
        json = self.json
        extensions = self.extensions

        meshDef = json['meshes'][meshIndex]

        dependencies = self.getMultiDependencies([
            'accessor',
            'material'

        ])

        primitives = meshDef['primitives']
        originalMaterials = []

        for i in range(len(primitives)):
            material = createDefaultMaterial() if 'material' not in primitives[i] else dependencies['materials'][ primitives[i]['material'] ]
            originalMaterials.append(material)

        geometries = self.loadGeometries(primitives)
        isMultiMaterial = len(geometries) == 1 and len(geometries[0].groups) > 0

        meshes = []

        for i in range(len(geometries)):
            geometry = geometries[i]
            primitive = primitives[i]

            # 1. create Mesh

            material = originalMaterials if isMultiMaterial else originalMaterials[i]

            if 'mode' not in primitive or \
                primitive['mode'] == _WEBGL_CONSTANTS['TRIANGLES'] or \
                primitive['mode'] == _WEBGL_CONSTANTS['TRIANGLE_STRIP'] or \
                primitive['mode'] == _WEBGL_CONSTANTS['TRIANGLE_FAN']:

                # .isSkinnedMesh isn't in glTF spec. See .markDefs()
                mesh = SkinnedMesh(geometry, material) if 'isSkinnedMesh' in meshDef else THREE.Mesh(geometry, material)

                if 'mode' in primitive:
                    if primitive['mode'] == _WEBGL_CONSTANTS['TRIANGLE_STRIP']:
                        mesh.drawMode = THREE.TriangleStripDrawMode

                    elif primitive['mode'] == _WEBGL_CONSTANTS['TRIANGLE_FAN']:
                        mesh.drawMode = THREE.TriangleFanDrawMode

            elif primitive['mode'] == _WEBGL_CONSTANTS['LINES']:
                mesh = THREE.LineSegments(geometry, material)

            elif primitive['mode'] == _WEBGL_CONSTANTS['LINE_STRIP']:
                mesh = THREE.Line(geometry, material)

            elif primitive['mode'] == _WEBGL_CONSTANTS['LINE_LOOP']:
                mesh = THREE.LineLoop(geometry, material)

            elif primitive['mode'] == _WEBGL_CONSTANTS['POINTS']:
                mesh = THREE.Points(geometry, material)

            else:
                raise RuntimeError('THREE.GLTFLoader: Primitive mode unsupported: ' + primitive.mode)

            if not mesh.geometry.morphAttributes.empty():
                updateMorphTargets(mesh, meshDef)

            mesh.name = meshDef['name'] if 'name' in meshDef else ('mesh_%d' % meshIndex)

            if len(geometries) > 1:
                mesh.name += '_%d' % i

            assignExtrasToUserData(mesh, meshDef)

            meshes.append(mesh)

            # 2. update Material depending on Mesh and BufferGeometry

            materials = mesh.material if isMultiMaterial else [mesh.material]

            useVertexColors = geometry.attributes.colors is not None
            useFlatShading = geometry.attributes.normal is None
            useSkinning = mesh.my_class(isSkinnedMesh)
            useMorphTargets = not geometry.morphAttributes.empty()
            useMorphNormals = useMorphTargets and len(geometry.morphAttributes.normal) > 0

            for j in range(len(materials)):
                material = materials[j]

                if mesh.my_class(isPoints):
                    cacheKey = 'PointsMaterial:%s' % material.uuid

                    pointsMaterial = self.cache.get(cacheKey)

                    if not pointsMaterial:
                        pointsMaterial = THREE.PointsMaterial()
                        pointsMaterial.copy(material)
                        pointsMaterial.color.copy(material.color)
                        pointsMaterial.map = material.map
                        pointsMaterial.lights = False     # PointsMaterial doesn't support lights yet

                        self.cache.add(cacheKey, pointsMaterial)

                    material = pointsMaterial

                elif mesh.my_class(isLine):
                    cacheKey = 'LineBasicMaterial:%s' % material.uuid

                    lineMaterial = self.cache.get(cacheKey)

                    if not lineMaterial:
                        lineMaterial = THREE.LineBasicMaterial()
                        THREE.Material.prototype.copy.call(lineMaterial, material)
                        lineMaterial.color.copy(material.color)
                        lineMaterial.lights = False     # LineBasicMaterial doesn't support lights yet

                        self.cache.add(cacheKey, lineMaterial)

                    material = lineMaterial

                # Clone the material if it will be modified
                if useVertexColors or useFlatShading or useSkinning or useMorphTargets:
                    cacheKey = 'ClonedMaterial:' + material.uuid + ':'

                    if material.isGLTFSpecularGlossinessMaterial:
                        cacheKey += 'specular-glossiness:'
                    if useSkinning:
                        cacheKey += 'skinning:'
                    if useVertexColors:
                        cacheKey += 'vertex-colors:'
                    if useFlatShading:
                        cacheKey += 'flat-shading:'
                    if useMorphTargets:
                        cacheKey += 'morph-targets:'
                    if useMorphNormals:
                        cacheKey += 'morph-normals:'

                    cachedMaterial = self.cache.get(cacheKey)

                    if not cachedMaterial:
                        cachedMaterial = extensions[_KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS].cloneMaterial(material) if material.isGLTFSpecularGlossinessMaterial else  material.clone()

                        if useSkinning:
                            cachedMaterial.skinning = True
                        if useVertexColors:
                            cachedMaterial.vertexColors = THREE.VertexColors
                        if useFlatShading:
                            cachedMaterial.flatShading = True
                        if useMorphTargets:
                            cachedMaterial.morphTargets = True
                        if useMorphNormals:
                            cachedMaterial.morphNormals = True

                        self.cache.add(cacheKey, cachedMaterial)

                    material = cachedMaterial

                materials[j] = material

                # workarounds for mesh and geometry

                if material.aoMap and geometry.attributes.uv2 is None and geometry.attributes.uv is not None:
                    print('THREE.GLTFLoader: Duplicating UVs to support aoMap.')
                    geometry.addAttribute('uv2', THREE.BufferAttribute(geometry.attributes.uv.array, 2))

                if material.my_class(isGLTFSpecularGlossinessMaterial):
                    # for GLTFSpecularGlossinessMaterial(ShaderMaterial) uniforms runtime update
                    mesh.onBeforeRender = extensions[_KHR_MATERIALS_PBR_SPECULAR_GLOSSINESS].refreshUniforms

            mesh.material = materials if isMultiMaterial else materials[0]

        if len(meshes) == 1:
            return meshes[0]

        group = THREE.Group()

        for i in range(len(meshes)):
            group.add(meshes[i])

        return group

    def loadCamera(self,cameraIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#cameras
         * @param {number} cameraIndex
         * @return {Promise<THREE.Camera>}
        """
        cameraDef = self.json.cameras[cameraIndex]
        params = cameraDef[cameraDef.type]

        if not params:
            print('THREE.GLTFLoader: Missing camera parameters.')
            return

        if cameraDef.type == 'perspective':
            camera = THREE.PerspectiveCamera(radToDeg(params.yfov), params.aspectRatio or 1, params.znear or 1, params.zfar or 2e6)

        elif cameraDef.type == 'orthographic':
            camera = THREE.OrthographicCamera(params.xmag / - 2, params.xmag / 2, params.ymag / 2, params.ymag / - 2, params.znear, params.zfar)

        if cameraDef.name is not None:
            camera.name = cameraDef.name

        assignExtrasToUserData(camera, cameraDef)

        return camera

    def loadSkin(self,skinIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#skins
         * @param {number} skinIndex
         * @return {Promise<Object>}
        """
        skinDef = self.json.skins[skinIndex]

        skinEntry = { 'joints': skinDef.joints }

        if skinDef.inverseBindMatrices is None:
            return skinEntry

        accessor = self.getDependency('accessor', skinDef.inverseBindMatrices)
        skinEntry.inverseBindMatrices = accessor

        return skinEntry

    def loadAnimation(self,animationIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#animations
         * @param {number} animationIndex
         * @return {Promise<THREE.AnimationClip>}
        """
        json = self.json

        animationDef = self.json.animations[animationIndex]

        dependencies = self.getMultiDependencies([
            'accessor',
            'node'
        ])
        tracks = []

        for i in range(len(animationDef.channels)):
            channel = animationDef.channels[i]
            sampler = animationDef.samplers[channel.sampler]

            if sampler:
                target = channel.target
                name = target.node if target.node is not None else target.id         # NOTE: target.id is deprecated.
                input = animationDef.parameters[sampler.input] if animationDef.parameters is not None else sampler.input
                output = animationDef.parameters[sampler.output] if animationDef.parameters is not None else sampler.output

                inputAccessor = dependencies.accessors[input]
                outputAccessor = dependencies.accessors[output]

                node = dependencies.nodes[name]

                if node:
                    node.updateMatrix()
                    node.matrixAutoUpdate = True

                    p = _PATH_PROPERTIES[target.path]
                    if p == _PATH_PROPERTIES['weights']:
                            TypedKeyframeTrack = THREE.NumberKeyframeTrack

                    elif p == _PATH_PROPERTIES['rotation']:
                            TypedKeyframeTrack = THREE.QuaternionKeyframeTrack

                    else:
                            TypedKeyframeTrack = THREE.VectorKeyframeTrack

                    targetName = node.name if node.name else node.uuid

                    interpolation = INTERPOLATION[sampler.interpolation] if sampler.interpolation is not None else THREE.InterpolateLinear

                    targetNames = []

                    if _PATH_PROPERTIES[target.path] == _PATH_PROPERTIES['weights']:
                        # node can be THREE.Group here but
                        # PATH_PROPERTIES.weights(morphTargetInfluences) should be
                        # the property of a mesh object under group.
                        def func(obj):
                            if obj.my_class(isMesh) and hasattr(obj, 'morphTargetInfluences'):
                                targetNames.append(obj.name if obj.name else obj.uuid)

                        node.traverse(func)

                    else:
                        targetNames.append(targetName)

                    # KeyframeTrack.optimize() will modify given 'times' and 'values'
                    # buffers before creating a truncated copy to keep. Because buffers may
                    # be reused by other tracks, make copies here.
                    for j in range(len(targetNames)):
                        track = TypedKeyframeTrack(
                            targetNames[j] + '.' + _PATH_PROPERTIES[target.path],
                            THREE.AnimationUtils.arraySlice(inputAccessor.array, 0),
                            THREE.AnimationUtils.arraySlice(outputAccessor.array, 0),
                            interpolation
                        )

                        # Here is the trick to enable custom interpolation.
                        # Overrides .createInterpolant in a factory method which creates custom interpolation.
                        if sampler.interpolation == 'CUBICSPLINE':
                            def InterpolantFactoryMethodGLTFCubicSpline(result):
                                # A CUBICSPLINE keyframe in glTF has three output values for each input value,
                                # representing inTangent, splineVertex, and outTangent. As a result, track.getValueSize()
                                # must be divided by three to get the interpolant's sampleSize argument.

                                return GLTFCubicSplineInterpolant(self.times, self.values, self.getValueSize() / 3, result)

                            track.createInterpolant = InterpolantFactoryMethodGLTFCubicSpline

                            # Workaround, provide an alternate way to know if the interpolant type is cubis spline to track.
                            # track.getInterpolation() doesn't return valid value for custom interpolant.
                            track.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline = True

                        tracks.append(track)

        name = animationDef.name if animationDef.name is not None else 'animation_' + animationIndex

        return THREE.AnimationClip(name, undefined, tracks)

    def loadNode(self,nodeIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#nodes-and-hierarchy
         * @param {number} nodeIndex
         * @return {Promise<THREE.Object3D>}
        """
        json = self.json
        extensions = self.extensions

        meshReferences = json['meshReferences']
        meshUses = json['meshUses']

        nodeDef = json['nodes'][nodeIndex]

        dependencies = self.getMultiDependencies([
            'mesh',
            'skin',
            'camera',
            'light'
        ])

        # .isBone isn't in glTF spec. See .markDefs
        if 'isBone' in nodeDef:
            node = Bone()

        elif 'mesh' in nodeDef:
            mesh = dependencies['meshes'][nodeDef['mesh']]

            if meshReferences[nodeDef['mesh']] > 1:
                instanceNum = meshUses[nodeDef['mesh']]
                meshUses[nodeDef['mesh']] += 1

                node = mesh.clone()
                node.name += '_instance_%d' % instanceNum

                # onBeforeRender copy for Specular-Glossiness
                node.onBeforeRender = mesh.onBeforeRender

                for i in range(len(node.children)):
                    node.children[i].name += '_instance_' + instanceNum
                    node.children[i].onBeforeRender = mesh.children[i].onBeforeRender

            else:
                node = mesh

        elif 'camera' in nodeDef:
            node = dependencies.cameras[nodeDef['camera']]

        elif 'extensions' in nodeDef and \
             extensions[_KHR_LIGHTS_PUNCTUAL] in nodeDef and \
             'light' in nodeDef[extensions[_KHR_LIGHTS_PUNCTUAL]]:
            lights = extensions[_KHR_LIGHTS_PUNCTUAL]['lights']
            node = lights[nodeDef.extensions[_KHR_LIGHTS_PUNCTUAL]['light']]

        else:
            node = THREE.Object3D()

        if 'name' in nodeDef:
            node.name = THREE.PropertyBinding.sanitizeNodeName(nodeDef['name'])

        assignExtrasToUserData(node, nodeDef)

        if 'extensions' in nodeDef:
            addUnknownExtensionsToUserData(extensions, node, nodeDef)

        if 'matrix' in nodeDef:
            matrix = THREE.Matrix4()
            matrix.fromArray(nodeDef.matrix)
            node.applyMatrix(matrix)

        else:
            if 'translation' in nodeDef:
                node.position.fromArray(nodeDef['translation'])

            if 'rotation' in nodeDef:
                node.quaternion.fromArray(nodeDef['rotation'])

            if 'scale' in nodeDef:
                node.scale.fromArray(nodeDef['scale'])

        return node

    def loadScene(self, sceneIndex):
        """
         * Specification: https:#github.com/KhronosGroup/glTF/tree/master/specification/2.0#scenes
         * @param {number} sceneIndex
         * @return {Promise<THREE.Scene>}
        """
        # scene node hierachy builder

        def buildNodeHierachy(nodeId, parentObject, json, allNodes, skins):
            node = allNodes[nodeId]
            nodeDef = json['nodes'][nodeId]

            # build skeleton here as well

            if 'skin' in nodeDef:
                meshes = node.children if node.my_class(isGroup) else [node]

                for i in range(len(meshes)):
                    mesh = meshes[i]
                    skinEntry = skins[nodeDef.skin]

                    bones = []
                    boneInverses = []

                    for j in range(len(skinEntry.joints)):
                        jointId = skinEntry.joints[j]
                        jointNode = allNodes[jointId]

                        if jointNode:
                            bones.append(jointNode)

                            mat = THREE.Matrix4()

                            if skinEntry.inverseBindMatrices is not None:
                                mat.fromArray(skinEntry.inverseBindMatrices.array, j * 16)

                            boneInverses.append(mat)

                        else:
                            print('THREE.GLTFLoader: Joint "%s" could not be found.', jointId)

                    mesh.bind(THREE.Skeleton(bones, boneInverses), mesh.matrixWorld)


            # build node hierachy

            parentObject.add(node)

            if 'children' in nodeDef:
                children = nodeDef['children']

                for i in range(len(children)):
                    child = children[i]
                    buildNodeHierachy(child, node, json, allNodes, skins)

        json = self.json
        extensions = self.extensions
        sceneDef = json['scenes'][sceneIndex]

        dependencies = self.getMultiDependencies([
            'node',
            'skin'
        ])

        scene = THREE.Scene()
        if 'name' in sceneDef:
            scene.name = sceneDef['name']

        assignExtrasToUserData(scene, sceneDef)

        if 'extensions' in sceneDef:
            addUnknownExtensionsToUserData(extensions, scene, sceneDef)

        nodeIds = sceneDef['nodes'] if 'nodes' in sceneDef else []

        for i in range(len(nodeIds)):
            skins = dependencies['skins'] if 'skins' in dependencies else None
            buildNodeHierachy(nodeIds[i], scene, json, dependencies['nodes'], skins)

        return scene
