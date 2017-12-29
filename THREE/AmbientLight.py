"""
/ **
* @ author mrdoob / http: // mrdoob.com /
* /
"""
from THREE.Light import *


class AmbientLight(Light):
    isAmbientLight = True

    def __init__(self, color=0xffffff, intensity=1):
        super().__init__(color, intensity)
        self.set_class(isAmbientLight)

        self.type = 'AmbientLight'

        self.castShadow = None
