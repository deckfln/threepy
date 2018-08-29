"""
    /**
     * @author mgreter / http://github.com/mgreter
     */
"""
from THREE.objects.Line import *


class LineLoop(Line):
    isLineLoop = True

    def __init__(self,geometry, material):
        super().__init__(geometry, material)

        self.type = 'LineLoop'
        self.set_class(isLineLoop)
