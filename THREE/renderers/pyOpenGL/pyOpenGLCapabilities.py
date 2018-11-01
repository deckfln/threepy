"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
# from OpenGL_accelerate import *
from OpenGL.GL import *
from OpenGL.GL.EXT.texture_filter_anisotropic import *


_maxAnisotropy=None


class pyOpenGLCapabilities:
    def __init__(self, extensions, parameters ):
        self.extensions = extensions

        precision = parameters.precision if 'precision' in parameters else 'highp'
        maxPrecision = self.getMaxPrecision( precision )

        if maxPrecision != precision:
            print( 'THREE.WebGLRenderer:', precision, 'not supported, using', maxPrecision, 'instead.' )
            precision = maxPrecision

        logarithmicDepthBuffer = 'logarithmicDepthBuffer' in parameters and parameters['logarithmicDepthBuffer'] and not extensions.get( 'EXT_frag_depth' )

        maxTextures = glGetIntegerv( GL_MAX_TEXTURE_IMAGE_UNITS )
        maxVertexTextures = glGetIntegerv( GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS )
        maxTextureSize = glGetIntegerv( GL_MAX_TEXTURE_SIZE )
        maxCubemapSize = glGetIntegerv( GL_MAX_CUBE_MAP_TEXTURE_SIZE )

        maxAttributes = glGetIntegerv( GL_MAX_VERTEX_ATTRIBS )
        maxVertexUniforms = glGetIntegerv( GL_MAX_VERTEX_UNIFORM_VECTORS )
        maxVaryings = glGetIntegerv( GL_MAX_VARYING_VECTORS )
        maxFragmentUniforms = glGetIntegerv( GL_MAX_FRAGMENT_UNIFORM_VECTORS )

        vertexTextures = maxVertexTextures > 0
        floatFragmentTextures = not extensions.get( 'OES_texture_float' )
        floatVertexTextures = vertexTextures and floatFragmentTextures

        self.precision = precision
        self.logarithmicDepthBuffer = logarithmicDepthBuffer
        self.maxTextures = maxTextures
        self.maxVertexTextures = maxVertexTextures
        self.maxTextureSize = maxTextureSize
        self.maxCubemapSize = maxCubemapSize

        self.maxAttributes = maxAttributes
        self.maxVertexUniforms = maxVertexUniforms
        self.maxVaryings = maxVaryings
        self.maxFragmentUniforms = maxFragmentUniforms

        self.vertexTextures = vertexTextures
        self.floatFragmentTextures = floatFragmentTextures
        self.floatVertexTextures = floatVertexTextures

    def getMaxAnisotropy(self):
        global _maxAnisotropy
        if _maxAnisotropy is not None:
            return _maxAnisotropy

        extension = self.extensions.get( 'EXT_texture_filter_anisotropic' )

        if extension is not None:
            _maxAnisotropy = glGetIntegerv( GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT )
        else:
            _maxAnisotropy = 0

        return _maxAnisotropy

    def getMaxPrecision(self, precision ):
        _range = GLint()
        _precisionV = GLint()
        _precisionF = GLint()

        if precision == 'highp':
            glGetShaderPrecisionFormat(GL_VERTEX_SHADER, GL_HIGH_FLOAT, _range, _precisionF)
            glGetShaderPrecisionFormat(GL_FRAGMENT_SHADER, GL_HIGH_FLOAT, _range, _precisionV)
            if _precisionF.value > 0 and _precisionV.value > 0:
                return 'highp'

            precision = 'mediump'

        if precision == 'mediump':
            glGetShaderPrecisionFormat(GL_VERTEX_SHADER, GL_MEDIUM_FLOAT, _range, _precisionF)
            glGetShaderPrecisionFormat(GL_FRAGMENT_SHADER, GL_MEDIUM_FLOAT, _range, _precisionV)
            if _precisionF.value > 0 and _precisionV.value > 0:
                return 'mediump'

        return 'lowp'
