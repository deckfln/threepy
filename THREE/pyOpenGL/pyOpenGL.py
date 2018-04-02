"""
lass to run the pyOpenGL loop
"""
import pygame as py
import time
from pygame.locals import *
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
            'keyup'
            ])

        self.flip = True

        self.clientWidth = 800
        self.clientHeight = 600
        window.innerWidth = self.clientWidth
        window.innerHeight = self.clientHeight

        self.params = params

        py.init()
        py.display.set_mode((self.clientWidth , self.clientHeight ),  py.OPENGL | py.RESIZABLE | py.HWSURFACE | py.DOUBLEBUF)

        self.events = [py.QUIT, py.KEYDOWN, py.KEYUP, VIDEORESIZE, py.MOUSEBUTTONDOWN, py.MOUSEBUTTONUP, py.MOUSEMOTION]

    # TODO FDE: implement antialias
        # pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        # pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

    def loop(self):
        previous = start = time.clock()
        target = previous + 0.03333333333333

        while True:
            current = time.clock()
            if current - start > 30:
                print("Frames:%d" % self.params.renderer._infoRender.frame)
                break

            if current >= target:
                while target <= current:
                    target += 0.03333333333333

                self.animate(self.params)

                if self.flip:
                    # only flip buffer if some drawing actually happened
                    py.display.flip()

                event = py.event.poll()

                if event.type not in self.events:
                    continue

                if event.type == py.QUIT:
                    py.quit()
                    return 0

                elif event.type == py.KEYDOWN:
                    self.dispatchEvent({'type': 'keydown', 'keyCode': event.key}, self.params)

                elif event.type == py.KEYUP:
                    self.dispatchEvent({'type': 'keyup', 'keyCode': event.key}, self.params)

                elif event.type == VIDEORESIZE:
                    window.innerWidth = self.clientWidth = event.w
                    window.innerHeight = self.clientHeight = event.h
                    self.dispatchEvent({'type': 'resize',
                                        'width': self.clientWidth,
                                        "height": self.clientHeight}, self.params)
                elif event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        # wheel up
                        self.dispatchEvent({'type': 'wheel',
                                            'button': event.button-1,
                                            'deltaMode': -1,
                                            'deltaY': -100}, self.params)
                    elif event.button == 5:
                        # wheel down
                        self.dispatchEvent({'type': 'wheel',
                                            'deltaMode': -1,
                                            'deltaY': 100}, self.params)
                    else:
                        self.dispatchEvent({'type': 'mousedown',
                                            'button': event.button-1,
                                            'pageX': event.pos[0],
                                            'pageY': event.pos[1],
                                            'clientX': event.pos[0],
                                            'clientY': event.pos[1]}, self.params)
                elif event.type == py.MOUSEBUTTONUP:
                    if event.button != 4 and event.button != 5:
                        self.dispatchEvent({'type': 'mouseup',
                                            'button': event.button-1,
                                            'pageX': event.pos[0],
                                            'pageY': event.pos[1],
                                            'clientX': event.pos[0],
                                            'clientY': event.pos[1]}, self.params)

                elif event.type == py.MOUSEMOTION:
                    self.dispatchEvent({'type': 'mousemove',
                                        'pageX': event.pos[0],
                                        'pageY': event.pos[1],
                                        'clientX': event.pos[0],
                                        'clientY': event.pos[1]}, self.params)

                # elif event.type != 0:
                #    pass
                #    #print(event.type)
