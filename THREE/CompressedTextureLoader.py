"""
 * @author mrdoob / http:#mrdoob.com/
 *
 * Abstract Base class to block based textures loader (dds, pvr, ...)
"""
from THREE.Constants import *
from THREE.CompressedTexture import *
from THREE.FileLoader import *


class CompressedTextureLoader:
    def __init__(self, manager=None ):
        self.manager = manager if ( manager is not None ) else DefaultLoadingManager

        # override in sub classes
        self._parser = None
        self.path = ''

    def load(self, url, onLoad=None, onProgress=None, onError=None ):
        scope = self

        texture = CompressedTexture()

        loader = FileLoader( self.manager )
        loader.setPath( self.path )
        loader.setResponseType( 'arraybuffer' )

        loaded = 0

        def loadTexture( i ):
            def _onLoad ( buffer ):
                nonlocal loaded
                texDatas = self._parser( buffer, True )

                image = CompressedImage(texDatas['width'], texDatas['height'], texDatas['format'], texDatas['mipmaps'])
                self.image.append(image)

                loaded += 1

                if loaded == 6:
                    if texDatas['mipmapCount'] == 1:
                        texture.minFilter = LinearFilter

                    texture.format = texDatas['format']
                    texture.needsUpdate = True

                    if onLoad:
                        onLoad( texture )

            self.image = []

            loader.load( url[ i ], _onLoad, onProgress, onError )

        if isinstance(url, list):
            for i in range(len(url)):
                loadTexture( i )

        else:
            # compressed cubemap texture stored in a single DDS file

            def _onLoad( buffer ):
                texDatas = self._parser( buffer, True )

                if texDatas['isCubemap']:
                    faces = len(texDatas['mipmaps']) / texDatas.mipmapCount

                    self.image = []

                    for f in range(faces):
                        image = CompressedImage(texDatas['width'], texDatas['height'])

                        for i in range(texDatas.mipmapCount):
                            image.mipmaps.append( texDatas['mipmaps'][ f * texDatas['mipmapCount'] + i ] )

                        self.image.append(image)
                else:
                    texture.image.width = texDatas['width']
                    texture.image.height = texDatas['height']
                    texture.mipmaps = texDatas['mipmaps']

                if texDatas['mipmapCount'] == 1:
                    texture.minFilter = LinearFilter

                texture.format = texDatas['format']
                texture.needsUpdate = True

                if onLoad:
                    onLoad( texture )

            loader.load( url, _onLoad, onProgress, onError )

        return texture

    def setPath(self, value ):
        self.path = value
        return self

