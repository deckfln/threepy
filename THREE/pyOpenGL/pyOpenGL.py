"""
lass to run the pyOpenGL loop
"""
import pygame
import time
from pygame.locals import *
from THREE.pyOpenGL.EventManager import *
from THREE.Constants import *

import THREE.pyOpenGL.window as window

class pyOpenGL(EventManager):
    def __init__(self):
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


    def loop(self):
        t0 = time.clock()

        while True:
            t1 = time.clock()
            if t1 - t0 > 0.033:
                self.dispatchEvent({'type': 'animationRequest'})
                pygame.display.flip()
                t0 = t1

            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                profiler.print()
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                self.dispatchEvent({'type': 'keydown', 'key': event.key})

            elif event.type == VIDEORESIZE:
                window.innerWidth = self.clientWidth = event.w
                window.innerHeight = self.clientHeight = event.h
                self.dispatchEvent({'type': 'resize',
                                    'width': self.clientWidth,
                                    "height": self.clientHeight})
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    # wheel up
                    self.dispatchEvent({'type': 'wheel',
                                        'button': event.button-1,
                                        'deltaMode': -1,
                                        'deltaY': -100})
                elif event.button == 5:
                    # wheel down
                    self.dispatchEvent({'type': 'wheel',
                                        'deltaMode': -1,
                                        'deltaY': 100})
                else:
                    self.dispatchEvent({'type': 'mousedown',
                                        'button': event.button-1,
                                        'pageX': event.pos[0],
                                        'pageY': event.pos[1],
                                        'clientX': event.pos[0],
                                        'clientY': event.pos[1]})
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button != 4 and event.button != 5:
                    self.dispatchEvent({'type': 'mouseup',
                                        'button': event.button-1,
                                        'pageX': event.pos[0],
                                        'pageY': event.pos[1],
                                        'clientX': event.pos[0],
                                        'clientY': event.pos[1]})

            elif event.type == pygame.MOUSEMOTION:
                self.dispatchEvent({'type': 'mousemove',
                                    'pageX': event.pos[0],
                                    'pageY': event.pos[1],
                                    'clientX': event.pos[0],
                                    'clientY': event.pos[1]})

            elif event.type != 0:
                print(event.type)
