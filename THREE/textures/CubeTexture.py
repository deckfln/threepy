"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.textures.Texture import *


class CubeTexture(Texture):
    isCubeTexture = True

    def __init__(self, images=None, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, format=None,
                 type=None, anisotropy=None, encoding=None):
        if images is None:
            images = [None, None, None, None, None, None]

        if mapping is None:
            mapping = CubeReflectionMapping

        super().__init__(images, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy, encoding)
        self.set_class(isCubeTexture)

        self.flipY = False

    def getImages(self):
        return self.image

    def setImages(self, value):
        self.image = value

    images = property(getImages, setImages)
