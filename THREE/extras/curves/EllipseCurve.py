"""

"""
from THREE.extras.core.Curve import *
from THREE.math.Vector2 import *


class EllipseCurve(Curve):
    isEllipseCurve = True

    def __init__(self, aX=0, aY=0, xRadius=1, yRadius=1, aStartAngle=0, aEndAngle=2*math.pi, aClockwise=False, aRotation=0):
        super().__init__()
        self.type = 'EllipseCurve'
        self.set_class(isEllipseCurve)

        self.aX = aX
        self.aY = aY

        self.xRadius = xRadius
        self.yRadius = yRadius

        self.aStartAngle = aStartAngle
        self.aEndAngle = aEndAngle

        self.aClockwise = aClockwise

        self.aRotation = aRotation

    def getPoint(self, t, optionalTarget=None):
        if optionalTarget is None:
            optionalTarget = Vector2()

        point = optionalTarget

        twoPi = math.pi * 2
        deltaAngle = self.aEndAngle - self.aStartAngle
        samePoints = abs(deltaAngle) < Number.EPSILON

        # // ensures that deltaAngle is 0 .. 2 PI
        while deltaAngle < 0:
            deltaAngle += twoPi
        while deltaAngle > twoPi:
            deltaAngle -= twoPi

        if deltaAngle < Number.EPSILON:
            if samePoints:
                deltaAngle = 0
            else:
                deltaAngle = twoPi

        if self.aClockwise and not samePoints:
            if deltaAngle == twoPi:
                deltaAngle = - twoPi
            else:
                deltaAngle = deltaAngle - twoPi

        angle = self.aStartAngle + t * deltaAngle
        x = self.aX + self.xRadius * math.cos(angle)
        y = self.aY + self.yRadius * math.sin(angle)

        if self.aRotation != 0:
            cos = math.cos(self.aRotation)
            sin = math.sin(self.aRotation)

            tx = x - self.aX
            ty = y - self.aY

            # // Rotate the point about the center of the ellipse.
            x = tx * cos - ty * sin + self.aX
            y = tx * sin + ty * cos + self.aY

        return point.set(x, y)

    def copy(self, source):
        super().copy(source)

        self.aX = source.aX
        self.aY = source.aY

        self.xRadius = source.xRadius
        self.yRadius = source.yRadius

        self.aStartAngle = source.aStartAngle
        self.aEndAngle = source.aEndAngle

        self.aClockwise = source.aClockwise

        self.aRotation = source.aRotation

        return self

    def toJSON(self):
        data = super().toJSON()

        data['aX'] = self.aX
        data['aY'] = self.aY

        data['xRadius'] = self.xRadius
        data['yRadius'] = self.yRadius

        data['aStartAngle'] = self.aStartAngle
        data['aEndAngle'] = self.aEndAngle

        data['aClockwise'] = self.aClockwise

        data['aRotation'] = self.aRotation

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.aX = json['aX']
        self.aY = json['aY']

        self.xRadius = json['xRadius']
        self.yRadius = json['yRadius']

        self.aStartAngle = json['aStartAngle']
        self.aEndAngle = json['aEndAngle']

        self.aClockwise = json['aClockwise']

        self.aRotation = json['aRotation']

        return self
