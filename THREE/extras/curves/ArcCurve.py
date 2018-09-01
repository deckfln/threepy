"""

"""
from THREE.extras.curves.EllipseCurve import *


class ArcCurve(EllipseCurve):
    isArcCurve = True

    def __init__(self, aX, aY, aRadius, aStartAngle, aEndAngle, aClockwise ):
        super().__init__( aX, aY, aRadius, aRadius, aStartAngle, aEndAngle, aClockwise )

        self.type = 'ArcCurve'
