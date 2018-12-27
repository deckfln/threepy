"""
    @author deckfln
"""

from THREE.math.Sphere import *


class BoundingSphere(Sphere):
    def __init__(self, center=None, radius=0):
        super().__init__(center, radius)
        self.cache = -1
