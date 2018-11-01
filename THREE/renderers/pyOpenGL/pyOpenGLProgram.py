"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

from OpenGL.raw.GL.VERSION.GL_2_0 import glCreateProgram

from THREE.renderers.shaders.ShaderChunk import *
from THREE.renderers.pyOpenGL.pyOpenGLUniformBlock import *


def addLineNumbers(string):
    lines = string.split('\n')

    for i in range(len(lines)):
        lines[i] = "%d : %s" % (i + 1, lines[i])

    return '\n'.join(lines)


def pyOpenGLShader(type, string):
    shader = glCreateShader(type)
    glShaderSource(shader, string)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        if type == GL_VERTEX_SHADER:
            t = 'vertex'
        else:
            t = 'fragment'
        log = glGetShaderInfoLog(shader)
        print(log.decode("utf-8"))
        print(addLineNumbers(string))
        raise RuntimeError('THREE.WebGLShader: Shader couldn\'t compile.')


    # // --enable - privileged - webgl - extension
    # // console.log(type, gl.getExtension('WEBGL_debug_shaders').getTranslatedShaderSource(shader));

    return shader


_programIdCount = 0


def getEncodingComponents(encoding):
    _enc = {
        LinearEncoding: ['Linear', '(value)'],
        sRGBEncoding: ['sRGB', '(value)'],
        RGBEEncoding: ['RGBE', '(value)'],
        RGBM7Encoding: ['RGBM', '(value, 7.0)'],
        RGBM16Encoding: ['RGBM', '(value, 16.0)'],
        RGBDEncoding: ['RGBD', '(value, 256.0)'],
        GammaEncoding: ['Gamma', '(value, float(GAMMA_FACTOR))']
    }

    if encoding in _enc:
        return _enc[encoding]
        
    raise RuntimeError('getEncodingComponents: unsupported encoding: %s ' % encoding)


def getTexelDecodingFunction(functionName, encoding):
    components = getEncodingComponents(encoding)
    return "vec4 %s (vec4 value) { return %sToLinear%s; }" % (functionName, components[0], components[1])


def getTexelEncodingFunction(functionName, encoding):
    components = getEncodingComponents(encoding)
    return "vec4 %s (vec4 value) { return LinearTo%s%s;}" % (functionName, components[0], components[1])


_tone_mapping = {
    LinearToneMapping: "Linear",
    ReinhardToneMapping: "Reinhard",
    Uncharted2ToneMapping: "Uncharted2",
    CineonToneMapping: "OptimizedCineon"
}


def getToneMappingFunction(functionName, toneMapping):
    if toneMapping not in _tone_mapping:
        raise RuntimeError('unsupported toneMapping: %d' % toneMapping)

    toneMappingName = _tone_mapping[toneMapping]

    return "vec3 " + functionName + "(vec3 color) { return " + toneMappingName + "ToneMapping(color); }"


def generateExtensions(extensions, parameters, rendererExtensions):
    extensions = extensions or {}

    chunks = [
        '#extension GL_OES_standard_derivatives : enable' if ('derivatives' in extensions or parameters['envMapCubeUV'] or parameters['bumpMap'] or ( parameters['normalMap'] and not parameters['objectSpaceNormalMap']) or parameters['flatShading']) else '',
        '#extension GL_EXT_frag_depth : enable' if ('fragDepth' in extensions or parameters['logarithmicDepthBuffer']) and rendererExtensions.get('EXT_frag_depth') else '',
        '#extension GL_EXT_draw_buffers : require' if ('drawBuffers' in extensions) and rendererExtensions.get('WEBGL_draw_buffers') else '',
        '#extension GL_EXT_shader_texture_lod : enable' if ('shaderTextureLOD' in extensions or parameters['envMap']) and rendererExtensions.get('EXT_shader_texture_lod') else '',
        '#extension GL_NV_shadow_samplers_cube : enable'  # TODO FDE: how to find there is a textureCube in the shader ?
    ]

    return '\n'.join([string for string in chunks if string != ''])


