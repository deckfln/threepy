"""
/**
 * @author alteredq / http://alteredqualia.com/
 */
"""
import time

class Clock:
    def __init__(self, autoStart=True):
        self.autoStart = autoStart
        self.startTime = 0
        self.oldTime = 0
        self.elapsedTime = 0

        self.running = False

    def start(self):
        self.startTime = time.time()
        self.oldTime = self.startTime
        self.elapsedTime = 0
        self.running = True

    def stop(self):
        self.getElapsedTime()
        self.running = False
        self.autoStart = False

    def getElapsedTime(self):
        self.getDelta()
        return self.elapsedTime

    def getDelta(self):
        diff = 0

        if self.autoStart and not self.running:
            self.start()
            return 0

        if self.running:
            newTime = time.time()

            diff = ( newTime - self.oldTime ) / 1000
            self.oldTime = newTime

            self.elapsedTime += diff

        return diff
