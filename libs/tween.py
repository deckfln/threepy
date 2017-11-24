"""
 * Tween.js - Licensed under the MIT license
 * https:#github.com/tweenjs/tween.js
 * ----------------------------------------------
 *
 * See https:#github.com/tweenjs/tween.js/graphs/contributors for the full list of contributors.
 * Thank you all, you're awesome!
"""
import math
from datetime import datetime


class _Group:
    def __init__(self):
        self._tweens = {}
        self._tweensAddedDuringUpdate = {}
        self._nextId = 0

    def getAll(self):
        return self._tweens

    def removeAll(self):
        self._tweens = {}

    def add(self, tween):
        self._tweens[tween.getId()] = tween
        self._tweensAddedDuringUpdate[tween.getId()] = tween

    def remove(self, tween):
        del self._tweens[tween.getId()]
        del self._tweensAddedDuringUpdate[tween.getId()]

    def update(self, time=None, preserve=False):
        tweenIds = list(self._tweens.keys())

        if len(tweenIds) == 0:
            return False

        time = time if time is not None else datetime.now().timestamp()

        # Tweens are updated in "batches". If you add a new tween during an update, then the
        # new tween will be updated in the next batch.
        # If you remove a tween during an update, it will normally still be updated. However,
        # if the removed tween was added during the current batch, then it will not be updated.
        while len(tweenIds) > 0:
            self._tweensAddedDuringUpdate = {}

            for tids in tweenIds:
                tween = self._tweens[tids]
                if tween is not None and tween.update(time) is False:
                    tween._isPlaying = False
                    if not preserve:
                        del self._tweens[tids]

            tweenIds = self._tweensAddedDuringUpdate.keys()

        return True

    def nextId(self):
        self._nextId += 1
        return self._nextId


Tweens = _Group()


class Tween:
    def __init__(self, obj, group=None):
        self._object = obj
        self._valuesStart = {}
        self._valuesEnd = {}
        self._valuesStartRepeat = {}
        self._duration = 1000
        self._repeat = 0
        self._repeatDelayTime = None
        self._yoyo = False
        self._isPlaying = False
        self._reversed = False
        self._delayTime = 0
        self._startTime = None
        self._easingFunction = Easing_Linear_None
        self._interpolationFunction = Interpolation_Linear
        self._chainedTweens = []
        self._onStartCallback = None
        self._onStartCallbackFired = False
        self._onUpdateCallback = None
        self._onCompleteCallback = None
        self._onStopCallback = None
        self._group = group or Tweens
        self._id = Tweens.nextId()

    def getId(self):
        return self._id

    def to(self, properties, duration=None):
        self._valuesEnd = properties

        if duration is not None:
            self._duration = duration

        return self

    def start(self, time=None):
        self._group.add(self)

        self._isPlaying = True

        self._onStartCallbackFired = False

        self._startTime = time if time is not None else datetime.now().timestamp()
        self._startTime += self._delayTime

        for property in self._valuesEnd:
            # Check if an Array was provided as property value
            if isinstance(self._valuesEnd[property], list):
                if len(self._valuesEnd[property]) == 0:
                    continue

                # Create a local copy of the Array with the start value at the front
                self._valuesEnd[property] = [self._object[property]].concat(self._valuesEnd[property])

            # If `to()` specifies a property that doesn't exist in the source object,
            # we should not set that property in the object
            if self._object[property] is None:
                continue

            # Save the starting value.
            self._valuesStart[property] = self._object[property]

            if not isinstance(self._valuesStart[property], list):
                self._valuesStart[property] *= 1.0     # Ensures we're using numbers, not strings

            self._valuesStartRepeat[property] = self._valuesStart[property] or 0

        return self

    def stop(self):
        if not self._isPlaying:
            return self

        self._group.remove(self)
        self._isPlaying = False

        if self._onStopCallback is not None:
            self._onStopCallback.call(self._object, self._object)

        self.stopChainedTweens()
        return self

    def end(self):
        self.update(self._startTime + self._duration)
        return self

    def stopChainedTweens(self):
        for chainedTween in self._chainedTweens:
            chainedTween.stop()

    def delay(self, amount):
        self._delayTime = amount
        return self

    def repeat(self, times):
        self._repeat = times
        return self

    def repeatDelay(self, amount):
        self._repeatDelayTime = amount
        return self

    def yoyo(self, yoyo):
        self._yoyo = yoyo
        return self

    def easing(self, easing):
        self._easingFunction = easing
        return self

    def interpolation(self, interpolation):
        self._interpolationFunction = interpolation
        return self

    def chain(self):
        self._chainedTweens = arguments
        return self

    def onStart(self, callback):
        self._onStartCallback = callback
        return self

    def onUpdate(self, callback):
        self._onUpdateCallback = callback
        return self

    def onComplete(self, callback):
        self._onCompleteCallback = callback
        return self

    def onStop(self, callback):
        self._onStopCallback = callback
        return self

    def update(self, time):
        if time < self._startTime:
            return True

        if self._onStartCallbackFired is False:
            if self._onStartCallback is not None:
                self._onStartCallback.call(self._object, self._object)

            self._onStartCallbackFired = True

        elapsed = (time - self._startTime) / self._duration * 1000
        elapsed = 1 if elapsed > 1 else elapsed

        value = self._easingFunction(elapsed)

        for property in self._valuesEnd:
            # Don't update properties that do not exist in the source object
            if self._valuesStart[property] is None:
                continue

            start = self._valuesStart[property] or 0
            end = self._valuesEnd[property]

            if isinstance(end, list):
                self._object[property] = self._interpolationFunction(end, value)

            else:
                # Parses relative end values with start as base (e.g.: +10, -3)
                if isinstance(end, str):
                    if end[0] == '+' or end[0] == '-':
                        end = start + float(end)
                    else:
                        end = float(end)

                # Protect against non numeric properties.
                self._object[property] = start + (end - start) * value

        if self._onUpdateCallback is not None:
            self._onUpdateCallback(self._object, value)

        if elapsed == 1:
            if self._repeat > 0:
                if isFinite(self._repeat):
                    self._repeat-=1

                # Reassign starting values, restart by making startTime = now
                for property in self._valuesStartRepeat:
                    if isinstance(self._valuesEnd[property], str):
                        self._valuesStartRepeat[property] = self._valuesStartRepeat[property] + float(self._valuesEnd[property])

                    if self._yoyo:
                        tmp = self._valuesStartRepeat[property]

                        self._valuesStartRepeat[property] = self._valuesEnd[property]
                        self._valuesEnd[property] = tmp

                    self._valuesStart[property] = self._valuesStartRepeat[property]

                if self._yoyo:
                    self._reversed = not self._reversed

                if self._repeatDelayTime is not None:
                    self._startTime = time + self._repeatDelayTime
                else:
                    self._startTime = time + self._delayTime

                return True

            else:
                if self._onCompleteCallback is not None:
                    self._onCompleteCallback.call(self._object, self._object)

                for chainedTween in self._chainedTweens:
                    # Make the chained tweens start exactly at the time they should,
                    # even if the `update()` method was called way past the duration of the tween
                    chainedTween.start(self._startTime + self._duration)

                return False

        return True