def generateDefines(defines):
    chunks = []

    if defines is None:
        return ""

    for name in defines:
        value = defines[name]

        if value is not False:
            chunks.append('#define %s %s' % (name, str(value)))

    return '\n'.join(chunks)


def fetchAttributeLocations(gl, program):
    attributes = {}

    n = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTES)

    for i in range(n):
        info = glGetActiveAttrib(program, i)
        name = info.name

        # // console.log("THREE.WebGLProgram: ACTIVE VERTEX ATTRIBUTE:", name, i)

        attributes[name] = glGetAttribLocation(program, name)

    return attributes


def filterEmptyLine(string):
    return string != ''


def replaceLightNums(string, parameters):
    string = re.sub('NUM_DIR_LIGHTS', str(parameters['numDirLights']), string)
    string = re.sub('NUM_SPOT_LIGHTS', str(parameters['numSpotLights']), string)
    string = re.sub('NUM_RECT_AREA_LIGHTS', str(parameters['numRectAreaLights']), string)
    string = re.sub('NUM_POINT_LIGHTS', str(parameters['numPointLights']), string)
    string = re.sub('NUM_HEMI_LIGHTS', str(parameters['numHemiLights']), string)

    return string


def replaceClippingPlaneNums(string, parameters):
    string = re.sub('NUM_CLIPPING_PLANES', str(parameters['numClippingPlanes']), string)
    string = re.sub('UNION_CLIPPING_PLANES', str(parameters['numClippingPlanes'] - parameters['numClipIntersection']), string)
    return string


def parseIncludes(string):
    pattern = '^[\t ]*#include +<([\w\d.]+)>'
    new = string

    for match in re.finditer(pattern, string, re.MULTILINE):
        include = match.groups(0)[0]
        includes = parseIncludes(getShaderChunk(include))
        toreplace = match.string[match.start(0):match.end(0)]
        new = re.sub(toreplace, includes, new)

    return new


def unrollLoops(string):
    pattern = '#pragma unroll_loop[\s]+?for \( *int i \= (\d+)\; i < (\d+)\; i \+\+ \) \{([\s\S]+?)(?=\})\}'

    unrolled_string = string
    for match in re.finditer(pattern, string):
        start = int(match.groups(0)[0])
        end= int(match.groups(0)[1])
        snipset = match.groups(0)[2]
        unroll = ''
        for i in range(start, end):
            vi = re.sub('\[ i \]', '[' + str(i) + ']', snipset)
            unroll += vi

        src = match.group()
        unrolled_string = unrolled_string.replace(src, unroll)

    return unrolled_string


def _glGetActiveAttrib(program, index):
    """Wrap PyOpenGL glGetActiveAttrib as for glGetActiveUniform
    """
    bufSize = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    length = GLsizei()
    size = GLint()
    type_ = GLenum()
    name = (GLchar * bufSize)()

    glGetActiveAttrib(program, index, bufSize, length, size, type_, name)
    return name.value, size.value, type_.value


def _getAttributeLocations(program):
    attributes = {}

    n = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTES)

    for i in range(n):
        info = _glGetActiveAttrib(program, i)
        name = info[0]
        item = name.decode("utf-8")

        attributes[item] = glGetAttribLocation(program, name)

    return attributes


_envmap_mapping = {
    CubeReflectionMapping: 'ENVMAP_TYPE_CUBE',
    CubeRefractionMapping: 'ENVMAP_TYPE_CUBE',
    CubeUVReflectionMapping: 'ENVMAP_TYPE_CUBE_UV',
    CubeUVRefractionMapping: 'ENVMAP_TYPE_CUBE_UV',
    EquirectangularReflectionMapping: 'ENVMAP_TYPE_EQUIREC',
    EquirectangularRefractionMapping: 'ENVMAP_TYPE_EQUIREC',
    SphericalReflectionMapping: 'ENVMAP_TYPE_SPHERE'
}


