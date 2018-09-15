"""
 * A bunch of parametric curves
 * @author zz85
 *
 * Formulas collected from various sources
 * http://mathworld.wolfram.com/HeartCurve.html
 * http://mathdl.maa.org/images/upload_library/23/stemkoski/knots/page6.html
 * http://en.wikipedia.org/wiki/Viviani%27s_curve
 * http://mathdl.maa.org/images/upload_library/23/stemkoski/knots/page4.html
 * http://www.mi.sanu.ac.rs/vismath/taylorapril2011/Taylor.pdf
 * http://prideout.net/blog/?p=44
"""
import math
from THREE.extras.core.Curve import *
from THREE.math.Vector3 import *


class GrannyKnot(Curve):
    def __init__(self):
        super().__init__()

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t = 2 * math.pi * t

        x = - 0.22 * math.cos(t) - 1.28 * math.sin(t) - 0.44 * math.cos(3 * t) - 0.78 * math.sin(3 * t)
        y = - 0.1 * math.cos(2 * t) - 0.27 * math.sin(2 * t) + 0.38 * math.cos(4 * t) + 0.46 * math.sin(4 * t)
        z = 0.7 * math.cos(3 * t) - 0.4 * math.sin(3 * t)

        return point.set(x, y, z).multiplyScalar(20)

        
class HeartCurve(Curve):
    def __init__(self, scale=5):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t *= 2 * math.pi

        x = 16 * pow(math.sin(t), 3)
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        z = 0

        return point.set(x, y, z).multiplyScalar(self.scale)

        
class VivianiCurve(Curve):
    def __init__(self, scale=70):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t = t * 4 * math.pi    # normalized to 0..1
        a = self.scale / 2

        x = a * (1 + math.cos(t))
        y = a * math.sin(t)
        z = 2 * a * math.sin(t / 2)

        return point.set(x, y, z)

        
class KnotCurve(Curve):
    def __init__(self):
        super().__init__()

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t *= 2 * math.pi

        R = 10
        s = 50

        x = s * math.sin(t)
        y = math.cos(t) * (R + s * math.cos(t))
        z = math.sin(t) * (R + s * math.cos(t))

        return point.set(x, y, z)

        
class HelixCurve(Curve):
    def __init__(self):
        super().__init__()

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        a = 30    # // radius
        b = 150    # // height

        t2 = 2 * math.pi * t * b / 30

        x = math.cos(t2) * a
        y = math.sin(t2) * a
        z = b * t

        return point.set(x, y, z)


class TrefoilKnot(Curve):
    def __init__(self, scale=10):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t *= math.pi * 2

        x = (2 + math.cos(3 * t)) * math.cos(2 * t)
        y = (2 + math.cos(3 * t)) * math.sin(2 * t)
        z = math.sin(3 * t)

        return point.set(x, y, z).multiplyScalar(self.scale)

        
class TorusKnot(Curve):
    def __init__(self, scale=10):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        p = 3
        q = 4

        t *= math.pi * 2

        x = (2 + math.cos(q * t)) * math.cos(p * t)
        y = (2 + math.cos(q * t)) * math.sin(p * t)
        z = math.sin(q * t)

        return point.set(x, y, z).multiplyScalar(self.scale)


class CinquefoilKnot(Curve):
    def __init__(self, scale=10):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        p = 2
        q = 5

        t *= math.pi * 2

        x = (2 + math.cos(q * t)) * math.cos(p * t)
        y = (2 + math.cos(q * t)) * math.sin(p * t)
        z = math.sin(q * t)

        return point.set(x, y, z).multiplyScalar(self.scale)

        
class TrefoilPolynomialKnot(Curve):
    def __init__(self, scale=10):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t = t * 4 - 2

        x = pow(t, 3) - 3 * t
        y = pow(t, 4) - 4 * t * t
        z = 1 / 5 * pow(t, 5) - 2 * t

        return point.set(x, y, z).multiplyScalar(self.scale)

        
def _scaleTo(x, y, t):
    r = y - x
    return t * r + x


class FigureEightPolynomialKnot(Curve):
    def __init__(self, scale=1):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t = _scaleTo(- 4, 4, t)

        x = 2 / 5 * t * (t * t - 7) * (t * t - 10)
        y = pow(t, 4) - 13 * t * t
        z = 1 / 10 * t * (t * t - 4) * (t * t - 9) * (t * t - 12)

        return point.set(x, y, z).multiplyScalar(self.scale)


class DecoratedTorusKnot4a(Curve):
    def __init__(self, scale=40):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        t *= math.pi * 2

        x = math.cos(2 * t) * (1 + 0.6 * (math.cos(5 * t) + 0.75 * math.cos(10 * t)))
        y = math.sin(2 * t) * (1 + 0.6 * (math.cos(5 * t) + 0.75 * math.cos(10 * t)))
        z = 0.35 * math.sin(5 * t)

        return point.set(x, y, z).multiplyScalar(self.scale)


class DecoratedTorusKnot4b(Curve):
    def __init__(self, scale=40):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        fi = t * math.pi * 2

        x = math.cos(2 * fi) * (1 + 0.45 * math.cos(3 * fi) + 0.4 * math.cos(9 * fi))
        y = math.sin(2 * fi) * (1 + 0.45 * math.cos(3 * fi) + 0.4 * math.cos(9 * fi))
        z = 0.2 * math.sin(9 * fi)

        return point.set(x, y, z).multiplyScalar(self.scale)


class DecoratedTorusKnot5a(Curve):
    def __init__(self, scale=40):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        fi = t * math.pi * 2

        x = math.cos(3 * fi) * (1 + 0.3 * math.cos(5 * fi) + 0.5 * math.cos(10 * fi))
        y = math.sin(3 * fi) * (1 + 0.3 * math.cos(5 * fi) + 0.5 * math.cos(10 * fi))
        z = 0.2 * math.sin(20 * fi)

        return point.set(x, y, z).multiplyScalar(self.scale)


class DecoratedTorusKnot5c(Curve):
    def __init__(self, scale=40):
        super().__init__()
        self.scale = scale

    def getPoint(self, t, optionalTarget=None):
        point = optionalTarget if optionalTarget else Vector3()

        fi = t * math.pi * 2

        x = math.cos(4 * fi) * (1 + 0.5 * (math.cos(5 * fi) + 0.4 * math.cos(20 * fi)))
        y = math.sin(4 * fi) * (1 + 0.5 * (math.cos(5 * fi) + 0.4 * math.cos(20 * fi)))
        z = 0.35 * math.sin(15 * fi)

        return point.set(x, y, z).multiplyScalar(self.scale)
