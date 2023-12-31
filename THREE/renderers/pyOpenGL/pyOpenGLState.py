"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL.GL import *
from THREE.Constants import *
from THREE.math.Vector4 import *
import OpenGL.raw.GL.VERSION.GL_1_0


class _ColorBuffer:
    def __init__(self):
        self.locked = False

        self.color = Vector4()
        self.currentColorMask = None
        self.currentColorClear = Vector4( 0, 0, 0, 0 )

    def setMask(self, colorMask ):
        if self.currentColorMask != colorMask and not self.locked:
            glColorMask( colorMask, colorMask, colorMask, colorMask )
            self.currentColorMask = colorMask

    def setLocked(self, lock ):
        self.locked = lock

    def setClear(self, r, g, b, a, premultipliedAlpha=None):
        if premultipliedAlpha:
            r *= a
            g *= a
            b *= a

        self.color.set(r, g, b, a)

        if not self.currentColorClear.equals(self.color):
            glClearColor(r, g, b, a)
            self.currentColorClear.copy(self.color)

        return self

    def reset(self):
        self.locked = False

        self.currentColorMask = None
        self.currentColorClear.set( - 1, 0, 0, 0 ) # // set to invalid state
        return self


class _DepthBuffer():
    def __init__(self, parent):
        self.locked = False
        self.parent = parent

        self.currentDepthMask = None
        self.currentDepthFunc = None
        self.currentDepthClear = None

    def setTest(self, depthTest):
        if depthTest:
            self.parent.enable(GL_DEPTH_TEST)
        else:
            self.parent.disable(GL_DEPTH_TEST)

    def setMask(self, depthMask):
        if self.currentDepthMask != depthMask and not self.locked:
            glDepthMask( depthMask)
            self.currentDepthMask = depthMask

    def setFunc(self, depthFunc):
        if self.currentDepthFunc != depthFunc:
            if depthFunc:
                if depthFunc == NeverDepth:
                        glDepthFunc(GL_NEVER)
                elif depthFunc == AlwaysDepth:
                        glDepthFunc(GL_ALWAYS)
                elif depthFunc == LessDepth:
                        glDepthFunc(GL_LESS)
                elif depthFunc == LessEqualDepth:
                        glDepthFunc(GL_LEQUAL)
                elif depthFunc == EqualDepth:
                        glDepthFunc(GL_EQUAL)
                elif depthFunc == GreaterEqualDepth:
                        glDepthFunc(GL_GEQUAL)
                elif depthFunc == GreaterDepth:
                        glDepthFunc(GL_GREATER)
                elif depthFunc == NotEqualDepth:
                        glDepthFunc(GL_NOTEQUAL)
                else:
                        glDepthFunc(GL_LEQUAL)
            else:
                glDepthFunc(GL_LEQUAL)

            self.currentDepthFunc = depthFunc

    def setLocked(self, lock):
        self.locked = lock

    def setClear(self, depth):
        if self.currentDepthClear != depth:
            glClearDepth(depth)
            self.currentDepthClear = depth
        return self

    def reset(self):
        self.locked = False
        self.currentDepthMask = None
        self.currentDepthFunc = None
        self.currentDepthClear = None


