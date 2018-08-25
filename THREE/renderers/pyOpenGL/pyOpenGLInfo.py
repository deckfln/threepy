"""
@author Mugen87 / https://github.com/Mugen87
"""
from OpenGL.GL import *


class _infoMemory:
    def __init__(self):
        self.geometries = 0
        self.textures = 0


class _infoRender:
    def __init__(self):
        self.frame = 0
        self.calls = 0
        self.triangles = 0
        self.lines = 0
        self.points = 0


class pyOpenGLInfo:
    def __init__(self):
        self.memory = _infoMemory()
        self.render = _infoRender()
        self.programs = None
        self.autoReset = True

    def update(self,  count, mode, instanceCount=1):
        self.render.calls += 1

        if mode == GL_TRIANGLES:
            self.render.triangles += instanceCount * (count / 3)
        elif mode == GL_TRIANGLE_STRIP or mode == GL_TRIANGLE_FAN:
            self.render.triangles += instanceCount * (count - 2)
        elif mode == GL_LINES:
            self.render.lines += instanceCount * (count / 2)
        elif mode == GL_LINE_STRIP:
            self.render.lines += instanceCount * (count - 1)
        elif mode == GL_LINE_LOOP:
            self.render.lines += instanceCount * count
        elif mode == GL_POINTS:
            self.render.points += instanceCount * count

    def reset(self):
        self.render.frame += 1
        self.render.calls = 0
        self.render.triangles = 0
        self.render.points = 0
        self.render.lines = 0