def Easing_Linear_None(k):
    return k


def Easing_Quadratic_In(k):
    return k * k


def Easing_Quadratic_Out(k):
    return k * (2 - k)


def Easing_Quadratic_InOut(k):
    k *= 2
    if k  < 1:
        return 0.5 * k * k

    return - 0.5 * (--k * (k - 2) - 1)


def Easing_Cubic_In(k):
    return k * k * k


def Easing_Cubic_Out(k):
    return --k * k * k + 1


def Easing_Cubic_InOut(k):
    k *= 2
    if k < 1:
        return 0.5 * k * k * k

    k -= 2
    return 0.5 * (k * k * k + 2)


def Easing_Quartic_In(k):
    return k * k * k * k


def Easing_Quartic_Out(k):
    k -= 1
    return 1 - (k * k * k * k)


def Easing_Quartic_InOut(k):
    k *= 2
    if k < 1:
        return 0.5 * k * k * k * k

    k -= 2
    return - 0.5 * (k * k * k * k - 2)

def Easing_Quintic_In(k):
    return k * k * k * k * k


def Easing_Quintic_Out(k):
    return --k * k * k * k * k + 1


def Easing_Quintic_InOut(k):
    k *= 2
    if k < 1:
        return 0.5 * k * k * k * k * k

    k -= 2
    return 0.5 * (k * k * k * k * k + 2)


def Easing_Sinusoidal_In(k):
    return 1 - math.cos(k * math.pi / 2)


def Easing_Sinusoidal_Out(k):
    return math.sin(k * math.pi / 2)


def Easing_Sinusoidal_InOut(k):
    return 0.5 * (1 - math.cos(math.pi * k))


def Easing_Exponential_In(k):
    return 0 if k == 0 else math.pow(1024, k - 1)


def Easing_Exponential_Out(k):
    return 1 if k == 1 else 1 - math.pow(2, - 10 * k)


def Easing_Exponential_InOut(k):
    if k == 0:
        return 0

    if k == 1:
        return 1

    k *= 2
    if k  < 1:
        return 0.5 * math.pow(1024, k - 1)

    return 0.5 * (- math.pow(2, - 10 * (k - 1)) + 2)


def Easing_Circular_In(k):
    return 1 - math.sqrt(1 - k * k)


