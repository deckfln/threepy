"""
    @author deckfln
"""

from THREE.math.Sphere import *


class BoundingSphere(Sphere):
    def __init__(self):
        super().__init__()
        self.cache = -1
