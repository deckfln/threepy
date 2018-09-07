"""

"""
from THREE.extras.core.Curve import *
from THREE.math.Vector2 import *
from THREE.extras.core.Interpolations import*


class SplineCurve(Curve):
    isSplineCurve = True

    def __init__(self, points=None):
        super().__init__()
        self.set_class(isSplineCurve)
        self.type = 'SplineCurve'

        self.points = [] if points is None else points

    def getPoint(self, t, optionalTarget=None):
        if optionalTarget is None:
            optionalTarget = Vector2()

        points = self.points
        point = (len(self.points) - 1) * t

        intPoint = int(point)
        weight = point - intPoint

        point0 = points[intPoint if intPoint == 0 else intPoint - 1]
        point1 = points[intPoint]
        point2 = points[points.length - 1 if intPoint > points.length - 2 else intPoint + 1]
        point3 = points[points.length - 1 if intPoint > points.length - 3 else intPoint + 2]

        return point.set(
            CatmullRom(weight, point0.x, point1.x, point2.x, point3.x),
            CatmullRom(weight, point0.y, point1.y, point2.y, point3.y)
        )

    def copy(self, source):
        super().copy(source)

        self.points = []

        for point in source.points:
            self.points.append( point.clone())

        return self

    def toJSON(self):
        data = super().toJSON()

        data['points'] = []

        for point in self.points:
            data['points'].append( point.toArray() )

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.points = []

        for point in json['points']:
            self.points.append( point.fromArray(point))

        return self

