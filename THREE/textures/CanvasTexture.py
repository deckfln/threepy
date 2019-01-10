"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.textures.Texture import *


class CanvasTexture(Texture):
    isCanvasTexture = True

    def __init__(self, canvas, mapping=None,
                wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping,
                magFilter=LinearFilter, minFilter=LinearMipMapLinearFilter,
                format=RGBAFormat,
                gltype=UnsignedByteType,
                anisotropy=1):

        super().__init__(canvas, mapping, wrapS, wrapT, magFilter, minFilter, format, gltype, anisotropy)

        self.set_class(isCanvasTexture)

        self.needsUpdate = True
