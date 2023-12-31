"""
 * @author alteredq / http://alteredqualia.com/
"""
from THREE.textures.Texture import *


class MipMap:
    def __init__(self, width, height, data):
        self.width = width
        self.height = height
        self.data = data


class CompressedImage:
    def __init__(self, width=0, height=0, format=0, mipmaps=None):
        self.width = width
        self.height = height
        self.format = format
        self.mipmaps = mipmaps if mipmaps is not None else []


class CompressedTexture(Texture):
    isCompressedTexture = True
    
    def __init__(self, mipmaps=None, width=None, height=None,
                format=RGBAFormat,
                gltype=UnsignedByteType,
                mapping=None,
                wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping,
                magFilter=LinearFilter, minFilter=LinearMipMapLinearFilter,
                anisotropy=1,
                encoding=LinearEncoding):

        super().__init__(None, mapping, wrapS, wrapT, magFilter, minFilter, format, gltype, anisotropy, encoding)

        self.set_class(isCompressedTexture)
        self.image = CompressedImage(width, height)
        self.mipmaps = mipmaps

        # no flipping for cube textures
        # (also flipping doesn't work for compressed textures )

        self.flipY = False

        # can't generate mipmaps for compressed textures
        # mips must be embedded in DDS files

        self.generateMipmaps = False
