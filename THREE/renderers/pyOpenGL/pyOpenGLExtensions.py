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
        self.s = []
        n = glGetIntegerv(GL_NUM_EXTENSIONS)
        for i in range(n):
            self.s.append(glGetStringi(GL_EXTENSIONS, i))

    def get(self, name):
        if name in self.extensions: 
            return self.extensions[ name ]

        self.extensions[name] = name in self.s

        return self.extensions[name]