class pyOpenGLProgram:
    def __init__(self, renderer, extensions, code, material, shader, parameters, instance=False):
        global _programIdCount
        global _envmap_mapping

        self.name = shader.name
        self.id = _programIdCount
        _programIdCount += 1
        self.code = code
        self.usedTimes = 1

        defines = material.defines

        vertexShader = shader.vertexShader
        fragmentShader = shader.fragmentShader

        shadowMapTypeDefine = 'SHADOWMAP_TYPE_BASIC'

        if 'shadowMapType' in parameters:
            if parameters['shadowMapType'] == PCFShadowMap:
                shadowMapTypeDefine = 'SHADOWMAP_TYPE_PCF'
            elif parameters['shadowMapType'] == PCFSoftShadowMap:
                shadowMapTypeDefine = 'SHADOWMAP_TYPE_PCF_SOFT'

        envMapTypeDefine = 'ENVMAP_TYPE_CUBE'
        envMapModeDefine = 'ENVMAP_MODE_REFLECTION'
        envMapBlendingDefine = 'ENVMAP_BLENDING_MULTIPLY'

        if parameters[ 'envMap' ] and material.envMap.mapping in _envmap_mapping:
            envMapTypeDefine = _envmap_mapping[material.envMap.mapping]

            if material.envMap.mapping == CubeRefractionMapping or material.envMap.mapping == EquirectangularRefractionMapping:
                envMapModeDefine = 'ENVMAP_MODE_REFRACTION'

            _combine = {
                MultiplyOperation: 'ENVMAP_BLENDING_MULTIPLY',
                MixOperation: 'ENVMAP_BLENDING_MIX',
                AddOperation: 'ENVMAP_BLENDING_ADD'
            }
            envMapBlendingDefine = _combine[material.combine]

        gammaFactorDefine = 1.0
        if renderer.gammaFactor > 0:
            gammaFactorDefine = renderer.gammaFactor

        # // console.log('building program ')
        exts = material.extensions
        customExtensions = generateExtensions(exts, parameters, extensions)

        customDefines = generateDefines(defines)

        if instance:
            customDefines += "#define USE_INSTANCES\n"

        # //

        program = OpenGL.raw.GL.VERSION.GL_2_0.glCreateProgram()

        if material.my_class(isRawShaderMaterial):
            # compatibility mode for threejs
            if '#version 330' not in vertexShader:
                _glversion = '#version 330'
            else:
                _glversion = ''

            prefixVertex = '\n'.join([
                _glversion,
                customDefines,
                '\n'
            ])

            if len(prefixVertex) > 0:
                prefixVertex += '\n'

            # compatibility mode for threejs
            if '#version 330' not in fragmentShader:
                _glversion = '#version 330'
            else:
                _glversion = ''

            prefixFragment = '\n'.join([
                _glversion,
                customExtensions,
                customDefines,
                '\n'
            ])
            if len(prefixFragment) > 0:
                prefixFragment += '\n'

            # compatibility mode with threejs
            vertexShader = vertexShader.replace("uniform mat4 modelViewMatrix;", """layout (std140) uniform modelViewMatricesBlock
                {
                    uniform mat4 modelViewMatrices[1024];
                };""")
            vertexShader = vertexShader.replace("uniform mat4 viewMatrix;", "")
            vertexShader = vertexShader.replace("uniform mat4 projectionMatrix;", """layout (std140) uniform camera
                {
                    uniform mat4 projectionMatrix;
                    uniform mat4 viewMatrix;
                };

                #ifdef USE_INSTANCES
                    in int objectID;
                #else
                    uniform int objectID;
                #endif""")

        else:
            _prefixVertex = [
                '#version 330',
                'precision ' + parameters['precision'] + ' float;',
                'precision ' + parameters['precision'] + ' int;',

                '#define SHADER_NAME ' + shader.name,

                customDefines,

                '#define VERTEX_TEXTURES' if parameters['supportsVertexTextures'] else '',

                '#define GAMMA_FACTOR %f' % gammaFactorDefine,

                '#define MAX_BONES %d' % parameters['maxBones'],
                '#define USE_FOG' if (parameters['useFog'] and parameters['fog']) else '',
                '#define FOG_EXP2' if (parameters['useFog'] and parameters['fogExp']) else '',

                '#define USE_MAP' if parameters['map'] else '',
                '#define USE_ENVMAP' if parameters['envMap'] else '',
                '#define ' + envMapModeDefine if parameters['envMap'] else '',
                '#define USE_LIGHTMAP' if parameters['lightMap'] else '',
                '#define USE_AOMAP' if parameters['aoMap'] else '',
                '#define USE_EMISSIVEMAP' if parameters['emissiveMap'] else '',
                '#define USE_BUMPMAP' if parameters['bumpMap'] else '',
                '#define USE_NORMALMAP' if parameters['normalMap'] else '',
                '#define OBJECTSPACE_NORMALMAP' if parameters['normalMap'] and parameters['objectSpaceNormalMap'] else '',
                '#define USE_DISPLACEMENTMAP' if parameters['displacementMap'] and parameters['supportsVertexTextures'] else '',
                '#define USE_SPECULARMAP' if parameters['specularMap'] else '',
                '#define USE_ROUGHNESSMAP' if parameters['roughnessMap'] else '',
                '#define USE_METALNESSMAP' if parameters['metalnessMap'] else '',
                '#define USE_ALPHAMAP' if parameters['alphaMap'] else '',
                '#define USE_COLOR' if parameters['vertexColors'] else '',

                '#define FLAT_SHADED' if parameters['flatShading'] else '',

                '#define USE_SKINNING' if parameters['skinning'] else '',
                '#define BONE_TEXTURE' if parameters['useVertexTexture'] else '',

                '#define USE_MORPHTARGETS' if parameters['morphTargets'] else '',
                '#define USE_MORPHNORMALS' if parameters['morphNormals'] and not parameters['flatShading'] else '',
                '#define DOUBLE_SIDED' if parameters['doubleSided'] else '',
                '#define FLIP_SIDED' if parameters['flipSided'] else '',

                '#define USE_SHADOWMAP' if parameters['shadowMapEnabled'] else '',
                '#define ' + shadowMapTypeDefine if parameters['shadowMapEnabled'] else '',

                '#define USE_SIZEATTENUATION' if parameters['sizeAttenuation'] else '',

                '#define USE_LOGDEPTHBUF' if parameters['logarithmicDepthBuffer'] else '',
                '#define USE_LOGDEPTHBUF_EXT' if parameters['logarithmicDepthBuffer'] and extensions.get('EXT_frag_depth') else '',

                'in vec3 position;',
                'in vec3 normal;',
                'in vec2 uv;',

                'layout (std140) uniform camera',
                '{',
                    'uniform mat4 projectionMatrix;',
                    'uniform mat4 viewMatrix;',
                '};',

                '#ifdef USE_INSTANCES',
                    'in int objectID;',
                '#else',
                    'uniform int objectID;',
                '#endif',

                'layout (std140) uniform modelMatricesBlock',
                '{',
                    'uniform mat4 modelMatrices[1024];',
                '};',
                'layout (std140) uniform modelViewMatricesBlock',
                '{',
                    'uniform mat4 modelViewMatrices[1024];',
                '};',
                'layout (std140) uniform normalMatricesBlock',
                '{',
                    'uniform mat3 normalMatrices[1024];',
                '};',

                # 'uniform mat4 modelMatrix;',
                # 'uniform mat4 modelViewMatrix;',
                # 'uniform mat3 normalMatrix;',
                'uniform vec3 cameraPosition;',

                '#ifdef USE_COLOR',

                '    attribute vec3 color;',

                '#endif',

                '#ifdef USE_MORPHTARGETS',

                '    attribute vec3 morphTarget0;',
                '    attribute vec3 morphTarget1;',
                '    attribute vec3 morphTarget2;',
                '    attribute vec3 morphTarget3;',

                '    #ifdef USE_MORPHNORMALS',

                '        attribute vec3 morphNormal0;',
                '        attribute vec3 morphNormal1;',
                '        attribute vec3 morphNormal2;',
                '        attribute vec3 morphNormal3;',

                '    #else',

                '        attribute vec3 morphTarget4;',
                '        attribute vec3 morphTarget5;',
                '        attribute vec3 morphTarget6;',
                '        attribute vec3 morphTarget7;',

                '    #endif',

                '#endif',

                '#ifdef USE_SKINNING',

                '    attribute vec4 skinIndex;',
                '    attribute vec4 skinWeight;',

                '#endif',

                '\n'
            ]
            prefixVertex = '\n'.join([string for string in _prefixVertex if string != ''])

            _prefixFragment = [
                '#version 330\n',
                customExtensions,
                'precision ' + parameters['precision'] + ' float;',
                'precision ' + parameters['precision'] + ' int;',

                '#define SHADER_NAME ' + shader.name,

                customDefines,

                '#define ALPHATEST %s ' % parameters['alphaTest'] + '' if parameters['alphaTest'] % 1 else '.0' if parameters['alphaTest'] else '',  # add '.0' if integer

                '#define GAMMA_FACTOR %f' % gammaFactorDefine,

                '#define USE_FOG' if (parameters['useFog'] and parameters['fog']) else '',
                '#define FOG_EXP2' if (parameters['useFog'] and parameters['fogExp']) else '',

                '#define USE_MAP' if parameters['map'] else '',
                '#define USE_ENVMAP' if parameters['envMap'] else '',
                '#define ' + envMapTypeDefine if parameters['envMap'] else '',
                '#define ' + envMapModeDefine if parameters['envMap'] else '',
                '#define ' + envMapBlendingDefine if parameters['envMap'] else '',
                '#define USE_LIGHTMAP' if parameters['lightMap'] else '',
                '#define USE_AOMAP' if parameters['aoMap'] else '',
                '#define USE_EMISSIVEMAP' if parameters['emissiveMap'] else '',
                '#define USE_BUMPMAP' if parameters['bumpMap'] else '',
                '#define USE_NORMALMAP' if parameters['normalMap'] else '',
                '#define OBJECTSPACE_NORMALMAP' if parameters['normalMap'] and parameters['objectSpaceNormalMap'] else '',
                '#define USE_SPECULARMAP' if parameters['specularMap'] else '',
                '#define USE_ROUGHNESSMAP' if parameters['roughnessMap'] else '',
                '#define USE_METALNESSMAP' if parameters['metalnessMap'] else '',
                '#define USE_ALPHAMAP' if parameters['alphaMap'] else '',
                '#define USE_COLOR' if parameters['vertexColors'] else '',

                '#define USE_GRADIENTMAP' if parameters['gradientMap'] else '',

                '#define FLAT_SHADED' if parameters['flatShading'] else '',

                '#define DOUBLE_SIDED' if parameters['doubleSided'] else '',
                '#define FLIP_SIDED' if parameters['flipSided'] else '',

                '#define USE_SHADOWMAP' if parameters['shadowMapEnabled'] else '',
                '#define ' + shadowMapTypeDefine if parameters['shadowMapEnabled'] else '',

                "#define PREMULTIPLIED_ALPHA" if parameters['premultipliedAlpha'] else '',

                "#define PHYSICALLY_CORRECT_LIGHTS" if parameters['physicallyCorrectLights'] else '',

                '#define USE_LOGDEPTHBUF' if parameters['logarithmicDepthBuffer'] else '',
                '#define USE_LOGDEPTHBUF_EXT' if parameters['logarithmicDepthBuffer'] and extensions.get('EXT_frag_depth') else '',

                '#define TEXTURE_LOD_EXT' if parameters['envMap'] and extensions.get('EXT_shader_texture_lod') else '',

                # 'uniform mat4 viewMatrix;',
                'layout (std140) uniform camera',
                '{',
                    'uniform mat4 projectionMatrix;',
                    'uniform mat4 viewMatrix;',
                '};',
                'uniform vec3 cameraPosition;',

                "#define TONE_MAPPING" if (parameters['toneMapping'] != NoToneMapping) else '',
                getShaderChunk('tonemapping_pars_fragment') if (parameters['toneMapping'] != NoToneMapping) else '',  # // self code is required here because it is used by the toneMapping() function defined below
                getToneMappingFunction("toneMapping", parameters['toneMapping']) if (parameters['toneMapping'] != NoToneMapping) else '',

                '#define DITHERING' if parameters['dithering'] else '',

                getShaderChunk('encodings_pars_fragment') if (parameters['outputEncoding'] or parameters['mapEncoding'] or parameters['envMapEncoding'] or parameters['emissiveMapEncoding']) else '', # // self code is required here because it is used by the various encoding/decoding function defined below
                getTexelDecodingFunction('mapTexelToLinear', parameters['mapEncoding']) if parameters['mapEncoding'] else '',
                getTexelDecodingFunction('envMapTexelToLinear', parameters['envMapEncoding']) if parameters['envMapEncoding'] else '',
                getTexelDecodingFunction('emissiveMapTexelToLinear', parameters['emissiveMapEncoding']) if parameters['emissiveMapEncoding'] else '',
                getTexelEncodingFunction("linearToOutputTexel", parameters['outputEncoding']) if parameters['outputEncoding'] else '',

                ("#define DEPTH_PACKING %d" %  material.depthPacking) if parameters['depthPacking'] else '',
                '\n'
            ]
            prefixFragment = '\n'.join([string for string in _prefixFragment if string != ''])

        # compatibility mode with threejs
        vertexShader = vertexShader.replace("modelViewMatrix", 'modelViewMatrices[objectID]')
        vertexShader = vertexShader.replace("modelMatrix", 'modelMatrices[objectID]')
        vertexShader = vertexShader.replace("normalMatrix", 'normalMatrices[objectID]')

        vertexShader = parseIncludes(vertexShader)
        vertexShader = replaceLightNums(vertexShader, parameters)
        vertexShader = replaceClippingPlaneNums(vertexShader, parameters)

        fragmentShader = parseIncludes(fragmentShader)
        fragmentShader = replaceLightNums(fragmentShader, parameters)
        fragmentShader = replaceClippingPlaneNums(fragmentShader, parameters)

        vertexShader = unrollLoops(vertexShader)
        fragmentShader = unrollLoops(fragmentShader)

        #TODO reimplement WEBGL2
        """
        if not material.my_class(isRawShaderMaterial):
            isGLSL3ShaderMaterial = False

            versionRegex = "^ \s *  # version\s+300\s+es\s*\n"

            if material.my_class(isShaderMaterial) and \
                re.search(versionRegex, vertexShader) is not None and \
                re.match( versionRegex, fragmentShader) is not None:

                isGLSL3ShaderMaterial = True

                vertexShader = vertexShader.replace( versionRegex, '' )
                fragmentShader = fragmentShader.replace( versionRegex, '' )

            # GLSL3.0 conversion
            _prefixVertex = [
                '#version 330\n',
                '#define attribute in',
                '#define varying out',
                '#define texture2D texture'
            ]
            prefixVertex = '\n'.join([string for string in _prefixVertex if string != '']) + prefixVertex

            _prefixFragment = [
                '#version 330\n',

                customExtensions,

                '#define varying in',
                '' if isGLSL3ShaderMaterial else 'out highp vec4 pc_fragColor;',
                '' if isGLSL3ShaderMaterial else '#define gl_FragColor pc_fragColor',
                '#define gl_FragDepthEXT gl_FragDepth',
                '#define texture2D texture',
                '#define textureCube texture',
                '#define texture2DProj textureProj',
                '#define texture2DLodEXT textureLod',
                '#define texture2DProjLodEXT textureProjLod',
                '#define textureCubeLodEXT textureLod',
                '#define texture2DGradEXT textureGrad',
                '#define texture2DProjGradEXT textureProjGrad',
                '#define textureCubeGradEXT textureGrad'
            ]
            prefixFragment = '\n'.join([string for string in _prefixFragment if string != '']) + "\n" + prefixFragment
        """

        vertexGlsl = prefixVertex + vertexShader
        fragmentGlsl = prefixFragment + fragmentShader

        # print('*VERTEX*', vertexGlsl)
        # print('*FRAGMENT*', fragmentGlsl)
        
        glVertexShader = pyOpenGLShader(GL_VERTEX_SHADER, vertexGlsl)
        glFragmentShader = pyOpenGLShader(GL_FRAGMENT_SHADER, fragmentGlsl)

        glAttachShader(program, glVertexShader)
        glAttachShader(program, glFragmentShader)

        # // Force a particular attribute to index 0.

        if material.index0AttributeName:
            glBindAttribLocation(program, 0, material.index0AttributeName)
        elif parameters['morphTargets']:
            # // programs with morphTargets displace position out of attribute 0
            glBindAttribLocation(program, 0, 'position')

        glLinkProgram(program)
        #TODO FDE ? glValidateProgram(program)

        programLog = glGetProgramInfoLog(program)
        vertexLog = glGetShaderInfoLog(glVertexShader)
        fragmentLog = glGetShaderInfoLog(glFragmentShader)

        runnable = True
        haveDiagnostics = True

        # // console.log('**VERTEX**', gl.getExtension('WEBGL_debug_shaders').getTranslatedShaderSource(glVertexShader))
        # // console.log('**FRAGMENT**', gl.getExtension('WEBGL_debug_shaders').getTranslatedShaderSource(glFragmentShader))

        if not glGetProgramiv(program, GL_LINK_STATUS):
            runnable = False

            error = glGetError()
            valid = glGetProgramiv(program, GL_VALIDATE_STATUS)

            raise RuntimeError('THREE.pyOpenGLProgram: shader error: %d GL_VALIDATE_STATUS %d gl.getProgramInfoLog %s %s %s' % (error, valid , programLog, vertexLog, fragmentLog))
        elif programLog != b'' and programLog != '':
            log = addLineNumbers(programLog.decode('utf8'))
            #print(log)
            #raise RuntimeError('THREE.WebGLProgram: gl.getProgramInfoLog()')

        elif vertexLog == '' or fragmentLog == '':
            haveDiagnostics = False

        if haveDiagnostics:
            self.diagnostics = {
                'runnable': runnable,
                'material': material,

                'programLog': programLog,
                'vertexShader': {
                    'log': vertexLog,
                    'prefix': prefixVertex
                },

                'fragmentShader': {
                    'log': fragmentLog,
                    'prefix': prefixFragment
                }
            }

        # // clean up

        glDeleteShader(glVertexShader)
        glDeleteShader(glFragmentShader)

        # // set up caching for uniform locations
        renderer.uniformBlocks.add(program, vertexGlsl, fragmentGlsl)
        self.cachedUniforms = pyOpenGLUniforms(program, renderer, vertexGlsl, fragmentGlsl)
        self.cachedAttributes = _getAttributeLocations(program)

        self.program = program
        self.vertexShader = glVertexShader
        self.fragmentShader = glFragmentShader

    def setObject(self, object):
        self.cachedUniforms.setValue('objectID', object.id, True)

    def getUniforms(self):
        return self.cachedUniforms

    # // set up caching for attribute locations

    def getAttributes(self):
        return self.cachedAttributes

    # // free resource

    def destroy(self):
        glDeleteProgram(self.program)
        self.program = None

    # // DEPRECATED
    def uniforms(self):
        print('THREE.WebGLProgram: .uniforms is now .getUniforms().')
        return self.getUniforms()

    def attributes(self):
        print('THREE.WebGLProgram: .attributes is now .getAttributes().')
        return self.getAttributes()

    """
    FDE
    """
    def start(self):
        glUseProgram(self.program)

    def stop(self):
        glUseProgram(0)

    def enableVertexAttrib(self):
        for a in self.cachedAttributes._attributes:
            glEnableVertexAttribArray(self.cachedAttributes._attributes[a])
