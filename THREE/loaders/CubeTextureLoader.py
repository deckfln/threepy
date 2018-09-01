"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.loaders.ImageLoader import *
from THREE.textures.CubeTexture import *


class CubeTextureLoader:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else DefaultLoadingManager
        self.path = None
        self.target = None

    def load(self, urls, onLoad=None, onProgress=None, onError=None):
        texture = CubeTexture()

        loader = ImageLoader( self.manager )
        loader.setPath( self.path )

        loaded = 0

        for i in range(len(urls)):
            texture.images[i] = loader.load(urls[i])
            loaded += 1
            if loaded == 6:
                texture.needsUpdate = True
                if onLoad:
                    onLoad(texture)

        return texture

    def setCrossOrigin(self, value ):
        self.crossOrigin = value
        return self

    def setPath(self, value ):
        self.path = value
        return self