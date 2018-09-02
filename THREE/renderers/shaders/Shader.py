"""
@author deckefln
"""
from THREE.renderers.shaders.ShaderLib import *


class Shader:
    def __init__(self, name, uniforms, vertexShader, fragmentShader):
        self.name = name
        self.uniforms = uniforms

        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader
