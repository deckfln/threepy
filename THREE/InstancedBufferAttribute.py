"""
 * @author benaadams / https://twitter.com/ben_a_adams
"""
from THREE.BufferAttribute import *


class InstancedBufferAttribute(BufferAttribute):
    isInstancedBufferAttribute = True

    def __init__(self, array, itemSize, meshPerAttribute):
        super().__init__(array, itemSize)

        self.set_class(isInstancedBufferAttribute)
        self.meshPerAttribute = meshPerAttribute or 1

    def copy(self, source):
        super().copy(source)

        self.meshPerAttribute = source.meshPerAttribute

        return self
