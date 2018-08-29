"""
 * @author mikael emtinger / http://gomo.se/
 * @author alteredq / http://alteredqualia.com/
 * @author ikerr / http://verold.com
"""

from THREE.core.Object3D import *


class Bone(Object3D):
    isBone = True
    
    def __init__(self):
        super().__init__( )
        self.type = 'Bone'

    def __getitem__(self, item):
        # quaternion and rotation are virtual attributes
        if item == "quaternion":
            return self._quaternion
        if item == "rotation":
            return self._rotation

        if item in self.__dict__:
            return self.__dict__[item]

        return None