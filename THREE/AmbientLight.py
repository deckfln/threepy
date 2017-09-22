"""
/ **
* @ author mrdoob / http: // mrdoob.com /
* /
"""
from THREE.Light import *


class AmbientLight(Light):
    isAmbientLight = True

    def __init__(self, color, intensity=1):
        super().__init__(color, intensity)

        self.type = 'AmbientLight'

        self.castShadow = None
