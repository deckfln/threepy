"""

"""

import time
import numpy as np

from THREE.renderers.pyOpenGLGuiRenderer import *


class pyGUI:
    def __init__(self, renderer, frame=None):
        renderer.guiRenderer = pyOpenGLGuiRenderer(renderer, frame)

        self.renderer = renderer

        self.texture = renderer.guiRenderer.texture
        self.gui_data = self.texture.get_data()
        (x, y) = renderer.guiRenderer.texture.image.size
        self.width = x
        self.height = y
        self.widgets = []

    def add(self, widget):
        self.widgets.append(widget)
        widget.set_parent(self)

    def update(self):
        for widget in self.widgets:
            widget.update()

    def load_bar(self, pct):
        t = time.time()
        if self.last_time > 0 and t < self.last_time + 1:
            return

        self.last_time = t

        h = int(self.height / 2)
        pct = int(pct * 200 / 100)

        for y in range(h - 20, h + 20):
            p = 4*y*self.width
            for x in range(0, pct):
                self.gui_data[p] = 255
                self.gui_data[p+3] = 255
                p += 4

        self.texture.needsUpdate = True

    def loaded_tiles(self, nb):
        h = 5
        pct = int(nb * 200 / 100)

        for y in range(h, 0, -1):
            p = 4*y*self.width
            for x in range(0, pct):
                self.gui_data[p] = 255
                self.gui_data[p+3] = 255
                p += 4

        self.texture.needsUpdate = True

    def reset(self):
        self.gui_data.fill(0)
        self.widgets.clear()
        self.texture.needsUpdate = True
