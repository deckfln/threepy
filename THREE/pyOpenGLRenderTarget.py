"""
/**
 * @author szimek / https://github.com/szimek/
 * @author alteredq / http://alteredqualia.com/
 * @author Marius Kintel / https://github.com/kintel
 */
"""

"""
/*
 In options, we can specify:
 * Texture parameters for an auto-generated target texture
 * depthBuffer/stencilBuffer: Booleans to indicate if we should generate these buffers
*/
"""
import THREE._Math as _Math
from THREE.pyOpenGLObject import *
from THREE.Vector4 import*
from THREE.Texture import *


class pyOpenGLRenderTarget(pyOpenGLObject):
    isWebGLRenderTarget = True
    
    def __init__(self, width=0, height=0, options=None ):
        self.uuid = _Math.generateUUID()

        self.width = width
        self.height = height

        self.scissor = Vector4( 0, 0, width, height )
        self.scissorTest = False

        self.viewport = Vector4( 0, 0, width, height )

        options = options or {}

        if 'minFilter' not in options:
            options.minFilter = LinearFilter

        wrapS = options['wrapS'] if 'wrapS' in options else None
        wrapT = options['wrapT'] if 'wrapT' in options else None
        magFilter = options['magFilter'] if 'magFilter' in options else None
        minFilter = options['minFilter'] if 'minFilter' in options else None
        format = options['format'] if 'format' in options else None
        type = options['type'] if 'type' in options else None
        anisotropy = options['anisotropy'] if 'anisotropy' in options else None
        encoding= options['encoding'] if 'encoding' in options else None

        self.texture = Texture( None, None, wrapS, wrapT, magFilter, minFilter, format, type, anisotropy, encoding )

        self.depthBuffer = options['depthBuffer'] if 'depthBuffer' in options else True
        self.stencilBuffer = options['stencilBuffer'] if 'stencilBuffer' in options else True
        self.depthTexture = options['depthTexture'] if 'depthTexture' in options else None
        
        self.callback = None

    def setSize(self, width, height ):
        if self.width != width or self.height != height:
            self.width = width
            self.height = height

            self.dispose()

        self.viewport.set( 0, 0, width, height )
        self.scissor.set( 0, 0, width, height )

    def clone(self):
        return WebGLRenderTarget().copy( self )

    def copy(self, source ):
        self.width = source.width
        self.height = source.height

        self.viewport.copy( source.viewport )

        self.texture = source.texture.clone()

        self.depthBuffer = source.depthBuffer
        self.stencilBuffer = source.stencilBuffer
        self.depthTexture = source.depthTexture

        return self

    def onDispose(self, callback):
        self.callback = callback
        
    def dispose(self):
        if self.callback:
            self.callback(self)
