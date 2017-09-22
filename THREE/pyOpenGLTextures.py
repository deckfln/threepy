"""
    /**
     * @author mrdoob / http:# //mrdoob.com/
     */
"""
from OpenGL.GL import *
import THREE._Math as _Math
from THREE.Constants import *
import PIL
from PIL import Image
import numpy


def _clampToMaxSize(image, maxSize):
    if image.width > maxSize or image.height > maxSize:
        # // Warning: Scaling through the canvas will only work with images that use
        # // premultiplied alpha.
        scale = maxSize / max(image.width, image.height)

        w = int(math.floor(image.width * scale))
        h = int(math.floor(image.height * scale))

        im = image.resize((w, h), PIL.Image.BICUBIC)

        print('THREE.WebGLRenderer: image is too big (%d, %d). Resized to (%d,%d)' % (image.width, image.height, w, h))

        return im

    return image


def _isPowerOfTwo(image):
    return _Math.isPowerOfTwo(image.width) and _Math.isPowerOfTwo(image.height)


def _makePowerOfTwo(image):
    w = int(_Math.nearestPowerOfTwo(image.width))
    h = int(_Math.nearestPowerOfTwo(image.height))

    im = image.resize((w, h), PIL.Image.BICUBIC)

    print('THREE.WebGLRenderer: image is not power of 2 (%d, %d). Resized to (%d,%d)' % (image.width, image.height, w, h))

    return im

def _textureNeedsPowerOfTwo(texture):
    return (texture.wrapS != ClampToEdgeWrapping or texture.wrapT != ClampToEdgeWrapping) or \
           (texture.minFilter != NearestFilter and texture.minFilter != LinearFilter)


def _textureNeedsGenerateMipmaps(texture, isPowerOfTwo):
    return texture.generateMipmaps and isPowerOfTwo and \
           texture.minFilter != NearestFilter and texture.minFilter != LinearFilter


# // Fallback filters for non-power-of-2 textures

def _filterFallback(f):
    if f == NearestFilter or f == NearestMipMapNearestFilter or f == NearestMipMapLinearFilter:
        return GL_NEAREST
    return GL_LINEAR


