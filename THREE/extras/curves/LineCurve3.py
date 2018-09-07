"""

"""
from THREE.extras.core.Curve import *
from THREE.math.Vector3 import *
from THREE.extras.core.Interpolations import *


class LineCurve3(Curve):
    isLineCurve3 = True

    def __init__(self, v1=None, v2=None):
        super().__init__()
        self.set_class(isLineCurve3)

        self.type = 'LineCurve3'

        self.v1 = v1 or Vector3()
        self.v2 = v2 or Vector3()

    def getPoint(self, t, optionalTarget=None):
        if optionalTarget is None:
            optionalTarget = Vector3()

        point = optionalTarget

        if t == 1:
            return point.copy(self.v2)

        point.copy(self.v2).sub(self.v1)
        point.multiplyScalar(t).add(self.v1)

        return point

    def copy(self, source):
        super().copy(source)

        self.v1.copy( source.v1 )
        self.v2.copy( source.v2 )

        return self

    def toJSON(self):
        data = super().toJSON()

        data['v1'] = self.v1.toArray()
        data['v2'] = self.v2.toArray()

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.v1.fromArray( json['v1'] )
        self.v2.fromArray( json['v2'] )

        return self
