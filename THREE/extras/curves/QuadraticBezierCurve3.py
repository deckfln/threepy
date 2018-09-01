"""

"""
from THREE.extras.core.Curve import *
from THREE.math.Vector3 import *
from THREE.extras.core.Interpolations import *


class QuadraticBezierCurve3(Curve):
    isQuadraticBezierCurve3 = True

    def __init__(self, v0=None, v1=None, v2=None):
        super().__init__()

        self.type = 'QuadraticBezierCurve3'

        self.v0 = v0 or Vector3()
        self.v1 = v1 or Vector3()
        self.v2 = v2 or Vector3()

    def getPoint(self, t, optionalTarget=None):
        if optionalTarget is None:
            optionalTarget = Vector3()

        point = optionalTarget

        v0 = self.v0
        v1 = self.v1
        v2 = self.v2

        return point.set(
            QuadraticBezier(t, v0.x, v1.x, v2.x),
            QuadraticBezier(t, v0.y, v1.y, v2.y),
            QuadraticBezier(t, v0.z, v1.z, v2.z)
        )

    def copy(self, source):
        super().copy(source )

        self.v0.copy( source.v0 )
        self.v1.copy( source.v1 )
        self.v2.copy( source.v2 )

        return self

    def toJSON(self):
        data = super().toJSON()

        data['v0'] = self.v0.toArray()
        data['v1'] = self.v1.toArray()
        data['v2'] = self.v2.toArray()

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.v0.fromArray(json['v0'])
        self.v1.fromArray(json['v1'])
        self.v2.fromArray(json['v2'])

        return self
