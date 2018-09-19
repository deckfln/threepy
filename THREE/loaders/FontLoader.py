"""
 * @author mrdoob / http://mrdoob.com/
"""
import json as JSON

from THREE.extras.core.Font import *
from THREE.loaders.FileLoader import *
from THREE.loaders.LoadingManager import *


class FontLoader:
    def __init__(self, manager=None ):
        self.manager = DefaultLoadingManager if manager is not None else manager
        self.path = None

    def load(self, url, onLoad=None, onProgress=None, onError=None ):
        loader = FileLoader( self.manager )
        loader.setPath( self.path )
                
        text = loader.load( url, None, onProgress, onError )
        json = JSON.loads( text )

        font = self.parse( json )

        if onLoad:
            onLoad( font )

        return font

    def parse(self, json ):
        return Font( json )

    def setPath(self, value ):
        self.path = value
        return self
