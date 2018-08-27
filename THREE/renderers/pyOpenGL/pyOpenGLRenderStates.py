"""
@author Mugen87 / https://github.com/Mugen87
"""

from THREE.renderers.pyOpenGL.pyOpenGLLights import *


class pyOpenGLRenderState:
	def __init__(self):
		self.lights = pyOpenGLLights()

		self.lightsArray = []
		self.shadowsArray = []

	def init(self):
		self.lightsArray.clear()
		self.shadowsArray.clear()

	def pushLight(self, light):
		self.lightsArray.append(light)

	def pushShadow(self, shadowLight ):
		self.shadowsArray.append(shadowLight)

	def setupLights(self, camera ):
		self.lights.setup( self.lightsArray, self.shadowsArray, camera)


class pyOpenGLRenderStates():
	def __init__(self):
		self.renderStates = {}

	def get(self, scene, camera ):
		if scene.id not in self.renderStates:
			renderState = pyOpenGLRenderState()
			self.renderStates[scene.id] = {}
			self.renderStates[scene.id][camera.id] = renderState
		else:
			if camera.id not in self.renderStates[ scene.id ]:
				renderState = pyOpenGLRenderState()
				self.renderStates[scene.id][camera.id] = renderState
			else:
				renderState = self.renderStates[scene.id][camera.id]

		return renderState

	def dispose(self):
		self.renderStates.clear()