class _StencilBuffer:
    def __init__(self, parent):
        self.locked = False
        self.parent = parent

        self.currentStencilMask = None
        self.currentStencilFunc = None
        self.currentStencilRef = None
        self.currentStencilFuncMask = None
        self.currentStencilFail = None
        self.currentStencilZFail = None
        self.currentStencilZPass = None
        self.currentStencilClear = None

    def setTest(self, stencilTest):
        if stencilTest:
            self.parent.enable(GL_STENCIL_TEST)
        else:
            self.parent.disable(GL_STENCIL_TEST)

    def setMask(self, stencilMask ):
        if self.currentStencilMask != stencilMask and not self.locked:
            glStencilMask( stencilMask )
            currentStencilMask = stencilMask

    def setFunc(self, stencilFunc, stencilRef, stencilMask ):
        if self.currentStencilFunc != stencilFunc or\
             self.currentStencilRef != stencilRef     or\
             self.currentStencilFuncMask != stencilMask:

            glStencilFunc( stencilFunc, stencilRef, stencilMask )

            self.currentStencilFunc = stencilFunc
            self.currentStencilRef = stencilRef
            self.currentStencilFuncMask = stencilMask

    def setOp(self, stencilFail, stencilZFail, stencilZPass ):
        if self.currentStencilFail     != stencilFail     or\
             self.currentStencilZFail != stencilZFail or\
             self.currentStencilZPass != stencilZPass:

            glStencilOp( stencilFail, stencilZFail, stencilZPass )

            self.currentStencilFail = stencilFail
            self.currentStencilZFail = stencilZFail
            self.currentStencilZPass = stencilZPass

    def setLocked(self, lock ):
        self.locked = lock

    def setClear(self, stencil ):
        if self.currentStencilClear != stencil:
            glClearStencil( stencil )
            self.currentStencilClear = stencil
        return self

    def reset(self):
        self.locked = False

        self.currentStencilMask = None
        self.currentStencilFunc = None
        self.currentStencilRef = None
        self.currentStencilFuncMask = None
        self.currentStencilFail = None
        self.currentStencilZFail = None
        self.currentStencilZPass = None
        self.currentStencilClear = None


class _BoundTexture:
    def __init__(self, type, texture):
        self.type = type
        self.texture = texture
    

class _Buffers:
    def __init__(self, color, depth, stencil):
        self.color = color
        self.depth = depth
        self.stencil = stencil
    
    
