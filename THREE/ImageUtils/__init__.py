"""

"""
from THREE.TextureLoader import *
from THREE.CubeTextureLoader import *


def loadTexture( url, mapping, onLoad, onError ):
    print( 'THREE.ImageUtils.loadTexture has been deprecated. Use THREE.TextureLoader() instead.' )

    loader = TextureLoader()

    texture = loader.load( url, onLoad, None, onError )

    if mapping:
        texture.mapping = mapping

    return texture


def loadTextureCube( urls, mapping, onLoad, onError ):
    print( 'THREE.ImageUtils.loadTextureCube has been deprecated. Use THREE.CubeTextureLoader() instead.' )

    loader = CubeTextureLoader()

    texture = loader.load( urls, onLoad, None, onError )

    if mapping:
        texture.mapping = mapping

    return texture


def loadCompressedTexture():
    raise RuntimeError( 'THREE.ImageUtils.loadCompressedTexture has been removed. Use THREE.DDSLoader instead.' )


def loadCompressedTextureCube():
    raise RuntimeError( 'THREE.ImageUtils.loadCompressedTextureCube has been removed. Use THREE.DDSLoader instead.' )
