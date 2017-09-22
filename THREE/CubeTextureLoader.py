"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

class CubeTextureLoader:
    def __init__(self, manager=None ):
        self.manager = manager if manager else DefaultLoadingManager

    def load(self, urls, onLoad, onProgress, onError ):
        return True