def createTexture( type, target, count ):
    data = np.zeros(4, 'B')     # // 4 is required to match default unpack alignment of 4.
    texture = glGenTextures(1)

    glBindTexture(type, texture)
    glTexParameteri(type, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(type, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    for i in range(count):
        glTexImage2D( target + i, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    return texture

    
class pyOpenGLState:
    def __init__(self, extensions, utils, capabilities):
        self.maxVertexAttributes = glGetIntegerv( GL_MAX_VERTEX_ATTRIBS )
        self.newAttributes = [None]
        self.enabledAttributes = [None]
        self.attributeDivisors = [None]

        self.enabledCapabilities = {}

        self.compressedTextureFormats = None

        self.currentProgram = None

        self.currentBlending = None
        self.currentBlendEquation = None
        self.currentBlendSrc = None
        self.currentBlendDst = None
        self.currentBlendEquationAlpha = None
        self.currentBlendSrcAlpha = None
        self.currentBlendDstAlpha = None
        self.currentPremultipledAlpha = False

        self.currentFlipSided = None
        self.currentCullFace = None

        self.currentLineWidth = None

        self.currentPolygonOffsetFactor = None
        self.currentPolygonOffsetUnits = None

        self.currentScissorTest = None

        self.maxTextures = glGetInteger( GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS )

        self.lineWidthAvailable = True

        self.version = float(glGetInteger( GL_MAJOR_VERSION ))+float(glGetInteger( GL_MAJOR_VERSION ))/10
        self.lineWidthAvailable = self.version >= 1.0

        self.currentTextureSlot = None
        self.currentBoundTextures = {}

        self.currentScissor = Vector4()
        self.currentViewport = Vector4()

        self.emptyTextures = {
                GL_TEXTURE_2D: createTexture( GL_TEXTURE_2D, GL_TEXTURE_2D, 1 ),
                GL_TEXTURE_CUBE_MAP: createTexture( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_CUBE_MAP_POSITIVE_X, 6 ),
                GL_TEXTURE_2D_ARRAY: createTexture( GL_TEXTURE_2D, GL_TEXTURE_2D, 1 )
        }

        # // init
        self.colorBuffer = _ColorBuffer().setClear( 0, 0, 0, 1 )
        self.depthBuffer = _DepthBuffer(self).setClear( 1 )
        self.stencilBuffer = _StencilBuffer(self).setClear( 0 )
        self.buffers = _Buffers(self.colorBuffer, self.depthBuffer, self.stencilBuffer)

        self.enable( GL_DEPTH_TEST )
        self.depthBuffer.setFunc( LessEqualDepth )

        self.setFlipSided( False )
        self.setCullFace( CullFaceBack )
        self.enable( GL_CULL_FACE )

        self.enable( GL_BLEND )
        self.setBlending( NormalBlending )

        self.extensions = extensions
        self.utils = utils
        self.capabilities = capabilities

    def initAttributes(self, vao):
        if len(self.newAttributes) < vao + 1:
            for i in range(len(self.newAttributes), vao +1):
                self.newAttributes.append(None)
                self.enabledAttributes.append(None)
                self.attributeDivisors.append(None)
            self.newAttributes[vao] = np.zeros(self.maxVertexAttributes, 'B')
            self.enabledAttributes[vao] = np.zeros(self.maxVertexAttributes, 'B')
            self.attributeDivisors[vao] = np.zeros(self.maxVertexAttributes, 'B')

        self.newAttributes[vao].fill(0)

        # for i in range(len(self.newAttributes)):
        #     self.newAttributes[ i ] = 0

    def enableAttribute(self, attribute, vao):
        self.enableAttributeAndDivisor(attribute, 0, vao)

    def enableAttributeAndDivisor(self, attribute, meshPerAttribute, vao):
        self.newAttributes[vao][attribute] = True

        if not self.enabledAttributes[vao][attribute]:
            glEnableVertexAttribArray(attribute)
            self.enabledAttributes[vao][attribute] = True

        if self.attributeDivisors[vao][attribute] != meshPerAttribute:
            glVertexAttribDivisor(attribute, meshPerAttribute )
            self.attributeDivisors[vao][attribute] = meshPerAttribute

    def disableUnusedAttributes(self, vao):
        for i in range(len(self.enabledAttributes[vao])):
            if self.enabledAttributes[vao][i] and not self.newAttributes[vao][i]:
                glDisableVertexAttribArray(i)
                self.enabledAttributes[vao][i] = False

    def enable(self, id):
        if id not in self.enabledCapabilities:
            self.enabledCapabilities[id] = False

        if not self.enabledCapabilities[id]:
            glEnable(id)
            self.enabledCapabilities[id] = True

    def disable(self, id ):
        if id not in self.enabledCapabilities:
            return

        if self.enabledCapabilities[id]:
            glDisable(id)
            self.enabledCapabilities[id] = False

    def getCompressedTextureFormats(self):
        if self.compressedTextureFormats is None:
            self.compressedTextureFormats = []

            # TODO FDE : what are the other compressed extenstions ?
            # WEBGL_compressed_texture_pvrtc
            # WEBGL_compressed_texture_etc1
            if self.extensions.get( 'GL_EXT_texture_compression_dxt1' ) or\
                 self.extensions.get( 'GL_EXT_texture_compression_s3tc' ) or\
                 self.extensions.get( 'GL_EXT_texture_compression_latc' ) or\
                 self.extensions.get( 'WEBGL_compressed_texture_astc'):

                n = glGetIntegerv(GL_NUM_COMPRESSED_TEXTURE_FORMATS)
                formats = arrays.GLintArray.zeros((n,))
                glGetIntegerv(GL_COMPRESSED_TEXTURE_FORMATS, formats)

                for format in formats:
                    self.compressedTextureFormats.append( format )

        return self.compressedTextureFormats

    def useProgram(self, program ):
        if self.currentProgram != program:
            glUseProgram( program )
            self.currentProgram = program
            return True

        return False

    def setBlending(self, blending=None, blendEquation=None, blendSrc=None, blendDst=None, blendEquationAlpha=None, blendSrcAlpha=None, blendDstAlpha=None, premultipliedAlpha=None ):
        if blending != NoBlending:
            self.enable( GL_BLEND )
        else:
            self.disable( GL_BLEND )

        if blending != CustomBlending:
            if blending != self.currentBlending or premultipliedAlpha != self.currentPremultipledAlpha:
                if blending == AdditiveBlending:
                    if premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ONE, gl.ONE, GL_ONE, GL_ONE )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_SRC_ALPHA, GL_ONE )
                elif blending == SubtractiveBlending:
                    if premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ZERO, GL_ZERO, GL_ONE_MINUS_SRC_COLOR, GL_ONE_MINUS_SRC_ALPHA )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_ZERO, GL_ONE_MINUS_SRC_COLOR )
                elif blending == MultiplyBlending:
                    if premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ZERO, GL_SRC_COLOR, GL_ZERO, GLSRC_ALPHA )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_ZERO, GL_SRC_COLOR )
                else:
                    if premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ONE, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA )
                    else:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA )


            self.currentBlendEquation = None
            self.currentBlendSrc = None
            self.currentBlendDst = None
            self.currentBlendEquationAlpha = None
            self.currentBlendSrcAlpha = None
            self.currentBlendDstAlpha = None
        else:
            blendEquationAlpha = blendEquationAlpha or blendEquation
            blendSrcAlpha = blendSrcAlpha or blendSrc
            blendDstAlpha = blendDstAlpha or blendDst

            if blendEquation != self.currentBlendEquation or blendEquationAlpha != self.currentBlendEquationAlpha:
                glBlendEquationSeparate( self.utils.convert( blendEquation ), self.utils.convert( blendEquationAlpha ) )

                self.currentBlendEquation = blendEquation
                self.currentBlendEquationAlpha = blendEquationAlpha

            if blendSrc != self.currentBlendSrc or blendDst != self.currentBlendDst or blendSrcAlpha != self.currentBlendSrcAlpha or blendDstAlpha != self.currentBlendDstAlpha:
                glBlendFuncSeparate( self.utils.convert( blendSrc ), self.utils.convert( blendDst ), self.utils.convert( blendSrcAlpha ), self.utils.convert( blendDstAlpha ) )

                self.currentBlendSrc = blendSrc
                self.currentBlendDst = blendDst
                self.currentBlendSrcAlpha = blendSrcAlpha
                self.currentBlendDstAlpha = blendDstAlpha

        self.currentBlending = blending
        self.currentPremultipledAlpha = premultipliedAlpha

    def setMaterial( self, material, frontFaceCW):
        if material.side == DoubleSide:
            self.disable( GL_CULL_FACE )
        else:
            self.enable( GL_CULL_FACE )

        flipSided = ( material.side == BackSide )
        #FIXME look at pyOpenGLRenderer:500
        #the frontFaceCW is now computer on the GPU
        if frontFaceCW:
           flipSided = not flipSided
        #if flipSided:
        #    self.setCullFace(CullFaceFront)
        #else:
        #    self.setCullFace(CullFaceBack)

        self.setFlipSided(flipSided)

        if material.blending == NormalBlending and not material.transparent:
            self.setBlending(NoBlending)
        else:
            self.setBlending(material.blending, material.blendEquation, material.blendSrc, material.blendDst,
                      material.blendEquationAlpha, material.blendSrcAlpha, material.blendDstAlpha,
                      material.premultipliedAlpha)

        self.depthBuffer.setFunc( material.depthFunc )
        self.depthBuffer.setTest( material.depthTest )
        self.depthBuffer.setMask( material.depthWrite )
        self.colorBuffer.setMask( material.colorWrite )

        self.setPolygonOffset( material.polygonOffset, material.polygonOffsetFactor, material.polygonOffsetUnits )

    def setFlipSided(self, flipSided ):
        if self.currentFlipSided != flipSided:
            if flipSided:
                glFrontFace( GL_CW )
            else:
                glFrontFace( GL_CCW )

            self.currentFlipSided = flipSided

    def setCullFace(self, cullFace ):
        if cullFace != CullFaceNone:
            self.enable( GL_CULL_FACE )
            if cullFace != self.currentCullFace:
                if cullFace == CullFaceBack:
                    glCullFace( GL_BACK )
                elif cullFace == CullFaceFront:
                    glCullFace( GL_FRONT )
                else:
                    glCullFace( GL_FRONT_AND_BACK )
        else:
            self.disable( GL_CULL_FACE )

        self.currentCullFace = cullFace

    def setLineWidth(self, width ):
        if width != self.currentLineWidth:
            if self.lineWidthAvailable:
                glLineWidth( width )

            self.currentLineWidth = width

    def setPolygonOffset(self, polygonOffset, factor=None, units=None):
        if polygonOffset:
            self.enable( GL_POLYGON_OFFSET_FILL )
            if self.currentPolygonOffsetFactor != factor or self.currentPolygonOffsetUnits != units:
                glPolygonOffset( factor, units )

                self.currentPolygonOffsetFactor = factor
                self.currentPolygonOffsetUnits = units
        else:
            self.disable( GL_POLYGON_OFFSET_FILL )

    def getScissorTest(self):
        return self.currentScissorTest

    def setScissorTest(self, scissorTest ):
        self.currentScissorTest = scissorTest

        if scissorTest:
            self.enable( GL_SCISSOR_TEST )
        else:
            self.disable( GL_SCISSOR_TEST )

    # // texture

    def activeTexture(self, webglSlot=None ):
        if webglSlot is None:
            webglSlot = GL_TEXTURE0 + self.maxTextures - 1

        if self.currentTextureSlot != webglSlot:
            OpenGL.raw.GL.VERSION.GL_1_3.glActiveTexture( webglSlot )
            self.currentTextureSlot = webglSlot

    def bindTexture(self, webglType, webglTexture ):
        if self.currentTextureSlot is None:
            self.activeTexture()

        if self.currentTextureSlot not in self.currentBoundTextures:
            boundTexture = _BoundTexture(None, None)
            self.currentBoundTextures[self.currentTextureSlot] = boundTexture
        else:
            boundTexture = self.currentBoundTextures[ self.currentTextureSlot ]

        if boundTexture.type != webglType or boundTexture.texture != webglTexture:
            OpenGL.raw.GL.VERSION.GL_1_1.glBindTexture( webglType, webglTexture or self.emptyTextures[ webglType ] )

            boundTexture.type = webglType
            boundTexture.texture = webglTexture

    @staticmethod
    def compressedTexImage2D(target, level, glFormat, width, height, border, data):
        glCompressedTexImage2D(target, level, glFormat, width, height, border, data.size, data)

    @staticmethod
    def texImage2D(target, level, internalFormat, width, height, border, format, type, data):
        OpenGL.raw.GL.VERSION.GL_1_0.glTexImage2D(target, level, internalFormat, width, height, border, format, type, data)

    @staticmethod
    def texImage2Df(target, level, internalFormat, border, format, data):
        glTexImage2Df(target, level, internalFormat, border, format, data)

    def scissor(self, scissor ):
        if not self.currentScissor.equals( scissor ):
            glScissor( int(scissor.x), int(scissor.y), int(scissor.z), int(scissor.w) )
            self.currentScissor.copy( scissor )

    def viewport(self, viewport ):
        if not self.currentViewport.equals( viewport ):
            glViewport( int(viewport.x), int(viewport.y), int(viewport.z), int(viewport.w) )
            self.currentViewport.copy( viewport )

    def reset(self):
        for i in range(len(self.enabledAttributes)):
            if self.enabledAttributes[ i ] == 1:
                glDisableVertexAttribArray( i )
                self.enabledAttributes[ i ] = 0

        self.enabledCapabilities = {}

        self.compressedTextureFormats = None

        self.currentTextureSlot = None
        self.currentBoundTextures = {}

        self.currentProgram = None

        self.currentBlending = None

        self.currentFlipSided = None
        self.currentCullFace = None

        self.colorBuffer.reset()
        self.depthBuffer.reset()
        self.stencilBuffer.reset()
