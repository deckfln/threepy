import time
import numpy as np


class Stats:
    def __init__(self, parent=None):
        self.history = np.zeros(30, 'b')
        self.last_frame = 0
        self.last_time = -1
        self.parent = parent

    def set_parent(self, parent):
        self.parent = parent

    def update(self):
        t = time.time()
        if self.last_time > 0 and t < self.last_time + 1:
            return False

        frame = self.parent.renderer.info.render.frame
        self.last_time = t
        fps = frame - self.last_frame
        if fps > 30:
            fps = 30

        self.last_frame = frame

        for i in range(29):
            self.history[i] = self.history[i+1]
        self.history[29] = fps

        bitmap = self.parent.gui_data
        height = self.parent.height
        width = self.parent.width

        for x in range(30):
            fps = self.history[x]
            for y in range(height - 30, height - 30 + fps):
                p = 4*(x + y*width)
                bitmap[p] = 255
                bitmap[p+3] = 255
            for y in range(height - 30 + fps, height):
                p = 4*(x + y*width)
                bitmap[p+3] = 0

        self.parent.texture.needsUpdate = True

        return True
