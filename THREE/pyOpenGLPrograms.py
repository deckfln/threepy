"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
import math
from THREE.Constants import *
from THREE.pyOpenGLProgram import *


def _allocateBones(object, capabilities):
    skeleton = object.skeleton
    bones = skeleton.bones

    if capabilities.floatVertexTextures:
        return 1024
    else:
        # // default for when object is not specified
        # // ( for example when prebuilding shader to be used with multiple objects )
        # //
        # //  - leave some extra space for other uniforms
        # //  - limit here is ANGLE's 254 max uniform vectors
        # //    (up to 54 should be safe)
        nVertexUniforms = capabilities.maxVertexUniforms
        nVertexMatrices = math.floor( ( nVertexUniforms - 20 ) / 4 )

        maxBones = min( nVertexMatrices, bones.length )

        if maxBones < bones.length:
            print( 'THREE.WebGLRenderer: Skeleton has ' + bones.length + ' bones. This GPU supports ' + maxBones + '.' )
            return 0

        return maxBones

        
def _getTextureEncodingFromMap(map, gammaOverrideLinear):
    if not map:
        encoding = LinearEncoding
    elif map.isTexture:
        encoding = map.encoding
    elif hasattr(map, 'isWebGLRenderTarget'):
        print( "THREE.WebGLPrograms.getTextureEncodingFromMap: don't use render targets as textures. Use their .texture property instead." )
        encoding = map.texture.encoding

    # // add backwards compatibility for WebGLRenderer.gammaInput/gammaOutput parameter, should probably be removed at some point.
    if encoding == LinearEncoding and gammaOverrideLinear:
        encoding = GammaEncoding

    return encoding

    
class pyOpenGLPrograms:
    shaderIDs = {
        'MeshDepthMaterial': 'depth',
        'MeshDistanceMaterial': 'distanceRGBA',
        'MeshNormalMaterial': 'normal',
        'MeshBasicMaterial': 'basic',
        'MeshLambertMaterial': 'lambert',
        'MeshPhongMaterial': 'phong',
        'MeshToonMaterial': 'phong',
        'MeshStandardMaterial': 'physical',
        'MeshPhysicalMaterial': 'physical',
        'LineBasicMaterial': 'basic',
        'LineDashedMaterial': 'dashed',
        'PointsMaterial': 'points',
        'ShadowMaterial': 'shadow'
    }

    parameterNames = [
        "precision", "supportsVertexTextures", "map", "mapEncoding", "envMap", "envMapMode", "envMapEncoding",
        "lightMap", "aoMap", "emissiveMap", "emissiveMapEncoding", "bumpMap", "normalMap", "displacementMap", "specularMap",
        "roughnessMap", "metalnessMap", "gradientMap",
        "alphaMap", "combine", "vertexColors", "fog", "useFog", "fogExp",
        "flatShading", "sizeAttenuation", "logarithmicDepthBuffer", "skinning",
        "maxBones", "useVertexTexture", "morphTargets", "morphNormals",
        "maxMorphTargets", "maxMorphNormals", "premultipliedAlpha",
        "numDirLights", "numPointLights", "numSpotLights", "numHemiLights", "numRectAreaLights",
        "shadowMapEnabled", "shadowMapType", "toneMapping", 'physicallyCorrectLights',
        "alphaTest", "doubleSided", "flipSided", "numClippingPlanes", "numClipIntersection", "depthPacking", "dithering"
    ]
        
    def __init__(self, renderer, extensions, capabilities):
        self.programs = []
        self.capabilities = capabilities
        self.extensions = extensions
        self.renderer = renderer

    def getParameters(self, material, lights, shadows, fog, nClipPlanes, nClipIntersection, object):
        shaderID = self.shaderIDs[ material.type ] if material.type in self.shaderIDs else None

        # // heuristics to create shader parameters according to lights in the scene
        # // (not to blow over maxLights budget)

        maxBones = _allocateBones(object, self.capabilities) if object.isSkinnedMesh else 0
        precision = self.capabilities.precision

        if material.precision is not None:
            precision = self.capabilities.getMaxPrecision(material.precision)

            if precision != material.precision:
                print( 'THREE.WebGLProgram.getParameters:', material.precision, 'not supported, using', precision, 'instead.')

        currentRenderTarget = self.renderer.getRenderTarget()

        map = material.map if hasattr(material, 'map') else None
        envMap = material.envMap if hasattr(material, 'envMap') else None
        lightMap = material.lightMap if hasattr(material, 'lightMap') else None
        aoMap = material.aoMap if hasattr(material, 'aoMap') else None
        emissiveMap = material.emissiveMap if hasattr(material, 'emissiveMap') else None
        bumpMap = material.bumpMap if hasattr(material, 'bumpMap') else None
        normalMap = material.normalMap if hasattr(material, 'normalMap') else None
        displacementMap = material.displacementMap if hasattr(material, 'displacementMap') else None
        roughnessMap = material.roughnessMap if hasattr(material, 'roughnessMap') else None
        metalnessMap = material.metalnessMap if hasattr(material, 'metalnessMap') else None
        specularMap = material.specularMap if hasattr(material, 'specularMap') else None
        alphaMap = material.alphaMap if hasattr(material, 'alphaMap') else None
        gradientMap = material.gradientMap if hasattr(material, 'gradientMap') else None
        combine = material.combine if hasattr(material, 'combine') else None

        parameters = {

            'shaderID': shaderID,

            'precision': precision,
            'supportsVertexTextures': self.capabilities.vertexTextures,
            'outputEncoding': _getTextureEncodingFromMap(currentRenderTarget.texture if currentRenderTarget else None, self.renderer.gammaOutput),
            'map': map is not None,
            'mapEncoding': _getTextureEncodingFromMap(map, self.renderer.gammaInput),
            'envMap': envMap is not None,
            'envMapMode': envMap and envMap.mapping,
            'envMapEncoding': _getTextureEncodingFromMap(envMap, self.renderer.gammaInput),
            'envMapCubeUV': ( envMap is not None ) and ( ( material.envMap.mapping == CubeUVReflectionMapping ) or ( material.envMap.mapping == CubeUVRefractionMapping ) ),
            'lightMap': lightMap is not None,
            'aoMap': aoMap is not None,
            'emissiveMap': emissiveMap is not None,
            'emissiveMapEncoding': _getTextureEncodingFromMap(emissiveMap, self.renderer.gammaInput),
            'bumpMap': bumpMap is not None,
            'normalMap': normalMap is not None,
            'displacementMap': displacementMap is not None,
            'roughnessMap': roughnessMap is not None,
            'metalnessMap': metalnessMap is not None,
            'specularMap': specularMap is not None,
            'alphaMap': alphaMap is not None,

            'gradientMap': gradientMap is not None,

            'combine': combine,

            'vertexColors': material.vertexColors,

            'fog': not not fog,
            'useFog': material.fog,
            'fogExp': ( fog and fog.isFogExp2 ),

            'flatShading': material.flatShading,

            'sizeAttenuation': material.sizeAttenuation if 'sizeAttenuation' in material.__dict__ else None,
            'logarithmicDepthBuffer': self.capabilities.logarithmicDepthBuffer,

            'skinning': material.skinning and maxBones > 0,
            'maxBones': maxBones,
            'useVertexTexture': self.capabilities.floatVertexTextures,

            'morphTargets': material.morphTargets,
            'morphNormals': material.morphNormals,
            'maxMorphTargets': self.renderer.maxMorphTargets,
            'maxMorphNormals': self.renderer.maxMorphNormals,

            'numDirLights': len(lights.directional),
            'numPointLights': len(lights.point),
            'numSpotLights': len(lights.spot),
            'numRectAreaLights': len(lights.rectArea),
            'numHemiLights': len(lights.hemi),

            'numClippingPlanes': nClipPlanes,
            'numClipIntersection': nClipIntersection,

            'dithering': material.dithering,

            'shadowMapEnabled': self.renderer.shadowMap.enabled and object.receiveShadow and len(shadows) > 0,
            'shadowMapType': self.renderer.shadowMap.type,

            'toneMapping': self.renderer.toneMapping,
            'physicallyCorrectLights': self.renderer.physicallyCorrectLights,

            'premultipliedAlpha': material.premultipliedAlpha,

            'alphaTest': material.alphaTest,
            'doubleSided': material.side == DoubleSide,
            'flipSided': material.side == BackSide,

            'depthPacking': 'depthPacking' in material.__dict__ and material.depthPacking is not None
        }

        return parameters

    def getProgramCode(self, material, parameters ):
        array = []

        if parameters['shaderID']:
            array.append(parameters['shaderID'])
        else:
            array.append(material['fragmentShader'])
            array.append(material['vertexShader'])

        if 'defines' in material.__dict__:
            for name in material.defines:
                array.append(name)
                array.append(str(material.defines[name]))

        for i in range(len(self.parameterNames)):
            array.append(str(parameters[ self.parameterNames[i]]))

        array.append(str(material.onBeforeCompile))

        array.append(str(self.renderer.gammaOutput))

        return "\n".join(array)

    def acquireProgram(self,  material, shader, parameters, code):
        program = None
        # // Check if code has been already compiled
        for p in range(len(self.programs)):
            programInfo = self.programs[p]

            if programInfo.code == code:
                program = programInfo
                program.usedTimes += 1

                break

        if program is None:
            program = pyOpenGLProgram(self.renderer, self.extensions, code, material, shader, parameters)
            self.programs.append(program)

        return program

    def releaseProgram(self, program):
        program.usedTimes -= 1
        if program.usedTimes == 0:
            # // Remove from unordered set
            i = self.programs.index(program)
            self.programs[i] = self.programs[len(self.programs) - 1]
            self.programs.pop()

            # // Free WebGL resources
            program.destroy()
