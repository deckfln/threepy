"""
/**
 * @author benaadams / https://twitter.com/ben_a_adams
 */
"""
from THREE.core.InterleavedBuffer import *


class InstancedInterleavedBuffer(InterleavedBuffer):
    isInstancedInterleavedBuffer = True

    def __init__(self, array, stride, meshPerAttribute):
        super().__init__(array, stride)

        self.set_class(isInstancedInterleavedBuffer)
        self.meshPerAttribute = meshPerAttribute or 1

    def copy(self, source):
        super().copy(source)

        self.meshPerAttribute = source.meshPerAttribute

        return self