def Easing_Circular_Out(k):
    return math.sqrt(1 - (--k * k))


def Easing_Circular_InOut(k):
    k *= 2
    if k < 1:
        return - 0.5 * (math.sqrt(1 - k * k) - 1)

    k -= 2
    return 0.5 * (math.sqrt(1 - k * k) + 1)


def Easing_Elastic_In(k):
    if k == 0:
        return 0

    if k == 1:
        return 1

    return -math.pow(2, 10 * (k - 1)) * math.sin((k - 1.1) * 5 * math.pi)


def Easing_Elastic_Out(k):
    if k == 0:
        return 0

    if k == 1:
        return 1

    return math.pow(2, -10 * k) * math.sin((k - 0.1) * 5 * math.pi) + 1


def Easing_Elastic_InOut(k):
    if k == 0:
        return 0

    if k == 1:
        return 1

    k *= 2

    if k < 1:
        return -0.5 * math.pow(2, 10 * (k - 1)) * math.sin((k - 1.1) * 5 * math.pi)

    return 0.5 * math.pow(2, -10 * (k - 1)) * math.sin((k - 1.1) * 5 * math.pi) + 1


def Easing__Back_In(k):
    s = 1.70158

    return k * k * ((s + 1) * k - s)


def Easing_Back_Out(k):
    s = 1.70158

    return --k * k * ((s + 1) * k + s) + 1


def Easing_Back_InOut(k):
    s = 1.70158 * 1.525

    k *= 2
    if k < 1:
        return 0.5 * (k * k * ((s + 1) * k - s))

    k -= 2
    return 0.5 * (k * k * ((s + 1) * k + s) + 2)


def Easing_Bounce_In(k):
    return 1 - Easing_Bounce_Out(1 - k)


def Easing_Bounce_Out(k):
    if k < (1 / 2.75):
        return 7.5625 * k * k
    elif k < (2 / 2.75):
        k -= (1.5 / 2.75)
        return 7.5625 * k * k + 0.75
    elif k < (2.5 / 2.75):
        k -= (2.25 / 2.75)
        return 7.5625 * k * k + 0.9375
    else:
        k -= (2.625 / 2.75)
        return 7.5625 * k * k + 0.984375


def Easing_Bounce_InOut(k):
    if k < 0.5:
        return TWEEN.Easing.Bounce.In(k * 2) * 0.5

    return TWEEN.Easing.Bounce.Out(k * 2 - 1) * 0.5 + 0.5

            
def Interpolation_Linear(v, k):
    m = len(v) - 1
    f = m * k
    i = math.floor(f)
    fn = Interpolation_Utils_Linear

    if k < 0:
        return fn(v[0], v[1], f)

    if k > 1:
        return fn(v[m], v[m - 1], m - f)

    return fn(v[i], v[m if i + 1 > m else i + 1], f - i)


def Interpolation_Bezier(v, k):
    b = 0
    n = v.length - 1
    pw = math.pow
    bn = Interpolation_Utils_Bernstein

    for i in range(n):
        b += pw(1 - k, n - i) * pw(k, i) * v[i] * bn(n, i)

    return b


def Interpolation_CatmullRom(v, k):
    m = len(v) - 1
    f = m * k
    i = math.floor(f)
    fn = Interpolation_Utils_CatmullRom

    if v[0] == v[m]:
        if k < 0:
            f = m * (1 + k)
            i = math.floor(f)

        return fn(v[(i - 1 + m) % m], v[i], v[(i + 1) % m], v[(i + 2) % m], f - i)

    else:
        if k < 0:
            return v[0] - (fn(v[0], v[0], v[1], v[1], -f) - v[0])

        if k > 1:
            return v[m] - (fn(v[m], v[m], v[m - 1], v[m - 1], f - m) - v[m])

        return fn(v[i - 1 if i else 0], v[i], v[m if m < i + 1 else i + 1], v[m if m < i + 2 else i + 2], f - i)


def Interpolation_Utils_Linear(p0, p1, t):
    return (p1 - p0) * t + p0


def Interpolation_Utils_Bernstein(n, i):
    fc = Interpolation_Utils_Factorial
    return fc(n) / fc(i) / fc(n - i)


def Interpolation_Utils_Factorial(n):
    a = [1]
    
    s = 1
    
    if a[n]:
        return a[n]
    
    for i in range(n, 0, -1):
        s *= i
    
    a[n] = s
    return s


def Interpolation_Utils_CatmullRom(p0, p1, p2, p3, t):
    v0 = (p2 - p0) * 0.5
    v1 = (p3 - p1) * 0.5
    t2 = t * t
    t3 = t * t2
    
    return (2 * p1 - 2 * p2 + v0 + v1) * t3 + (- 3 * p1 + 3 * p2 - 2 * v0 - v1) * t2 + v0 * t + p1
