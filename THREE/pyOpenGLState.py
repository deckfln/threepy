"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from array import *
import re
from OpenGL.GL import *
from THREE.Constants import *
from THREE.Vector4 import *


class _ColorBuffer:
    def __init__(self):
        self.locked = False

        self.color = Vector4()
        self.currentColorMask = None
        self.currentColorClear = Vector4( 0, 0, 0, 0 )

    def setMask(self, colorMask ):
        if  self.currentColorMask != colorMask and not self.locked:
            glColorMask( colorMask, colorMask, colorMask, colorMask )
            self.currentColorMask = colorMask

    def setLocked(self, lock ):
        self.locked = lock

    def setClear(self, r, g, b, a, premultipliedAlpha=None ):
        if  premultipliedAlpha:
            r *= a; g *= a; b *= a

        self.color.set( r, g, b, a )

        if  not self.currentColorClear.equals( self.color ):
            glClearColor( r, g, b, a )
            self.currentColorClear.copy( self.color )

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

    def setTest(self, depthTest ):
        if  depthTest:
            self.parent.enable( GL_DEPTH_TEST )
        else:
            self.parent.disable( GL_DEPTH_TEST )

    def setMask(self, depthMask ):
        if  self.currentDepthMask != depthMask and not self.locked:
            glDepthMask( depthMask )
            self.currentDepthMask = depthMask

    def setFunc(self, depthFunc ):
        if self.currentDepthFunc != depthFunc:
            if depthFunc:
                if depthFunc == NeverDepth:
                        glDepthFunc( GL_NEVER )
                elif depthFunc == AlwaysDepth:
                        glDepthFunc( GL_ALWAYS )
                elif depthFunc == LessDepth:
                        glDepthFunc( GL_LESS )
                elif depthFunc == LessEqualDepth:
                        glDepthFunc( GL_LEQUAL )
                elif depthFunc == EqualDepth:
                        glDepthFunc( GL_EQUAL )
                elif depthFunc == GreaterEqualDepth:
                        glDepthFunc( GL_GEQUAL )
                elif depthFunc == GreaterDepth:
                        glDepthFunc( GL_GREATER )
                elif depthFunc == NotEqualDepth:
                        glDepthFunc( GL_NOTEQUAL )
                else:
                        glDepthFunc( GL_LEQUAL )
            else:
                glDepthFunc( GL_LEQUAL )

            self.currentDepthFunc = depthFunc

    def setLocked(self, lock ):
        locked = lock

    def setClear(self, depth ):
        if  self.currentDepthClear != depth:
            glClearDepth( depth )
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

    def setTest(self, stencilTest ):
        if  stencilTest:
            self.parent.enable( GL_STENCIL_TEST )
        else:
            self.parent.disable( GL_STENCIL_TEST )

    def setMask(self, stencilMask ):
        if  self.currentStencilMask != stencilMask and not self.locked:
            glStencilMask( stencilMask )
            currentStencilMask = stencilMask

    def setFunc(self, stencilFunc, stencilRef, stencilMask ):
        if  self.currentStencilFunc != stencilFunc or\
             self.currentStencilRef != stencilRef     or\
             self.currentStencilFuncMask != stencilMask:

            glStencilFunc( stencilFunc, stencilRef, stencilMask )

            self.currentStencilFunc = stencilFunc
            self.currentStencilRef = stencilRef
            self.currentStencilFuncMask = stencilMask

    def setOp(self, stencilFail, stencilZFail, stencilZPass ):
        if  self.currentStencilFail     != stencilFail     or\
             self.currentStencilZFail != stencilZFail or\
             self.currentStencilZPass != stencilZPass:

            glStencilOp( stencilFail, stencilZFail, stencilZPass )

            self.currentStencilFail = stencilFail
            self.currentStencilZFail = stencilZFail
            self.currentStencilZPass = stencilZPass

    def setLocked(self, lock ):
        self.locked = lock

    def setClear(self, stencil ):
        if  self.currentStencilClear != stencil:
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
    data = array('B', 4 )     # // 4 is required to match default unpack alignment of 4.
    texture = glCreateTextures(1)

    glBindTexture( type, texture )
    glTexParameteri( type, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
    glTexParameteri( type, GL_TEXTURE_MAG_FILTER, GL_NEAREST )

    for i in range(count):
        glTexImage2D( target + i, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, data )

    return texture

    
class pyOpenGLState:
    def __init__(self, extensions, utils):
        maxVertexAttributes = glGetIntegerv( GL_MAX_VERTEX_ATTRIBS )
        self.newAttributes = array('B', maxVertexAttributes )
        self.enabledAttributes = array('B', maxVertexAttributes )
        self.attributeDivisors = array('B', maxVertexAttributes )

        self.capabilities = {}

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

        self.version = float(glGetInteger( GL_MAJOR_VERSION ))+float(glGetInteger( GL_MAJOR_VERSION ))/10
        self.lineWidthAvailable = self.version >= 1.0

        self.currentTextureSlot = None
        self.currentBoundTextures = {}

        self.currentScissor = Vector4()
        self.currentViewport = Vector4()

        self.emptyTextures = {
                GL_TEXTURE_2D: createTexture( GL_TEXTURE_2D, GL_TEXTURE_2D, 1 ),
                GL_TEXTURE_CUBE_MAP: createTexture( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_CUBE_MAP_POSITIVE_X, 6 )
        }

        # // init
        self.colorBuffer = _ColorBuffer(self).setClear( 0, 0, 0, 1 )
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

    def initAttributes(self):
        for i in range(len(self.newAttributes)):
            self.newAttributes[ i ] = 0

    def enableAttribute(self, attribute ):
        self.newAttributes[ attribute ] = 1

        if self.enabledAttributes[ attribute ] == 0:
            glEnableVertexAttribArray( attribute )
            self.enabledAttributes[ attribute ] = 1

        if self.attributeDivisors[ attribute ] != 0:
            extension = extensions.get( 'ANGLE_instanced_arrays' )

            extension.vertexAttribDivisorANGLE( attribute, 0 )
            self.attributeDivisors[ attribute ] = 0

    def enableAttributeAndDivisor(self, attribute, meshPerAttribute ):
        self.newAttributes[ attribute ] = 1

        if  self.enabledAttributes[ attribute ] == 0:
            glEnableVertexAttribArray( attribute )
            self.enabledAttributes[ attribute ] = 1

        if self.attributeDivisors[ attribute ] != meshPerAttribute:
            extension = extensions.get( 'ANGLE_instanced_arrays' )

            extension.vertexAttribDivisorANGLE( attribute, meshPerAttribute )
            self.attributeDivisors[ attribute ] = meshPerAttribute

    def disableUnusedAttributes(self):
        for i in range(len(self.enabledAttributes)):
            if  self.enabledAttributes[ i ] != self.newAttributes[ i ]:
                glDisableVertexAttribArray( i )
                self.enabledAttributes[ i ] = 0

    def enable(self, id ):
        if not self.capabilities[ id ] != True:
            glEnable( id )
            self.capabilities[ id ] = True

    def disable(self, id ):
        if  self.capabilities[ id ] != False:
            glDisable( id )
            self.capabilities[ id ] = False

    def getCompressedTextureFormats(self):
        if  self.compressedTextureFormats is None:
            self.compressedTextureFormats = []

            if  extensions.get( 'WEBGL_compressed_texture_pvrtc' ) or\
                 extensions.get( 'WEBGL_compressed_texture_s3tc' ) or\
                 extensions.get( 'WEBGL_compressed_texture_etc1' ):
                formats = glGetIntegerv( GL_COMPRESSED_TEXTURE_FORMATS )

                for i in range(len(formats)):
                    self.compressedTextureFormats.append( formats[ i ] )

        return self.compressedTextureFormats

    def useProgram(self, program ):
        if  self.currentProgram != program:
            glUseProgram( program )
            self.currentProgram = program
            return True

        return False

    def setBlending(self, blending=None, blendEquation=None, blendSrc=None, blendDst=None, blendEquationAlpha=None, blendSrcAlpha=None, blendDstAlpha=None, premultipliedAlpha=None ):
        if  blending != NoBlending:
            self.enable( GL_BLEND )
        else:
            self.disable( GL_BLEND )

        if  blending != CustomBlending:
            if  blending != self.currentBlending or premultipliedAlpha != self.currentPremultipledAlpha:
                if blending == AdditiveBlending:
                    if  premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ONE, gl.ONE, GL_ONE, GL_ONE )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_SRC_ALPHA, GL_ONE )
                elif blending == SubtractiveBlending:
                    if  premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ZERO, GL_ZERO, GL_ONE_MINUS_SRC_COLOR, GL_ONE_MINUS_SRC_ALPHA )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_ZERO, GL_ONE_MINUS_SRC_COLOR )
                elif blending == MultiplyBlending:
                    if  premultipliedAlpha:
                        glBlendEquationSeparate( GL_FUNC_ADD, GL_FUNC_ADD )
                        glBlendFuncSeparate( GL_ZERO, GL_SRC_COLOR, GL_ZERO, GLSRC_ALPHA )
                    else:
                        glBlendEquation( GL_FUNC_ADD )
                        glBlendFunc( GL_ZERO, GL_SRC_COLOR )
                else:
                    if  premultipliedAlpha:
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

            if  blendEquation != self.currentBlendEquation or blendEquationAlpha != self.currentBlendEquationAlpha:
                glBlendEquationSeparate( utils.convert( blendEquation ), utils.convert( blendEquationAlpha ) )

                self.currentBlendEquation = blendEquation
                self.currentBlendEquationAlpha = blendEquationAlpha

            if  blendSrc != self.currentBlendSrc or blendDst != self.currentBlendDst or blendSrcAlpha != self.currentBlendSrcAlpha or blendDstAlpha != self.currentBlendDstAlpha:
                glBlendFuncSeparate( utils.convert( blendSrc ), utils.convert( blendDst ), utils.convert( blendSrcAlpha ), utils.convert( blendDstAlpha ) )

                self.currentBlendSrc = blendSrc
                self.currentBlendDst = blendDst
                self.currentBlendSrcAlpha = blendSrcAlpha
                self.currentBlendDstAlpha = blendDstAlpha

        self.currentBlending = blending
        self.currentPremultipledAlpha = premultipliedAlpha

    def setMaterial( self, material ):
        if material.side == DoubleSide:
            self.disable( GL_CULL_FACE )
        else:
            self.enable( GL_CULL_FACE )

        self.setFlipSided( material.side == BackSide )

        if material.transparent:
            self.setBlending( material.blending, material.blendEquation, material.blendSrc, material.blendDst, material.blendEquationAlpha, material.blendSrcAlpha, material.blendDstAlpha, material.premultipliedAlpha )
        else:
            self.setBlending( NoBlending )

        self.depthBuffer.setFunc( material.depthFunc )
        self.depthBuffer.setTest( material.depthTest )
        self.depthBuffer.setMask( material.depthWrite )
        self.colorBuffer.setMask( material.colorWrite )

        self.setPolygonOffset( material.polygonOffset, material.polygonOffsetFactor, material.polygonOffsetUnits )

    def setFlipSided(self, flipSided ):
        if self.currentFlipSided != flipSided:
            if  flipSided:
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
        if  width != self.currentLineWidth:
            if self.lineWidthAvailable:
                glLineWidth( width )

            self.currentLineWidth = width

    def setPolygonOffset(self, polygonOffset, factor, units ):
        if  polygonOffset:
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

        if  scissorTest:
            self.enable( GL_SCISSOR_TEST )
        else:
            self.disable( GL_SCISSOR_TEST )

    # // texture

    def activeTexture(self, webglSlot ):
        if  webglSlot is None:
            webglSlot = GL_TEXTURE0 + maxTextures - 1

        if  self.currentTextureSlot != webglSlot:
            glActiveTexture( webglSlot )
            self.currentTextureSlot = webglSlot

    def bindTexture(self, webglType, webglTexture ):
        if self.currentTextureSlot is None:
            self.activeTexture()

        boundTexture = self.currentBoundTextures[ self.currentTextureSlot ]

        if  boundTexture is None:
            boundTexture = _BoundTexture(None, None)
            self.currentBoundTextures[ self.currentTextureSlot ] = boundTexture

        if  boundTexture.type != webglType or boundTexture.texture != webglTexture:
            glBindTexture( webglType, webglTexture or self.emptyTextures[ webglType ] )

            boundTexture.type = webglType
            boundTexture.texture = webglTexture

    def compressedTexImage2D(self):
        try:
            glCompressedTexImage2D.apply( gl, arguments )
        except:
            raise( 'THREE.WebGLState:', error )

    def texImage2D(self):
        try:
            glTexImage2D.apply( gl, arguments )
        except:
            raise( 'THREE.WebGLState:', error )

    def scissor(self, scissor ):
        if not self.currentScissor.equals( scissor ):
            glScissor( scissor.x, scissor.y, scissor.z, scissor.w )
            self.currentScissor.copy( scissor )

    def viewport(self, viewport ):
        if  not self.currentViewport.equals( viewport ):
            glViewport( viewport.x, viewport.y, viewport.z, viewport.w )
            self.currentViewport.copy( viewport )

    def reset(self):
        for i in range(len(self.enabledAttributes)):
            if  self.enabledAttributes[ i ] == 1:
                glDisableVertexAttribArray( i )
                self.enabledAttributes[ i ] = 0

        self.capabilities = {}

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
