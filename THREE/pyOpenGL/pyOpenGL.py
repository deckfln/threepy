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

        self.clientWidth = 800
        self.clientHeight = 600
        window.innerWidth = self.clientWidth
        window.innerHeight = self.clientHeight

        self.params = params

    def loop(self):
        t0 = time.time()

        while True:
            t1 = time.time()
            if t1 - t0 > 0.033:
                self.dispatchEvent({'type': 'animationRequest'}, self.params)
                py.display.flip()
                t0 = t1

            event = py.event.poll()
            if event.type == py.QUIT:
                profiler.print()
                py.quit()
                quit()

            elif event.type == py.KEYDOWN:
                self.dispatchEvent({'type': 'keydown', 'key': event.key})

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

            elif event.type != 0:
                print(event.type)

