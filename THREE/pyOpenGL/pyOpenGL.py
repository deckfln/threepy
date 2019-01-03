"""
lass to run the pyOpenGL loop
"""

import os
#import pygame as py
import time
import glfw

from OpenGL.GL import *

# from pygame.locals import *
from THREE.pyOpenGL.EventManager import *
from THREE.Constants import *

import THREE.pyOpenGL.window as window


class pyOpenGL(EventManager):
    def __init__(self, params=None):
        super().__init__([
            'resize',
            'animationRequest',
            'contextmenu',
            'mousedown',
            'wheel',
            'touchstart',
            'touchend',
            'touchmove',
            'keydown',
            'keyup',
            'mousemove'
            ])

        self.flip = True

        self.clientWidth = 800
        self.clientHeight = 600
        window.innerWidth = self.clientWidth
        window.innerHeight = self.clientHeight

        self.params = params
        self.run = False

        # save current working directory
        # initialize glfw - this changes cwd
        # restore cwd
        cwd = os.getcwd()
        glfw.init()
        os.chdir(cwd)

        self.win = glfw.create_window(self.clientWidth, self.clientHeight, "test", None, None)
        # version hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, GL_TRUE)
        glfw.window_hint(glfw.DOUBLEBUFFER, GL_TRUE)
        glfw.window_hint(glfw.SAMPLES, glfw.DONT_CARE)

        # make context current
        glfw.make_context_current(self.win)

        #py.init()
        # max_msaa = glGetIntegerv(GL_MAX_SAMPLES)  # unfortunately works only AFTER creating a dummy window
        #py.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        #py.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)
        #py.display.set_mode((self.clientWidth , self.clientHeight ),  py.OPENGL | py.RESIZABLE | py.DOUBLEBUF)

        # set window callbacks
        glfw.set_mouse_button_callback(self.win, self.onMouseButton)
        glfw.set_key_callback(self.win, self.onKeyboard)
        glfw.set_window_size_callback(self.win, self.onSize)
        glfw.set_scroll_callback(self.win, self.onWheel)
        glfw.set_cursor_pos_callback(self.win, self.onMouseMove)
        glfw.set_window_close_callback(self.win, self.onClose)

        self.start = None
        self.previous = None
        self.start_frame = 0
        self.x = 0
        self.y = 0

    def start_benchmark(self):
        self.start = time.clock()
        self.start_frame = self.params.renderer.info.render.frame

    def quit(self):
        self.run = False

    def onMouseButton(self, win, button, action, mods):
        # print('mouse button: ', button, action, mods)

        if action == glfw.PRESS:
            self.dispatchEvent({'type': 'mousedown',
                                'button': button,
                                'pageX': self.x,
                                'pageY': self.y,
                                'clientX': self.x,
                                'clientY': self.y}, self.params)
        elif action == glfw.RELEASE:
            self.dispatchEvent({'type': 'mouseup',
                                'button': button,
                                'pageX': self.x,
                                'pageY': self.y,
                                'clientX': self.x,
                                'clientY': self.y}, self.params)

    def onWheel(self, win, xoffset, yoffset):
        # print('wheel: ', xoffset, yoffset)
        if yoffset < 0:
            # wheel up
            self.dispatchEvent({'type': 'wheel',
                                'deltaMode': -1,
                                'deltaY': 100}, self.params)
        else:
            # wheel down
            self.dispatchEvent({'type': 'wheel',
                                'deltaMode': -1,
                                'deltaY': -100}, self.params)

    def onMouseMove(self, win, xoffset, yoffset):
        self.x = xoffset
        self.y = yoffset
        self.dispatchEvent({'type': 'mousemove',
                            'pageX': xoffset,
                            'pageY': yoffset,
                            'clientX': xoffset,
                            'clientY': yoffset}, self.params)

    def onKeyboard(self, win, key, scancode, action, mods):
        #print('keyboard: ', key, scancode, action, mods)
        if action == glfw.PRESS:
            self.dispatchEvent({'type': 'keydown', 'keyCode': key}, self.params)
        elif action == glfw.RELEASE:
            self.dispatchEvent({'type': 'keyup', 'keyCode': key}, self.params)

    def onSize(self, win, width, height):
        #print 'onsize: ', win, width, height
        window.innerWidth = self.clientWidth = width
        window.innerHeight = self.clientHeight = height
        self.dispatchEvent({'type': 'resize',
                            'width': self.clientWidth,
                            "height": self.clientHeight}, self.params)

    def onClose(self, win):
        self.run = False

    def loop(self):
        self.run = True
        previous = time.clock()
        target = previous + 0.03333333333333

        while self.run:
            if glfw.window_should_close(self.win):
                break

            current = time.clock()

            if self.start is not None:
                if current - self.start > 60:
                   print("Frames:%d" % (self.params.renderer.info.render.frame - self.start_frame))
                   break

            if hasattr(self.params, 'frame_by_frame') and self.params.frame_by_frame:
                if not self.params.suspended:
                    self.animate(self.params)
                    self.params.renderer.init_shaders()
                    glfw.swap_buffers(self.win)
                    print("loop", self.params.renderer.info.render.frame)
                    self.params.suspended = True

            elif current >= target:
                while target <= current:
                    target += 0.03333333333333

                self.animate(self.params)

                # c = time.clock() - current
                # if c > 0.0333333333:
                #    print(c)

                if self.flip:
                    # only flip buffer if some drawing actually happened
                    glfw.swap_buffers(self.win)

            glfw.poll_events()

        glfw.terminate()
