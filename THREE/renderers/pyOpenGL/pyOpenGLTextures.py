"""
    /**
     * @author mrdoob / http:# //mrdoob.com/
     */
"""
# from OpenGL_accelerate import *
from OpenGL.GL import *
from OpenGL.GL.EXT.texture_filter_anisotropic import *
import OpenGL.raw.GL.VERSION.GL_1_0
from ctypes import c_void_p

import THREE._Math as _Math
from THREE.textures.TextureArray import *
import PIL
from PIL import Image
import numpy


def _clampToMaxSize(image, maxSize):
    if image.width > maxSize or image.height > maxSize:
        if 'data' in image:
            raise RuntimeWarning( 'THREE.WebGLRenderer: image in DataTexture is too big (' + image.width + 'x' + image.height + ').' );

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
    w = int(_Math.floorPowerOfTwo(image.width))
    h = int(_Math.floorPowerOfTwo(image.height))

    im = image.resize((w, h), PIL.Image.BICUBIC)

    print('THREE.WebGLRenderer: image is not power of 2 (%d, %d). Resized to (%d,%d)' % (image.width, image.height, w, h))

    return im


def _textureNeedsPowerOfTwo(texture):
    # TODO ?
    # if ( ! capabilities.isWebGL2 ) return False;

    return (texture.wrapS != ClampToEdgeWrapping or texture.wrapT != ClampToEdgeWrapping) or \
           (texture.minFilter != NearestFilter and texture.minFilter != LinearFilter)


def _textureNeedsGenerateMipmaps(texture, isPowerOfTwo):
    return texture.generateMipmaps and isPowerOfTwo and \
           texture.minFilter != NearestFilter and texture.minFilter != LinearFilter


def generateMipmap(properties, target, texture, width, height ):
    glGenerateMipmap( target )

    textureProperties = properties.get( texture )

    # Note: Math.log( x ) * Math.LOG2E used instead of Math.log2( x ) which is not supported by IE11
    textureProperties._maxMipLevel = math.log( max( width, height ) ) * _Math.LOG2E


def getInternalFormat( glFormat, glType ):
    # TODO ?
    # if ( ! capabilities.isWebGL2 ) return glFormat;

    if glFormat == GL_RGB:
        if glType == GL_FLOAT:
            return GL_RGB32F
        if glType == GL_HALF_FLOAT:
            return GL_RGB16F
        if glType == GL_UNSIGNED_BYTE:
            return GL_RGB8

    if glFormat == GL_RGBA:
        if glType == GL_FLOAT:
            return GL_RGBA32F
        if glType == GL_HALF_FLOAT:
            return GL_RGBA16F
        if glType == GL_UNSIGNED_BYTE:
            return GL_RGBA8

    return glFormat


# // Fallback filters for non-power-of-2 textures

def _filterFallback(f):
    if f == NearestFilter or f == NearestMipMapNearestFilter or f == NearestMipMapLinearFilter:
        return GL_NEAREST
    return GL_LINEAR


