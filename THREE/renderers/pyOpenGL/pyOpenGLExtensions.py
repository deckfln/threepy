"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from OpenGL import *
# from OpenGL_accelerate import *
from OpenGL.GL import *

from THREE.Constants import *


class pyOpenGLExtensions():
    def __init__(self):
        self.extensions = {}
        self.s = (glGetString(GL_EXTENSIONS)).decode("utf-8")

    def get(self, name):
        if name in self.extensions: 
            return self.extensions[ name ]

        self.extensions[name] = name in self.s

        return self.extensions[name]
