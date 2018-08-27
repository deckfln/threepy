"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
from THREE.renderers.pyOpenGL.pyOpenGLProgram import *


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
    encoding = LinearEncoding

    if map is None:
        encoding = LinearEncoding
    elif map.my_class(isTexture):
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
        'ShadowMaterial': 'shadow',
        'SpriteMaterial': 'sprite'
    }

    parameterNames = [
        "precision", "supportsVertexTextures", "map", "mapEncoding", "envMap", "envMapMode", "envMapEncoding",
        "lightMap", "aoMap", "emissiveMap", "emissiveMapEncoding", "bumpMap", "normalMap", "objectSpaceNormalMap", "displacementMap", "specularMap",
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

        maxBones = _allocateBones(object, self.capabilities) if object.is_a('SkinnedMesh') else 0
        precision = self.capabilities.precision

        if material.precision is not None:
            precision = self.capabilities.getMaxPrecision(material.precision)

            if precision != material.precision:
                print( 'THREE.WebGLProgram.getParameters:', material.precision, 'not supported, using', precision, 'instead.')

        currentRenderTarget = self.renderer.getRenderTarget()

        map = material.map
        envMap = material.envMap
        lightMap = material.lightMap
        aoMap = material.aoMap
        emissiveMap = material.emissiveMap
        bumpMap = material.bumpMap
        normalMap = material.normalMap
        displacementMap = material.displacementMap
        roughnessMap = material.roughnessMap
        metalnessMap = material.metalnessMap
        specularMap = material.specularMap
        alphaMap = material.alphaMap
        gradientMap = material.gradientMap
        combine = material.combine

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
            'objectSpaceNormalMap': material.normalMapType == ObjectSpaceNormalMap,
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
            'fogExp': ( fog and fog.my_class(isFogExp2) ),

            'flatShading': material.flatShading,

            'sizeAttenuation': material.sizeAttenuation,
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

            'depthPacking': 'depthPacking' if material.depthPacking else False
        }

        return parameters

    def getProgramCode(self, material, parameters ):
        array = []

        if parameters['shaderID']:
            array.append(parameters['shaderID'])
        else:
            array.append(material['fragmentShader'])
            array.append(material['vertexShader'])

        if material.defines:
            for name in material.defines:
                array.append(name)
                array.append(str(material.defines[name]))

        for parameter in self.parameterNames:
            array.append(str(parameters[parameter]))

        array.append(str(material.onBeforeCompile))

        array.append(str(self.renderer.gammaOutput))

        return "\n".join(array)

    def acquireProgram(self,  material, shader, parameters, code):
        program = None
        # // Check if code has been already compiled
        for programInfo in self.programs:
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
