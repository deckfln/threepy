"""
@author mrdoob / http://mrdoob.com/
"""

class pyOpenGLAnimation:
    def __init__(self):
        self.context = False
        self.isAnimating = False
        self.animationLoop = None

    def onAnimationFrame(self, time, frame ):
        if not self.isAnimating:
            return

        self.animationLoop( time, frame )

        self.context.requestAnimationFrame( onAnimationFrame )

    def start(self):
        if self.isAnimating:
            return
        if animationLoop is None:
            return

        self.context.requestAnimationFrame( onAnimationFrame )

        self.isAnimating = True

    def stop(self):
        self.isAnimating = False

    def setAnimationLoop(self, callback ):
        self.animationLoop = callback

    def setContext( value ):
        context = value;