class pyOpenGLTextures:
    _videoTextures = {}

    def __init__(self, extensions, state, properties, capabilities, utils, info):
        self.extensions = extensions
        self.state = state
        self.properties = properties
        self.capabilities = capabilities
        self.utils = utils
        self.info = info

        # //

    def dispose(self, texture=None):
        if texture is None:
            for property in self.properties.properties:
                obj = property.object
                if obj.my_class(isTexture):
                    self.deallocateTexture(obj)
                elif obj.my_class(isWebGLRenderTarget):
                    self.deallocateRenderTarget(obj)
        else:
            if texture.my_class(isTexture):
                self.deallocateTexture(texture)
            elif texture.my_class(isWebGLRenderTarget):
                self.deallocateRenderTarget(texture)

        self.info.memory.textures -= 1

    def deallocateTexture(self, texture):
        textureProperties = self.properties.get(texture)

        if texture.image and textureProperties.imageopenglTextureCube:
            # // cube texture
            glDeleteTextures(1, textureProperties.imageopenglTextureCube)
        else:
            # // 2D texture
            if not textureProperties.openglInit:
                return

            glDeleteTextures(1, [textureProperties.openglTexture])

        # // remove all webgl properties
        self.properties.remove(texture)

    def deallocateRenderTarget(self, renderTarget):
        renderTargetProperties = self.properties.get(renderTarget)
        textureProperties = self.properties.get(renderTarget.texture)

        if not renderTarget:
            return

        if textureProperties.openglTexture is not None:
            glDeleteTextures(1, textureProperties.openglTexture)

        if renderTarget.depthTexture:
            renderTarget.depthTexture.dispose()

        if renderTarget.my_class(isWebGLRenderTargetCube):
            for i in range(6):
                glDeleteFramebuffers(1, renderTargetProperties.openglFrameBuffer[i])
                if renderTargetProperties.depthBuffer:
                    glDeleteRenderbuffers(1, renderTargetProperties.openglDepthBuffer[i])
        else:
            glDeleteFramebuffers(1, renderTargetProperties.openglFrameBuffer)
            if renderTargetProperties.depthBuffer:
                glDeleteRenderbuffers(1, renderTargetProperties.openglDepthBuffer)

        self.properties.remove(renderTarget.texture)
        self.properties.remove(renderTarget)

    def setTextureParameters(self, textureType, texture, isPowerOfTwoImage):
        if isPowerOfTwoImage:
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_WRAP_S, self.utils.convert(texture.wrapS))
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_WRAP_T, self.utils.convert(texture.wrapT))
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_WRAP_R, self.utils.convert(texture.wrapT))

            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_MAG_FILTER, self.utils.convert(texture.magFilter))
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_MIN_FILTER, self.utils.convert(texture.minFilter))

        else:
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            if texture.wrapS != ClampToEdgeWrapping or texture.wrapT != ClampToEdgeWrapping:
                raise RuntimeWarning('THREE.WebGLRenderer: Texture is not power of two. Texture.wrapS and Texture.wrapT should be set to THREE.ClampToEdgeWrapping.', texture)

            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_MAG_FILTER, _filterFallback(texture.magFilter))
            OpenGL.raw.GL.VERSION.GL_1_0.glTexParameteri(textureType, GL_TEXTURE_MIN_FILTER, _filterFallback(texture.minFilter))

            if texture.minFilter != NearestFilter and texture.minFilter != LinearFilter:
                raise RuntimeWarning('THREE.WebGLRenderer: Texture is not power of two. Texture.minFilter should be set to THREE.NearestFilter or THREE.LinearFilter.', texture)

        extension = self.extensions.get('EXT_texture_filter_anisotropic')

        if extension:
            if texture.type == FloatType and self.extensions.get('OES_texture_float_linear') is None:
                return
            if texture.type == HalfFloatType and self.extensions.get('OES_texture_half_float_linear') is None:
                return

            if texture.anisotropy > 1 or self.properties.get(texture).currentAnisotropy:
                glTexParameterf(textureType, GL_TEXTURE_MAX_ANISOTROPY_EXT, min(texture.anisotropy, self.capabilities.getMaxAnisotropy()))
                self.properties.get(texture).currentAnisotropy = texture.anisotropy

    def uploadTexture(self, textureProperties, texture, slot):
        if isinstance(texture, TextureArray):
            return self._uploadTextureArray(textureProperties, texture, slot)

        return self._uploadTexture(textureProperties, texture, slot)

    def _uploadTexture(self, textureProperties, texture, slot):
        """
        Original member from THREE.js
        """
        if not textureProperties.openglInit:
            textureProperties.openglInit = True

            textureProperties.openglTexture = glGenTextures(1)

            self.info.memory.textures += 1
            new_texture = True
        else:
            new_texture = False

        self.state.activeTexture(GL_TEXTURE0 + slot)
        self.state.bindTexture(GL_TEXTURE_2D, textureProperties.openglTexture)

        # glPixelStorei(GL_UNPACK_FLIP_Y_WEBGL, texture.flipY)
        # glPixelStorei(GL_UNPACK_PREMULTIPLY_ALPHA_WEBGL, texture.premultiplyAlpha)
        glPixelStorei(GL_UNPACK_ALIGNMENT, texture.unpackAlignment)

        image = _clampToMaxSize(texture.image, self.capabilities.maxTextureSize)

        if _textureNeedsPowerOfTwo(texture) and not _isPowerOfTwo(image):
            image = _makePowerOfTwo(image)

        isPowerOfTwoImage = _isPowerOfTwo(image)
        glFormat = self.utils.convert(texture.format)
        glType = self.utils.convert(texture.type)
        glInternalFormat = getInternalFormat(glFormat, glType)

        if new_texture:
            self.setTextureParameters(GL_TEXTURE_2D, texture, isPowerOfTwoImage)

        mipmaps = texture.mipmaps

        if texture.my_class(isDepthTexture):
            # // populate depth texture with dummy data

            glInternalFormat = GL_DEPTH_COMPONENT

            if texture.type == FloatType:
                glInternalFormat = GL_DEPTH_COMPONENT32F
            else:
                # // WebGL 2.0 requires signed internalformat for glTexImage2D
                glInternalFormat = GL_DEPTH_COMPONENT16

            if texture.format == DepthFormat and glInternalFormat == GL_DEPTH_COMPONENT:
                # // The error INVALID_OPERATION is generated by texImage2D if format and internalformat are
                # // DEPTH_COMPONENT and type is not UNSIGNED_SHORT or UNSIGNED_INT
                # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

                if texture.type != UnsignedShortType and texture.type != UnsignedIntType:
                    print('THREE.WebGLRenderer: Use UnsignedShortType or UnsignedIntType for DepthFormat DepthTexture.')

                    texture.type = UnsignedShortType
                    glType = self.utils.convert(texture.type)

            # // Depth stencil textures need the DEPTH_STENCIL internal format
            # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

            if texture.format == DepthStencilFormat:
                glInternalFormat = GL_DEPTH_STENCIL

                # // The error INVALID_OPERATION is generated by texImage2D if format and internalformat are
                # // DEPTH_STENCIL and type is not UNSIGNED_INT_24_8_WEBGL.
                # // (https:# //www.khronos.org/registry/webgl/extensions/WEBGL_depth_texture/)

                if texture.type != UnsignedInt248Type:
                    print('THREE.WebGLRenderer: Use UnsignedInt248Type for DepthStencilFormat DepthTexture.')

                    texture.type = UnsignedInt248Type
                    glType = self.utils.convert(texture.type)

            self.state.texImage2D(GL_TEXTURE_2D, 0, glInternalFormat, image.width, image.height, 0, glFormat, glType, None)

        elif texture.my_class(isDataTexture):
            # // use manually created mipmaps if available
            # // if there are no manual mipmaps
            # // set 0 level mipmap and then use GL to generate other mipmap levels

            if mipmaps and isPowerOfTwoImage:
                for i in range(len(mipmaps)):
                    mipmap = mipmaps[i]
                    self.state.texImage2D(GL_TEXTURE_2D, i, glInternalFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data)

                texture.generateMipmaps = False
                textureProperties._maxMipLevel = len(mipmaps) - 1
            else:
                # self.state.texImage2D(GL_TEXTURE_2D, 0, glFormat, image.width, image.height, 0, GL_RGBA, glType, image.data)
                OpenGL.raw.GL.VERSION.GL_1_0.glTexImage2D(GL_TEXTURE_2D, 0, glInternalFormat, image.width, image.height, 0, glFormat, glType, image.data)
                textureProperties._maxMipLevel = 0

        elif texture.my_class(isCompressedTexture):
            for i in range(len(mipmaps)):
                mipmap = mipmaps[i]

                if texture.format != RGBAFormat and texture.format != RGBFormat:
                    if self.state.getCompressedTextureFormats().index(glFormat) > - 1:
                        self.state.compressedTexImage2D(GL_TEXTURE_2D, i, glInternalFormat, mipmap.width, mipmap.height, 0, mipmap.data)
                    else:
                        raise RuntimeWarning('THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()')

                else:
                    self.state.texImage2D(GL_TEXTURE_2D, i, glInternalFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data)

            textureProperties._maxMipLevel = len(mipmaps) - 1

        else:
            # // regular Texture (image, video, canvas)

            # // use manually created mipmaps if available
            # // if there are no manual mipmaps
            # // set 0 level mipmap and then use GL to generate other mipmap levels

            if mipmaps and isPowerOfTwoImage:
                i = 0
                for mipmap in mipmaps:
                    self.state.texImage2D(GL_TEXTURE_2D, i, glInternalFormat, image.width, image.height, 0, glFormat, glType, mipmap)
                    i += 1

                texture.generateMipmaps = False
                textureProperties._maxMipLevel = len(mipmaps) - 1
            else:
                if texture.img_data is None:
                    texture.get_data()
                width, height = image.size
                # self.state.texImage2D(GL_TEXTURE_2D, 0, glFormat,  width, height, 0, glFormat, glType, texture.img_data)
                OpenGL.raw.GL.VERSION.GL_1_0.glTexImage2D(GL_TEXTURE_2D, 0, glInternalFormat,  width, height, 0, glFormat, glType, texture.img_data)
                textureProperties._maxMipLevel = 0

        if _textureNeedsGenerateMipmaps(texture, isPowerOfTwoImage):
            generateMipmap(self.properties, GL_TEXTURE_2D, texture, image.width, image.height)
            #OpenGL.raw.GL.VERSION.GL_3_0.glGenerateMipmap(GL_TEXTURE_2D)

        textureProperties.version = texture.version

        if texture.onUpdate:
            texture.onUpdate(texture)

    # // Render targets

    # // Setup storage for target texture and bind it to correct framebuffer

    def setupFrameBufferTexture(self, framebuffer, renderTarget, attachment, textureTarget):
        glFormat = self.utils.convert(renderTarget.texture.format)
        glType = self.utils.convert(renderTarget.texture.type)
        glInternalFormat = getInternalFormat(glFormat, glType)
        self.state.texImage2D(textureTarget, 0, glInternalFormat, renderTarget.width, renderTarget.height, 0, glFormat, glType, None)
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, textureTarget, self.properties.get(renderTarget.texture).openglTexture, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # // Setup storage for internal depth/stencil buffers and bind to correct framebuffer
    def setupRenderBufferStorage(self, renderbuffer, renderTarget):
        glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)

        if renderTarget.depthBuffer and not renderTarget.stencilBuffer:
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, renderTarget.width, renderTarget.height)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, renderbuffer)

        elif renderTarget.depthBuffer and renderTarget.stencilBuffer:
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_STENCIL, renderTarget.width, renderTarget.height)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, renderbuffer)

        else:
            # // FIXME: We don't support !depth !stencil
            glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA4, renderTarget.width, renderTarget.height)

        glBindRenderbuffer(GL_RENDERBUFFER, 0)

    # // Setup resources for a Depth Texture for a FBO (needs an extension)
    def setupDepthTexture(self, framebuffer, renderTarget):
        isCube = (renderTarget and renderTarget.my_class(isWebGLRenderTargetCube))
        if isCube:
            raise RuntimeError('Depth Texture with cube render targets is not supported')

        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

        if not(renderTarget.depthTexture and renderTarget.depthTexture.is_a('DepthTexture')):
            raise RuntimeError('renderTarget.depthTexture must be an instance of THREE.DepthTexture')

        # // upload an empty depth texture with framebuffer size
        if not self.properties.get(renderTarget.depthTexture).openglTexture or \
                renderTarget.depthTexture.image.width != renderTarget.width or \
                renderTarget.depthTexture.image.height != renderTarget.height:
            renderTarget.depthTexture.image.width = renderTarget.width
            renderTarget.depthTexture.image.height = renderTarget.height
            renderTarget.depthTexture.needsUpdate = True

        self.setTexture2D(renderTarget.depthTexture, 0)

        webglDepthTexture = self.properties.get(renderTarget.depthTexture).openglTexture

        if renderTarget.depthTexture.format == DepthFormat:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, webglDepthTexture, 0)

        elif renderTarget.depthTexture.format == DepthStencilFormat:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, webglDepthTexture, 0)

        else:
            raise RuntimeError('Unknown depthTexture format')

    # // Setup GL resources for a non-texture depth buffer
    def setupDepthRenderbuffer(self, renderTarget):
        renderTargetProperties = self.properties.get(renderTarget)

        isCube = renderTarget.my_class(isWebGLRenderTargetCube)

        if renderTarget.depthTexture:

            if isCube:
                raise RuntimeError('target.depthTexture not supported in Cube render targets')

            self.setupDepthTexture(renderTargetProperties.openglFrameBuffer, renderTarget)

        else:
            if isCube:
                renderTargetProperties.openglDepthBuffer = []

                for i in range(6):
                    glBindFramebuffer(GL_FRAMEBUFFER, renderTargetProperties.openglFrameBuffer[i])
                    renderTargetProperties.openglDepthBuffer[i] = glGenRenderbuffers(1)
                    self.setupRenderBufferStorage(renderTargetProperties.openglDepthBuffer[i], renderTarget)

            else:
                glBindFramebuffer(GL_FRAMEBUFFER, renderTargetProperties.openglFrameBuffer)
                renderTargetProperties.openglDepthBuffer = glGenRenderbuffers(1)
                self.setupRenderBufferStorage(renderTargetProperties.openglDepthBuffer, renderTarget)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # //

    def setTexture2D(self, texture, slot):
        textureProperties = self.properties.get(texture)

        if texture.my_class(isVideoTexture):
            self.updateVideoTexture( texture )

        if texture.version > 0 and textureProperties.version != texture.version:
            image = texture.image

            if image is None:
                raise RuntimeWarning('THREE.WebGLRenderer: Texture marked for update but image is undefined', texture)

            self.uploadTexture(textureProperties, texture, slot)
        else:
            if texture.my_class(isTextureArray):
                self.state.activeTexture(GL_TEXTURE0 + slot)
                self.state.bindTexture(GL_TEXTURE_2D_ARRAY, textureProperties.openglTexture)
            else:
                self.state.activeTexture(GL_TEXTURE0 + slot)
                self.state.bindTexture(GL_TEXTURE_2D, textureProperties.openglTexture)

    def setTextureCube(self, texture, slot):
        textureProperties = self.properties.get(texture)

        if len(texture.image) == 6:
            if 0 < texture.version and textureProperties.version != texture.version:
                if not textureProperties.imageopenglTextureCube:
                    textureProperties.imageopenglTextureCube = glGenTextures(1)
                    self.info.memory.textures += 1

                self.state.activeTexture(GL_TEXTURE0 + slot)
                self.state.bindTexture(GL_TEXTURE_CUBE_MAP, textureProperties.imageopenglTextureCube)

                # TODO FDE:is this needed with openGL ?
                # glPixelStorei(GL_UNPACK_FLIP_Y_WEBGL, texture.flipY)

                isCompressed = (texture and texture.is_a('CompressedTexture'))
                isDataTexture = (texture.image[0] and hasattr(texture.image[0], 'isDataTexture'))

                cubeImage = [None, None, None, None, None, None]

                for i in range(6):
                    if not isCompressed and not isDataTexture:
                        cubeImage[i] = _clampToMaxSize(texture.image[i], self.capabilities.maxCubemapSize)
                    else:
                        cubeImage[i] = texture.image[i].image if isDataTexture else texture.image[i]

                image = cubeImage[0]
                isPowerOfTwoImage = _isPowerOfTwo(image)
                glFormat = self.utils.convert(texture.format)
                glType = self.utils.convert(texture.type)
                glInternalFormat = getInternalFormat(glFormat, glType)

                self.setTextureParameters(GL_TEXTURE_CUBE_MAP, texture, isPowerOfTwoImage)

                for i in range(6):
                    if not isCompressed:
                        if isDataTexture:
                            self.state.texImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, glInternalFormat, cubeImage[i].width, cubeImage[i].height, 0, glFormat, glType, cubeImage[i].data)
                        else:
                            #TODO FDE: optimize data cache ?

                            # glTexImage2D expects the first element of the image data to be the bottom-left corner of the image.
                            # Subsequent elements go left to right, with subsequent lines going from bottom to top.
                            #
                            # However, the image data was created with PIL Image tostring and numpy's fromstring, which means we
                            # have to do a bit of reorganization. The first element in the data output by tostring() will be the
                            # top-left corner of the image, with following values going left-to-right and lines going top-to-bottom.
                            # So, we need to flip the vertical coordinate (y).

                            im = cubeImage[i].transpose(Image.FLIP_TOP_BOTTOM)

                            img_data = numpy.fromstring(im.tobytes(), numpy.uint8)
                            ix, iy = cubeImage[i].size
                            self.state.texImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, glInternalFormat, ix, iy, 0, glFormat, glType, img_data)
                    else:
                        mipmap, mipmaps = cubeImage[i].mipmaps

                        for j in range(len(mipmaps)):
                            mipmap = mipmaps[j]

                            if texture.format != RGBAFormat and texture.format != RGBFormat:
                                if self.state.getCompressedTextureFormats().indexOf(glFormat) > - 1:
                                    self.state.compressedTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, j, glInternalFormat, mipmap.width, mipmap.height, 0, mipmap.data)
                                else:
                                    raise RuntimeWarning('THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()')
                            else:
                                self.state.texImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, j, glInternalFormat, mipmap.width, mipmap.height, 0, glFormat, glType, mipmap.data)

                if not isCompressed:
                    textureProperties._maxMipLevel = 0
                else:
                    textureProperties._maxMipLevel = len(mipmaps) - 1

                if _textureNeedsGenerateMipmaps(texture, isPowerOfTwoImage):
                    # We assume images for cube map have the same size.
                    generateMipmap(self.properties, GL_TEXTURE_CUBE_MAP, texture, image.width, image.height)
                    # glGenerateMipmap(GL_TEXTURE_CUBE_MAP)

                textureProperties.version = texture.version

                if texture.onUpdate:
                    texture.onUpdate(texture)

            else:
                self.state.activeTexture(GL_TEXTURE0 + slot)
                self.state.bindTexture(GL_TEXTURE_CUBE_MAP, textureProperties.imageopenglTextureCube)

    def setTextureCubeDynamic(self, texture, slot):
        self.state.activeTexture(GL_TEXTURE0 + slot)
        self.state.bindTexture(GL_TEXTURE_CUBE_MAP, self.properties.get(texture).openglTexture)

    # // Set up GL resources for the render target
    def setupRenderTarget(self, renderTarget):
        renderTargetProperties = self.properties.get(renderTarget)
        textureProperties = self.properties.get(renderTarget.texture)

        textureProperties.openglTexture = glGenTextures(1)

        self.info.memory.textures += 1

        isCube = (renderTarget.my_class(isWebGLRenderTargetCube) == True)
        isTargetPowerOfTwo = _isPowerOfTwo(renderTarget)

        # // Setup framebuffer

        if isCube:
            renderTargetProperties.openglFrameBuffer = []

            for i in range(6):
                renderTargetProperties.openglFrameBuffer[i] = glGenFramebuffers(1)

        else:
            renderTargetProperties.openglFrameBuffer = glGenFramebuffers(1)

        # // Setup color buffer

        if isCube:
            self.state.bindTexture(GL_TEXTURE_CUBE_MAP, textureProperties.openglTexture)
            self.setTextureParameters(GL_TEXTURE_CUBE_MAP, renderTarget.texture, isTargetPowerOfTwo)

            for i in range(6):
                self.setupFrameBufferTexture(renderTargetProperties.openglFrameBuffer[i], renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i)

            if _textureNeedsGenerateMipmaps(renderTarget.texture, isTargetPowerOfTwo):
                generateMipmap(self.properties, GL_TEXTURE_CUBE_MAP, renderTarget.texture, renderTarget.width, renderTarget.height);

            self.state.bindTexture(GL_TEXTURE_CUBE_MAP, None)

        else:
            self.state.bindTexture(GL_TEXTURE_2D, textureProperties.openglTexture)
            self.setTextureParameters(GL_TEXTURE_2D, renderTarget.texture, isTargetPowerOfTwo)
            self.setupFrameBufferTexture(renderTargetProperties.openglFrameBuffer, renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D)

            if _textureNeedsGenerateMipmaps(renderTarget.texture, isTargetPowerOfTwo):
                generateMipmap(self.properties, GL_TEXTURE_2D, renderTarget.texture, renderTarget.width, renderTarget.height)

            self.state.bindTexture(GL_TEXTURE_2D, None)

        # // Setup depth and stencil buffers

        if renderTarget.depthBuffer:
            self.setupDepthRenderbuffer(renderTarget)

    def updateRenderTargetMipmap(self, renderTarget):
        texture = renderTarget.texture
        isTargetPowerOfTwo = _isPowerOfTwo(renderTarget)

        if _textureNeedsGenerateMipmaps(texture, isTargetPowerOfTwo):
            target = GL_TEXTURE_CUBE_MAP if renderTarget.my_class(isWebGLRenderTargetCube) else GL_TEXTURE_2D
            webglTexture = self.properties.get(texture).openglTexture

            self.state.bindTexture(target, webglTexture)
            generateMipmap(self.properties, target, texture, renderTarget.width, renderTarget.height)
            self.state.bindTexture(target, None)

    def updateVideoTexture(self, texture):
        id = texture.id
        frame = self.info.render.frame

        # Check the last frame we updated the VideoTexture

        if self._videoTextures[ id ] != frame:
            self._videoTextures[ id ] = frame
            texture.update()

    #
    #   Extension for TextureArray
    #

    def _uploadTextureArray(self, textureProperties, texture: TextureArray, slot):
        if not textureProperties.openglInit:
            textureProperties.openglInit = True

            textureProperties.openglTexture = glGenTextures(1)

            self.info.memory.textures += 1
            new_texture = True
        else:
            new_texture = False

        isPowerOfTwoImage = _Math.isPowerOfTwo(texture.width) and _Math.isPowerOfTwo(texture.height)

        if not isinstance(texture.image, list):
            image = _clampToMaxSize(texture.image, self.capabilities.maxTextureSize)

            if _textureNeedsPowerOfTwo(texture) and not isPowerOfTwoImage:
                image = _makePowerOfTwo(image)

        glFormat = self.utils.convert(texture.format)
        glType = self.utils.convert(texture.type)
        glInternalFormat = getInternalFormat(glFormat, glType)

        self.state.activeTexture(GL_TEXTURE0 + slot)
        self.state.bindTexture(GL_TEXTURE_2D_ARRAY, textureProperties.openglTexture)
        ### glPixelStorei(GL_UNPACK_ALIGNMENT, texture.unpackAlignment)

        if new_texture:
            #glTexStorage3D(GL_TEXTURE_2D_ARRAY, texture.mipmaps, glInternalFormat, texture.width, texture.height,
            #               texture.layerCount)

            glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, glInternalFormat, texture.width, texture.height,
                           texture.layerCount, 0, glFormat, glType, None)
            self.setTextureParameters(GL_TEXTURE_2D_ARRAY, texture, isPowerOfTwoImage)
            """
            if isinstance(texture.image, list):
                d = glGetIntegerv(GL_MAX_ARRAY_TEXTURE_LAYERS)
                images = len(texture.image)
                glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA32F, 9, 9, 1024, 0, GL_RGBA, GL_FLOAT, None)
            """

        mipmaps = texture.mipmaps

        if texture.my_class(isDepthTexture):
            raise RuntimeError('pyOpenGLTextures: DepthTexture not supported for TextureArray.')

        elif texture.my_class(isCompressedTexture):
            raise RuntimeError('pyOpenGLTextures: CompressedTexturenot supported for TextureArray.')

        else:
            # // regular Texture and DataTexture (image, video, canvas)
            images = texture.image
            if isinstance(images, list):
                # load each picture

                # build the private versions list
                if textureProperties._versions is None:
                    textureProperties._versions = [-1 for i in range(len(images))]

                # for each layer, upload only if newer
                for i in range(len(images)):
                    if textureProperties._versions[i] < texture._versions[i]:
                        img_data = texture.img_data[i]
                        glTexSubImage3D(
                            GL_TEXTURE_2D_ARRAY,
                            0,
                            0, 0, i,
                            texture.width, texture.height, 1,
                            glFormat,
                            glType,
                            img_data
                        )
                        textureProperties._versions[i] = texture._versions[i]
            else:
                # load the whole picture at once
                if texture.img_data is None:
                    texture.get_data()

                glTexSubImage3D(
                    GL_TEXTURE_2D_ARRAY,
                    0,            # mipmap level
                    0, 0, 0,
                    texture.width,      # width
                    texture.height,     # height
                    texture.layerCount, # depth
                    glFormat,           # cpu pixelformat
                    glType,             # cpu pixel coord type
                    texture.img_data    # pixel data
                )


            textureProperties._maxMipLevel = 0

        if _textureNeedsGenerateMipmaps(texture, isPowerOfTwoImage):
            glGenerateMipmap(GL_TEXTURE_2D_ARRAY)

        textureProperties.version = texture.version

        if texture.onUpdate:
            texture.onUpdate(texture)

    def _setupRenderTargetArray(self, renderTarget):
        """
        Set up GL resources for the render target
        :param renderTarget:
        :return:
        """
        renderTargetProperties = self.properties.get(renderTarget)
        textureProperties = self.properties.get(renderTarget.texture)

        textureProperties.openglTexture = glGenTextures(1)

        self.info.memory.textures += 1

        isCube = (renderTarget.my_class(isWebGLRenderTargetCube) == True)
        isTargetPowerOfTwo = oglTextures._isPowerOfTwo(renderTarget)

        # // Setup framebuffer

        if isCube:
            renderTargetProperties.openglFrameBuffer = []

            for i in range(6):
                renderTargetProperties.openglFrameBuffer[i] = glGenFramebuffers(1)

        else:
            renderTargetProperties.openglFrameBuffer = glGenFramebuffers(1)

        # // Setup color buffer

        if isCube:
            self.state.bindTexture(GL_TEXTURE_CUBE_MAP, textureProperties.openglTexture)
            self.setTextureParameters(GL_TEXTURE_CUBE_MAP, renderTarget.texture, isTargetPowerOfTwo)

            for i in range(6):
                self.setupFrameBufferTexture(renderTargetProperties.openglFrameBuffer[i], renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + i)

            if oglTextures._textureNeedsGenerateMipmaps(renderTarget.texture, isTargetPowerOfTwo):
                oglTextures.generateMipmap(self.properties, GL_TEXTURE_CUBE_MAP, renderTarget.texture, renderTarget.width, renderTarget.height);

            self.state.bindTexture(GL_TEXTURE_CUBE_MAP, None)

        else:
            self.state.bindTexture(GL_TEXTURE_2D_ARRAY, textureProperties.openglTexture)
            self.setTextureParameters(GL_TEXTURE_2D_ARRAY, renderTarget.texture, isTargetPowerOfTwo)
            self.setupFrameBufferTexture(renderTargetProperties.openglFrameBuffer, renderTarget, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D)

            if oglTextures._textureNeedsGenerateMipmaps(renderTarget.texture, isTargetPowerOfTwo):
                oglTextures.generateMipmap(self.properties, GL_TEXTURE_2D, renderTarget.texture, renderTarget.width, renderTarget.height)

            self.state.bindTexture(GL_TEXTURE_2D_ARRAY, None)

        # // Setup depth and stencil buffers

        if renderTarget.depthBuffer:
            self.setupDepthRenderbuffer(renderTarget)
