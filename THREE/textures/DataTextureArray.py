"""
 * @author alteredq / http://alteredqualia.com/
"""
from THREE.textures.TextureArray import *
from THREE.Constants import *


class DataTextureArray(TextureArray):
    isDataTextureArray = True
    
    def __init__(self, data, width: int, height: int, layerCount: int,
                 format=RGBAFormat,
                 gltype=FloatType,
                 mapping=None,
                 wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping,
                 magFilter=NearestFilter, minFilter=NearestFilter,
                 anisotropy=1,
                 encoding=LinearEncoding):
        super().__init__(data, width, height, layerCount, 1, format, gltype, mapping, wrapS, wrapT, magFilter, minFilter, anisotropy, encoding)

        self.set_class(isDataTextureArray)
        self.format = format

        self.generateMipmaps = False
        self.flipY = False
        self.unpackAlignment = 1
