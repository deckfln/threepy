"""
/**
 * @author abelnation / http://github.com/abelnation
 */
"""
from THREE.lights.Light import *


class RectAreaLight(Light):
    isRectAreaLight: True

    def __init__(self, color, intensity, width=10, height=10 ):
        super().__init__( color, intensity )

        self.type = 'RectAreaLight'
        self.set_class(isRectAreaLight)
        self.width = width
        self.height = height

    def copy(self, source):
        super().copy(source)

        self.width = source.width
        self.height = source.height

        return self

	def toJSON(self, meta):
		data = super().toJSON(meta)

		data.object.width = self.width
		data.object.height = self.height

		return data
