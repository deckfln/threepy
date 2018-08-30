"""
 *
 * A timed sequence of keyframes for a specific property.
 *
 *
 * @author Ben Houston / http:#clara.io/
 * @author David Sarno / http:#lighthaus.us/
 * @author tschw
"""
from THREE.math.interpolants.LinearInterpolant import *
from THREE.math.interpolants.DiscreteInterpolant import *
from THREE.math.interpolants.CubicInterpolant import *
from THREE.animation.AnimationUtils import *

def _getTrackTypeForValueTypeName(typeName):
    t = typeName.lower()
    if t == "scalar" or t == "double" or t == "float" or t == "number" or t == "integer":
        return NumberKeyframeTrack

    if t == "vector" or t == "vector2" or t == "vector3" or t == "vector4":
        return VectorKeyframeTrack

    if t == "color":
        return ColorKeyframeTrack

    if t == "quaternion":
        return QuaternionKeyframeTrack

    if t == "bool" or t == "boolean":
        return BooleanKeyframeTrack

    if t == "string":
        return StringKeyframeTrack

    raise RuntimeError("Unsupported typeName: " + typeName)


class KeyframeTrack:
    TimeBufferType = 'Float32Array'
    ValueBufferType = 'Float32Array'
    DefaultInterpolation = InterpolateLinear

    def __init__(self, name, times, values, interpolation=None):
        if name is None:
            raise RuntimeWarning( 'THREE.KeyframeTrack: track name is undefined' )
        if times is None or len(times) == 0:
            raise RuntimeWarning( 'THREE.KeyframeTrack: no keyframes in track named ' + name )

        self.name = name

        self.times = AnimationUtils.convertArray(times, self.TimeBufferType)
        self.values = AnimationUtils.convertArray(values, self.ValueBufferType)

        self.createInterpolant = None
        self.setInterpolation(interpolation or self.DefaultInterpolation)

    def toJSON(self, track):
        # by default, we assume the data can be serialized as-is
        json = {
            'name': track.name,
            'times': AnimationUtils.convertArray( track.times, list ),
            'values': AnimationUtils.convertArray( track.values, list )
        }

        interpolation = track.getInterpolation()

        if interpolation != track.DefaultInterpolation:
            json['interpolation'] = interpolation

        json['type'] = track.ValueTypeName      #mandatory

        return json

    def InterpolantFactoryMethodDiscrete(self, result):
        return DiscreteInterpolant(self.times, self.values, self.getValueSize(), result)

    def InterpolantFactoryMethodLinear(self, result):
        return LinearInterpolant(self.times, self.values, self.getValueSize(), result)

    def InterpolantFactoryMethodSmooth(self, result):
        return CubicInterpolant(self.times, self.values, self.getValueSize(), result)

    def setInterpolation(self, interpolation):
        factoryMethod = None

        if interpolation == InterpolateDiscrete:
            factoryMethod = self.InterpolantFactoryMethodDiscrete

        elif interpolation == InterpolateLinear:
            factoryMethod = self.InterpolantFactoryMethodLinear

        elif interpolation == InterpolateSmooth:
            factoryMethod = self.InterpolantFactoryMethodSmooth

        if factoryMethod is None:
            message = "unsupported interpolation for " + self.ValueTypeName + " keyframe track named " + self.name

            if self.createInterpolant is None:
                # fall back to default, unless the default itself is messed up
                if interpolation != self.DefaultInterpolation:
                    self.setInterpolation(self.DefaultInterpolation)

                else:
                    raise RuntimeError(message)  # fatal, in self case

            print('THREE.KeyframeTrackPrototype:', message)
            return

        self.createInterpolant = factoryMethod

    def getInterpolation(self):
        if self.createInterpolant == self.InterpolantFactoryMethodDiscrete:
            return InterpolateDiscrete

        if self.createInterpolant == self.InterpolantFactoryMethodLinear:
            return InterpolateLinear

        if self.createInterpolant == self.InterpolantFactoryMethodSmooth:
            return InterpolateSmooth

    def getValueSize(self):
        return int(len(self.values) / len(self.times))

    # move all keyframes either forwards or backwards in time
    def shift(self, timeOffset):
        if timeOffset != 0.0:
            times = self.times

            for i in range(len(times)):
                times[i] += timeOffset

        return self

    # scale all keyframe times by a factor (useful for frame <-> seconds conversions)
    def scale(self, timeScale):
        if timeScale != 1.0:
            times = self.times

            for i in range(len(times)):
                times[i] *= timeScale

        return self

    # removes keyframes before and after animation without changing any values within the range [startTime, endTime].
    # IMPORTANT: We do not shift around keys to the start of the track time, because for interpolated keys self will change their values
    def trim(self, startTime, endTime):
        times = self.times
        nKeys = len(times)
        fromm = 0
        to = nKeys - 1

        while fromm != nKeys and times[fromm] < startTime:
            fromm += 1

        while to != - 1 and times[to] > endTime:
            to -= 1

        to += 1  # inclusive -> exclusive bound

        if fromm != 0 or to != nKeys:
            # empty tracks are forbidden, so keep at least one keyframe
            if fromm >= to:
                to = max(to, 1)
                fromm = to - 1

            stride = self.getValueSize()
            self.times = AnimationUtils.arraySlice(times, fromm, to )
            self.values = AnimationUtils.arraySlice(self.values, fromm*stride, to * stride )

            return self

    # ensure we do not get a GarbageInGarbageOut situation, make sure tracks are at least minimally viable
    def validate(self):
        valid = True

        valueSize = self.getValueSize()
        if valueSize - math.floor(valueSize) != 0:
            raise RuntimeError('THREE.KeyframeTrackPrototype: Invalid value size in track.', self)

        times = self.times
        values = self.values

        nKeys = len(times)

        if nKeys == 0:
            raise RuntimeError('THREE.KeyframeTrackPrototype: Track is empty.', self)

        prevTime = None

        for i in range(nKeys):
            currTime = times[i]

            if isinstance(currTime, float) and currTime == float("nan"):
                raise RuntimeError('THREE.KeyframeTrackPrototype: Time is not a valid number.', self, i, currTime)

            if prevTime != None and prevTime > currTime:
                raise RuntimeError('THREE.KeyframeTrackPrototype: Out of order keys.', self, i, currTime, prevTime)

            prevTime = currTime

        if values is not None:
            if AnimationUtils.isTypedArray(values):
                for i in range(len(values)):
                    value = values[i]

            if value == float("nan"):
                raise RuntimeError('THREE.KeyframeTrackPrototype: Value is not a valid number.', self, i, value)

        return valid

    # removes equivalent sequential keys as common in morph target sequences
    # (0,0,0,0,1,1,1,0,0,0,0,0,0,0) --> (0,0,1,1,0,0)
    def optimize(self):
        times = self.times
        values = self.values
        stride = self.getValueSize()

        smoothInterpolation = self.getInterpolation() == InterpolateSmooth

        writeIndex = 1
        lastIndex = len(times) - 1

        for i in range(1, lastIndex):
            keep = False

            time = times[i]
            timeNext = times[i + 1]

            # remove adjacent keyframes scheduled at the same time

            if time != timeNext and (i != 1 or time != time[0]):
                if not smoothInterpolation:
                    # remove unnecessary keyframes same as their neighbors
                    offset = i * stride
                    offsetP = offset - stride
                    offsetN = offset + stride

                    for j in range(stride):
                        value = values[offset + j]

                        if value != values[offsetP + j] or value != values[offsetN + j]:
                            keep = True
                            break

                else:
                    keep = True

            # in-place compaction

            if keep:
                if i != writeIndex:
                    times[writeIndex] = times[i]

                    readOffset = i * stride
                    writeOffset = writeIndex * stride

                    for j in range(stride):
                        values[writeOffset + j] = values[readOffset + j]

                writeIndex += 1

        # flush last keyframe (compaction looks ahead)

        if lastIndex > 0:
            times[writeIndex] = times[lastIndex]

            readOffset = lastIndex * stride
            writeOffset = writeIndex * stride

            for j in range(stride):
                values[writeOffset + j] = values[readOffset + j]

            writeIndex += 1

        if writeIndex != len(times):
            self.times = AnimationUtils.arraySlice(times, 0, writeIndex)
            self.values = AnimationUtils.arraySlice(values, 0, writeIndex * stride)

        return self

    """
    #
    # Static methods:
    #
    """
    def parse( json ):
        # Serialization (in static context, because of constructor invocation
        # and automatic invocation of .toJSON):

        if json.type is None:
            raise RuntimeError( "track type undefined, can not parse" )

        trackType = _getTrackTypeForValueTypeName( json.type )

        if json.times is None:
            times = []
            values = []

            AnimationUtils.flattenJSON( json.keys, times, values, 'value' )

            json.times = times
            json.values = values

        # derived classes can define a static parse method
        if trackType.parse is not None:
            return trackType.parse( json )

        else:
            # by default, we assume a constructor compatible with the base
            return trackType(json.name, json.times, json.values, json.interpolation )

    def toJSON( track ):
        trackType = type(track)

        # derived classes can define a static toJSON method
        if trackType.toJSON is not None:
            json = trackType.toJSON( track )

        else:
            # by default, we assume the data can be serialized as-is
            json = {
                'name': track.name,
                'times': AnimationUtils.convertArray( track.times, Array ),
                'values': AnimationUtils.convertArray( track.values, Array )

            }

            interpolation = track.getInterpolation()

            if interpolation != track.DefaultInterpolation:
                json.interpolation = interpolation

        json.type = track.ValueTypeName     # mandatory

        return json

from THREE.animation.tracks.QuaternionKeyframeTrack import *
from THREE.animation.tracks.NumberKeyframeTrack import *
from THREE.animation.tracks.VectorKeyframeTrack import *
from THREE.animation.tracks.ColorKeyframeTrack  import *
from THREE.animation.tracks.BooleanKeyframeTrack import *
from THREE.animation.tracks.StringKeyframeTrack import *
