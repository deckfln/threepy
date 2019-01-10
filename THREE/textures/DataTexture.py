"""
 * @author alteredq / http://alteredqualia.com/
"""
from THREE.textures.Texture import *
from THREE.Constants import *


class _DataTextureImage:
    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height
        
        
class DataTexture(Texture):
    isDataTexture = True
    
    def __init__(self, data, width, height, format=RGBAFormat, gltype=FloatType, mapping=None,
                 wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping,
                 magFilter=NearestFilter, minFilter=NearestFilter,
                 anisotropy=1,
                 encoding=LinearEncoding):
        super().__init__(None, mapping, wrapS, wrapT, magFilter, minFilter, format, gltype, anisotropy, encoding)

        self.set_class(isDataTexture)
        self.image = _DataTextureImage(data, width, height)

        self.generateMipmaps = False
        self.flipY = False
        self.unpackAlignment = 1

