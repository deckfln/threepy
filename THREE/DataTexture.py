"""
 * @author alteredq / http://alteredqualia.com/
"""
from THREE.Texture import *
from THREE.Constants import *


class _DataTextureImage:
    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height
        
        
class DataTexture(Texture):
    isDataTexture = True
    
    def __init__(self, data, width, height, format, type, mapping=None, wrapS=None, wrapT=None, magFilter=None, minFilter=None, anisotropy=None, encoding=None ):
        super().__init__(None, mapping, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy, encoding )

        self.set_class(isDataTexture)
        self.format = RGBA32Format
        self.image = _DataTextureImage(data, width, height)

        self.magFilter = magFilter if magFilter is not None else NearestFilter
        self.minFilter = minFilter if minFilter is not None else NearestFilter

        self.generateMipmaps = False
        self.flipY = False
        self.unpackAlignment = 1

