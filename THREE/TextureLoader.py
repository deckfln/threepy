"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
import re
import numpy

from THREE.ImageLoader import *
from THREE.Texture import *
from THREE.Constants import *
from THREE.LoadingManager import *


def _onLoad(url, texture):
    # // JPEGs can't have an alpha channel, so memory can be saved by storing them as RGB.
    isJPEG = re.search('\.(jpg|jpeg)$', url) is not None
    texture.format = RGBFormat if isJPEG else RGBAFormat
    texture.needsUpdate = True


class TextureLoader:
    def __init__(self, manager=None ):
        global DefaultLoadingManager
        self.manager = manager if manager else DefaultLoadingManager
        self.path = None

    def load(self, url, onLoad=None, onProgress=None, onError=None ):
        loader = ImageLoader( self.manager )
        loader.setPath( self.path )

        texture = Texture()
        texture.unpackAlignment = 1
        loader.setTarget(texture)
        texture.image = loader.load( url, _onLoad, onProgress, onError )
        texture.format = RGBFormat if texture.image.mode == 'RGB' else RGBAFormat
        texture.img_data = numpy.fromstring(texture.image.tobytes(), numpy.uint8)
        texture.name = url

        return texture

    def setPath(self, value ):
        self.path = value
        return self

    def setCrossOrigin(self, value):
        return True