class pyOpenGLTextures():
    def __init__( self, extensions, state, properties, capabilities, utils, infoMemory ):
        self.extensions = extensions
        self.state = state
        self.properties = properties
        self.capabilities = capabilities
        self.utils = utils
        self.infoMemory = infoMemory

        # //

        # //

    def onTextureDispose(self, event ):
        texture = event.target
        texture.removeEventListener( 'dispose', onTextureDispose )
        self.deallocateTexture( texture )
        self.infoMemory.textures -= 1

    def onRenderTargetDisposeself(self, event ):
        renderTarget = event.target
        renderTarget.removeEventListener( 'dispose', onRenderTargetDispose )
        self.deallocateRenderTarget( renderTarget )
        self.infoMemory.textures -= 1

        # //

    def deallocateTexture(self, texture ):
        textureProperties = self.properties.get( texture )

        if texture.image and textureProperties.__imageopenglTextureCube:
            # // cube texture
            glDeleteTextures(1, textureProperties.__imageopenglTextureCube )
        else:
            # // 2D texture
            if textureProperties.__webglInit is None:
                return

            glDeleteTextures(1, textureProperties.openglTexture )

        # // remove all webgl properties
        self.properties.remove( texture )

    def deallocateRenderTarget(self, renderTarget ):
        renderTargetProperties = self.properties.get( renderTarget )
        textureProperties = self.properties.get( renderTarget.texture )

        if not renderTarget:
            return

        if textureProperties.openglTexture is not None:
            glDeleteTextures(1, textureProperties.openglTexture )

        if renderTarget.depthTexture:
            renderTarget.depthTexture.dispose()

        if renderTarget.isWebGLRenderTargetCube:
            for i in range(6):
                glDeleteFramebuffers(1, renderTargetProperties.__webglFramebuffer[ i ] )
                if renderTargetProperties.__webglDepthbuffer:
                    glDeleteRenderbuffers(1, renderTargetProperties.__webglDepthbuffer[ i ] )
        else:
            glDeleteFramebuffers(1, renderTargetProperties.__webglFramebuffer )
            if renderTargetProperties.__webglDepthbuffer:
                glDeleteRenderbuffers(1, renderTargetProperties.__webglDepthbuffer )

        self.properties.remove( renderTarget.texture )
        self.properties.remove( renderTarget )

    def setTextureParameters(self, textureType, texture, isPowerOfTwoImage ):
        if isPowerOfTwoImage:
            glTexParameteri( textureType, GL_TEXTURE_WRAP_S, self.utils.convert( texture.wrapS ) )
            glTexParameteri( textureType, GL_TEXTURE_WRAP_T, self.utils.convert( texture.wrapT ) )

            glTexParameteri( textureType, GL_TEXTURE_MAG_FILTER, self.utils.convert( texture.magFilter ) )
            glTexParameteri( textureType, GL_TEXTURE_MIN_FILTER, self.utils.convert( texture.minFilter ) )

        else:
            glTexParameteri( textureType, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
            glTexParameteri( textureType, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )

            if texture.wrapS != ClampToEdgeWrapping or texture.wrapT != ClampToEdgeWrapping:
                raise RuntimeWarning( 'THREE.WebGLRenderer: Texture is not power of two. Texture.wrapS and Texture.wrapT should be set to THREE.ClampToEdgeWrapping.', texture )

            glTexParameteri( textureType, GL_TEXTURE_MAG_FILTER, _filterFallback( texture.magFilter ) )
            glTexParameteri( textureType, GL_TEXTURE_MIN_FILTER, _filterFallback( texture.minFilter ) )

            if texture.minFilter != NearestFilter and texture.minFilter != LinearFilter:
                raise RuntimeWarning( 'THREE.WebGLRenderer: Texture is not power of two. Texture.minFilter should be set to THREE.NearestFilter or THREE.LinearFilter.', texture )

        extension = self.extensions.get( 'EXT_texture_filter_anisotropic' )

        if extension:
            if texture.type == FloatType and self.extensions.get( 'OES_texture_float_linear' ) is None:
                return
            if texture.type == HalfFloatType and self.extensions.get( 'OES_texture_half_float_linear' ) is None:
                return

            if texture.anisotropy > 1 or self.properties.get( texture ).currentAnisotropy:
                glTexParameterf( textureType, extension.TEXTURE_MAX_ANISOTROPY_EXT, min( texture.anisotropy, self.capabilities.getMaxAnisotropy() ) )
                self.properties.get( texture ).currentAnisotropy = texture.anisotropy

    def uploadTexture(self, textureProperties, texture, slot ):
        if not textureProperties.openglInit:
            textureProperties.openglInit = True

            texture.onDispose(self.onTextureDispose )

            textureProperties.openglTexture = glGenTextures(1)

            self.infoMemory.textures +=1

        self.state.activeTexture( GL_TEXTURE0 + slot )
        self.state.bindTexture( GL_TEXTURE_2D, textureProperties.openglTexture )

        # glPixelStorei( GL_UNPACK_FLIP_Y_WEBGL, texture.flipY )
        # glPixelStorei( GL_UNPACK_PREMULTIPLY_ALPHA_WEBGL, texture.premultiplyAlpha )
        glPixelStorei( GL_UNPACK_ALIGNMENT, texture.unpackAlignment )

        image = _clampToMaxSize( texture.image, self.capabilities.maxTextureSize )

        if _textureNeedsPowerOfTwo( texture ) and _isPowerOfTwo( image ) == False:
            image = _makePowerOfTwo( image )

        isPowerOfTwoImage = _isPowerOfTwo( image )
        glFormat = self.utils.convert( texture.format )
        glType = self.utils.convert( texture.type )

        self.setTextureParameters( GL_TEXTURE_2D, texture, isPowerOfTwoImage )

        mipmaps = texture.mipmaps

        if texture.isDepthTexture:
            # // populate depth texture with dummy data

            internalFormat = GL_DEPTH_COMPONENT

            if texture.type == FloatType:
                internalFormat = GL_DEPTH_COMPONENT32F
            else:
                # // WebGL 2.0 requires signed internalformat for glTexImage2D
                internalFormat = GL_DEPTH_COMPONENT16

            if texture.format == DepthFormat and internalFormat == GL_DEPTH_COMPONENT:
                # // The error INVALID_OPERATION is generated by texImage2D if format and internalformat are
                # // DEPTH_COMPONENT and type is not UNSIGNED_SHORT or UNSIGNED_INT
                # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

                if texture.type != UnsignedShortType and texture.type != UnsignedIntType:
                    print( 'THREE.WebGLRenderer: Use UnsignedShortType or UnsignedIntType for DepthFormat DepthTexture.' )

                    texture.type = UnsignedShortType
                    glType = self.utils.convert( texture.type )

            # // Depth stencil textures need the DEPTH_STENCIL internal format
            # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

            if texture.format == DepthStencilFormat:
                internalFormat = GL_DEPTH_STENCIL

                # // The error INVALID_OPERATION is generated by texImage2D if format and internalformat are
                # // DEPTH_STENCIL and type is not UNSIGNED_INT_24_8_WEBGL.
                # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

                if texture.type != UnsignedInt248Type:
                    print( 'THREE.WebGLRenderer: Use UnsignedInt248Type for DepthStencilFormat DepthTexture.' )

                    texture.type = UnsignedInt248Type
                    glType = self.utils.convert( texture.type )

            self.state.texImage2D( GL_TEXTURE_2D, 0, internalFormat, image.width, image.height, 0, glFormat, glType, None )

        elif texture.isDataTexture:
            # // use manually created mipmaps if available
            # // if there are no manual mipmaps
            # // set 0 level mipmap and then use GL to generate other mipmap levels

            if mipmaps.length > 0 and isPowerOfTwoImage:
                for i in range(len(mipmaps)):
                    mipmap = mipmaps[ i ]
                    self.state.texImage2D( GL_TEXTURE_2D, i, glFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data )

                texture.generateMipmaps = False

            else:
                self.state.texImage2D( GL_TEXTURE_2D, 0, glFormat, image.width, image.height, 0, glFormat, glType, image.data )

        elif texture.isCompressedTexture:
            for i in range(len(mipmaps)):
                mipmap = mipmaps[ i ]

                if texture.format != RGBAFormat and texture.format != RGBFormat:
                    if self.state.getCompressedTextureFormats().indexOf( glFormat ) > - 1:
                        self.state.compressedTexImage2D( GL_TEXTURE_2D, i, glFormat, mipmap.width, mipmap.height, 0, mipmap.data )
                    else:
                        raise RuntimeWarning( 'THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()' )

                else:
                    self.state.texImage2D( GL_TEXTURE_2D, i, glFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data )

        else:
            # // regular Texture (image, video, canvas)

            # // use manually created mipmaps if available
            # // if there are no manual mipmaps
            # // set 0 level mipmap and then use GL to generate other mipmap levels

            if len(mipmaps) > 0 and isPowerOfTwoImage:
                for i in range(len(mipmaps)):
                    mipmap = mipmaps[ i ]
                    self.state.texImage2D( GL_TEXTURE_2D, i, glFormat, image.width, image.height, 0, glFormat, glType, mipmap )

                texture.generateMipmaps = False

            else:
                img_data = numpy.fromstring(image.tobytes(), numpy.uint8)
                width, height = image.size
                self.state.texImage2D(GL_TEXTURE_2D, 0, glFormat,  width, height, 0, glFormat, glType, img_data)

        if _textureNeedsGenerateMipmaps( texture, isPowerOfTwoImage ):
            glGenerateMipmap( GL_TEXTURE_2D )

        textureProperties.version = texture.version

        if texture.onUpdate:
            texture.onUpdate( texture )

    # // Render targets

    # // Setup storage for target texture and bind it to correct framebuffer

    def setupFrameBufferTexture(self, framebuffer, renderTarget, attachment, textureTarget ):
        glFormat = self.utils.convert( renderTarget.texture.format )
        glType = self.utils.convert( renderTarget.texture.type )
        self.state.texImage2D( textureTarget, 0, glFormat, renderTarget.width, renderTarget.height, 0, glFormat, glType, None )
        glBindFramebuffer( GL_FRAMEBUFFER, framebuffer )
        glFramebufferTexture2D( GL_FRAMEBUFFER, attachment, textureTarget, self.properties.get( renderTarget.texture ).openglTexture, 0 )
        glBindFramebuffer( GL_FRAMEBUFFER, 0 )

    # // Setup storage for internal depth/stencil buffers and bind to correct framebuffer
    def setupRenderBufferStorage(self, renderbuffer, renderTarget ):
        glBindRenderbuffer( GL_RENDERBUFFER, renderbuffer )

        if renderTarget.depthBuffer and not renderTarget.stencilBuffer:
            glRenderbufferStorage( GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, renderTarget.width, renderTarget.height )
            glFramebufferRenderbuffer( GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, renderbuffer )

        elif renderTarget.depthBuffer and renderTarget.stencilBuffer:
            glRenderbufferStorage( GL_RENDERBUFFER, GL_DEPTH_STENCIL, renderTarget.width, renderTarget.height )
            glFramebufferRenderbuffer( GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, renderbuffer )

        else:
            # // FIXME: We don't support !depth !stencil
            glRenderbufferStorage( GL_RENDERBUFFER, GL_RGBA4, renderTarget.width, renderTarget.height )

        glBindRenderbuffer( GL_RENDERBUFFER, None )

    # // Setup resources for a Depth Texture for a FBO (needs an extension)
    def setupDepthTexture(self, framebuffer, renderTarget ):
        isCube = ( renderTarget and renderTarget.isWebGLRenderTargetCube )
        if isCube:
            raise RuntimeError( 'Depth Texture with cube render targets is not supported' )

        glBindFramebuffer( GL_FRAMEBUFFER, framebuffer )

        if not( renderTarget.depthTexture and renderTarget.depthTexture.isDepthTexture ):
            raise RuntimeError( 'renderTarget.depthTexture must be an instance of THREE.DepthTexture' )

        # // upload an empty depth texture with framebuffer size
        if not self.properties.get( renderTarget.depthTexture ).openglTexture or \
                renderTarget.depthTexture.image.width != renderTarget.width or \
                renderTarget.depthTexture.image.height != renderTarget.height:
            renderTarget.depthTexture.image.width = renderTarget.width
            renderTarget.depthTexture.image.height = renderTarget.height
            renderTarget.depthTexture.needsUpdate = True

        self.setTexture2D( renderTarget.depthTexture, 0 )

        webglDepthTexture = self.properties.get( renderTarget.depthTexture ).openglTexture

        if renderTarget.depthTexture.format == DepthFormat:
            glFramebufferTexture2D( GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, webglDepthTexture, 0 )

        elif renderTarget.depthTexture.format == DepthStencilFormat:
            glFramebufferTexture2D( GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, webglDepthTexture, 0 )

        else:
            raise RuntimeError( 'Unknown depthTexture format' )

    # // Setup GL resources for a non-texture depth buffer
    def setupDepthRenderbuffer(self, renderTarget ):
        renderTargetProperties = self.properties.get( renderTarget )

        isCube = ( renderTarget.isWebGLRenderTargetCube == True )

        if renderTarget.depthTexture:

            if isCube:
                raise RuntimeError( 'target.depthTexture not supported in Cube render targets' )

            self.setupDepthTexture( renderTargetself.properties.__webglFramebuffer, renderTarget )

        else:
            if isCube:
                renderTargetProperties.__webglDepthbuffer = []

                for i in range(6):
                    glBindFramebuffer( GL_FRAMEBUFFER, renderTargetProperties.__webglFramebuffer[ i ] )
                    renderTargetProperties.__webglDepthbuffer[ i ] = glCreateRenderbuffers(1)
                    self.setupRenderBufferStorage( renderTargetProperties.__webglDepthbuffer[ i ], renderTarget )

            else:
                glBindFramebuffer( GL_FRAMEBUFFER, renderTargetProperties.__webglFramebuffer )
                renderTargetProperties.__webglDepthbuffer = glCreateRenderbuffers(1)
                self.setupRenderBufferStorage( renderTargetProperties.__webglDepthbuffer, renderTarget )

        glBindFramebuffer( GL_FRAMEBUFFER, 0 )

    # //

    def setTexture2D(self, texture, slot ):
        textureProperties = self.properties.get( texture )

        if texture.version > 0 and textureProperties.version != texture.version:
            image = texture.image

            if image is None:
                raise RuntimeWarning( 'THREE.WebGLRenderer: Texture marked for update but image is undefined', texture )
            else:
                self.uploadTexture( textureProperties, texture, slot )
                return

        self.state.activeTexture( GL_TEXTURE0 + slot )

        self.state.bindTexture( GL_TEXTURE_2D, textureProperties.openglTexture )

    def setTextureCube(self, texture, slot ):
        textureProperties = self.properties.get( texture )

        if texture.image.length == 6:
            if texture.version > 0 and textureProperties.version != texture.version:
                if not textureProperties.__imageopenglTextureCube:
                    texture.addEventListener( 'dispose', onTextureDispose )
                    textureProperties.__imageopenglTextureCube = glGenTextures(1)
                    self.infoMemory.textures += 1

                self.state.activeTexture( GL_TEXTURE0 + slot )
                self.state.bindTexture( GL_TEXTURE_CUBE_MAP, textureProperties.__imageopenglTextureCube )

                glPixelStorei( GL_UNPACK_FLIP_Y_WEBGL, texture.flipY )

                isCompressed = ( texture and texture.isCompressedTexture )
                isDataTexture = ( texture.image[ 0 ] and texture.image[ 0 ].isDataTexture )

                cubeImage = []

                for i in range(6):
                    if not isCompressed and not isDataTexture:
                        cubeImage[ i ] = _clampToMaxSize( texture.image[ i ], self.capabilities.maxCubemapSize )
                    else:
                        cubeImage[ i ] = texture.image[ i ].image if isDataTexture else texture.image[ i ]

                image = cubeImage[ 0 ],
                isPowerOfTwoImage = _isPowerOfTwo( image )
                glFormat = self.utils.convert( texture.format )
                glType = self.utils.convert( texture.type )

                self.setTextureParameters( GL_TEXTURE_CUBE_MAP, texture, isPowerOfTwoImage )

                for i in range(6):
                    if not isCompressed:
                        if isDataTexture:
                            self.state.texImage2D( GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, glFormat, cubeImage[ i ].width, cubeImage[ i ].height, 0, glFormat, glType, cubeImage[ i ].data )
                        else:
                            self.state.texImage2D( GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, glFormat, glFormat, glType, cubeImage[ i ] )
                    else:
                        mipmap, mipmaps = cubeImage[ i ].mipmaps

                        for j in range(len(mipmaps)):
                            mipmap = mipmaps[ j ]

                            if texture.format != RGBAFormat and texture.format != RGBFormat:
                                if self.state.getCompressedTextureFormats().indexOf( glFormat ) > - 1:
                                    self.state.compressedTexImage2D( GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, j, glFormat, mipmap.width, mipmap.height, 0, mipmap.data )
                                else:
                                    raise RuntimeWarning( 'THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()' )
                            else:
                                self.state.texImage2D( GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, j, glFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data )

                if _textureNeedsGenerateMipmaps( texture, isPowerOfTwoImage ):
                    glGenerateMipmap( GL_TEXTURE_CUBE_MAP )

                textureProperties.version = texture.version

                if texture.onUpdate:
                    texture.onUpdate( texture )

            else:
                self.state.activeTexture( GL_TEXTURE0 + slot )
                self.state.bindTexture( GL_TEXTURE_CUBE_MAP, textureProperties.__imageopenglTextureCube )

    def setTextureCubeDynamic(self, texture, slot ):
        self.state.activeTexture( GL_TEXTURE0 + slot )
        self.state.bindTexture( GL_TEXTURE_CUBE_MAP, self.properties.get( texture ).openglTexture )

    # // Set up GL resources for the render target
    def setupRenderTarget(self, renderTarget ):
        renderTargetProperties = self.properties.get( renderTarget )
        textureProperties = self.properties.get( renderTarget.texture )

        renderTarget.addEventListener( 'dispose', onRenderTargetDispose )

        textureProperties.openglTexture = glGenTextures(1)

        self.infoMemory.textures += 1

        isCube = ( renderTarget.isWebGLRenderTargetCube == True )
        isTargetPowerOfTwo = _isPowerOfTwo( renderTarget )

        # // Setup framebuffer

        if isCube:
            renderTargetProperties.__webglFramebuffer = []

            for i in range(6):
                renderTargetProperties.__webglFramebuffer[ i ] = glCreateFramebuffers(1)

        else:
            renderTargetProperties.__webglFramebuffer = glCreateFramebuffers(1)

        # // Setup color buffer

        if isCube:
            self.state.bindTexture( GL_TEXTURE_CUBE_MAP, textureProperties.openglTexture )
            self.setTextureParameters( GL_TEXTURE_CUBE_MAP, renderTarget.texture, isTargetPowerOfTwo )

            for i in range(6):
                self.setupFrameBufferTexture( renderTargetProperties.__webglFramebuffer[ i ], renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i )

            if _textureNeedsGenerateMipmaps( renderTarget.texture, isTargetPowerOfTwo ):
                glGenerateMipmap( GL_TEXTURE_CUBE_MAP )
            self.state.bindTexture( GL_TEXTURE_CUBE_MAP, None )

        else:
            self.state.bindTexture( GL_TEXTURE_2D, textureProperties.openglTexture )
            self.setTextureParameters( GL_TEXTURE_2D, renderTarget.texture, isTargetPowerOfTwo )
            self.setupFrameBufferTexture( renderTargetProperties.__webglFramebuffer, renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D )

            if _textureNeedsGenerateMipmaps( renderTarget.texture, isTargetPowerOfTwo ):
                glGenerateMipmap( GL_TEXTURE_2D )
            self.state.bindTexture( GL_TEXTURE_2D, None )

        # // Setup depth and stencil buffers

        if renderTarget.depthBuffer:
            self.setupDepthRenderbuffer( renderTarget )

    def updateRenderTargetMipmap(self, renderTarget ):
        texture = renderTarget.texture
        isTargetPowerOfTwo = _isPowerOfTwo( renderTarget )

        if _textureNeedsGenerateMipmaps( texture, isTargetPowerOfTwo ):
            target = GL_TEXTURE_CUBE_MAP if renderTarget.isWebGLRenderTargetCube else GL_TEXTURE_2D
            webglTexture = self.properties.get( texture ).openglTexture

            self.state.bindTexture( target, webglTexture )
            glGenerateMipmap( target )
            self.state.bindTexture( target, None )
