"""
    @author deckfln
"""

from THREE.Sphere import *


class BoundingSphere(Sphere):
    def __init__(self):
        super().__init__()
        self.cache = -1
