"""
 * Action provided by AnimationMixer for scheduling clip playback on specific
 * objects.
 *
 * @author Ben Houston / http:#clara.io/
 * @author David Sarno / http:#lighthaus.us/
 * @author tschw
"""
from THREE.Constants import *


class AnimationAction:
    def __init__(self, mixer, clip, localRoot ):
        self._mixer = mixer
        self._clip = clip
        self._localRoot = localRoot or None

        tracks = clip.tracks
        nTracks = len(tracks)
        interpolants = [None for i in range(nTracks )]

        interpolantSettings = {
            'endingStart':     ZeroCurvatureEnding,
            'endingEnd':        ZeroCurvatureEnding
        }

        for i in range(nTracks):
            interpolant = tracks[ i ].createInterpolant( None )
            interpolants[ i ] = interpolant
            interpolant.settings = interpolantSettings

        self._interpolantSettings = interpolantSettings

        self._interpolants = interpolants    # bound by the mixer

        # inside: PropertyMixer (managed by the mixer)
        self._propertyBindings = [ None for i in range(nTracks )]

        self._cacheIndex = None            # for the memory manager
        self._byClipCacheIndex = None        # for the memory manager

        self._timeScaleInterpolant = None
        self._weightInterpolant = None

        self.loop = LoopRepeat
        self._loopCount = -1

        # global mixer time when the action is to be started
        # it's set back to 'None' upon start of the action
        self._startTime = None

        # scaled local time of the action
        # gets clamped or wrapped to 0..clip.duration according to loop
        self.time = 0

        self.timeScale = 1
        self._effectiveTimeScale = 1

        self.weight = 1
        self._effectiveWeight = 1

        self.repetitions = float("+Inf")         # no. of repetitions when looping

        self.paused = False                # True -> zero effective time scale
        self.enabled = True                # False -> zero effective weight

        self.clampWhenFinished     = False    # keep feeding the last frame?

        self.zeroSlopeAtStart     = True        # for smooth interpolation w/o separate
        self.zeroSlopeAtEnd        = True        # clips for start, loop and end

    # State & Scheduling
    def play(self):
        self._mixer._activateAction( self )
        return self

    def stop(self):
        self._mixer._deactivateAction( self )
        return self.reset()

    def reset(self):
        self.paused = False
        self.enabled = True

        self.time = 0            # restart clip
        self._loopCount = -1    # forget previous loops
        self._startTime = None    # forget scheduling

        return self.stopFading().stopWarping()

    def isRunning(self):
        return self.enabled and not self.paused and self.timeScale != 0 and \
                self._startTime is None and self._mixer._isActiveAction( self )

    # return True when play has been called
    def isScheduled(self):
        return self._mixer._isActiveAction( self )

    def startAt(self, time ):
        self._startTime = time
        return self

    def setLoop(self, mode, repetitions ):
        self.loop = mode
        self.repetitions = repetitions
        return self

    # Weight

    # set the weight stopping any scheduled fading
    # although .enabled = False yields an effective weight of zero, self
    # method does *not* change .enabled, because it would be confusing
    def setEffectiveWeight(self, weight ):
        self.weight = weight

        # note: same logic as when updated at runtime
        self._effectiveWeight = weight if self.enabled else 0
        return self.stopFading()

    # return the weight considering fading and .enabled
    def getEffectiveWeight(self):
        return self._effectiveWeight

    def fadeIn(self, duration ):
        return self._scheduleFading( duration, 0, 1 )

    def fadeOut(self, duration ):
        return self._scheduleFading( duration, 1, 0 )

    def crossFadeFrom(self, fadeOutAction, duration, warp=False ):
        fadeOutAction.fadeOut( duration )
        self.fadeIn( duration )

        if warp:
            fadeInDuration = self._clip.duration
            fadeOutDuration = fadeOutAction._clip.duration

            startEndRatio = fadeOutDuration / fadeInDuration
            endStartRatio = fadeInDuration / fadeOutDuration

            fadeOutAction.warp( 1.0, startEndRatio, duration )
            self.warp( endStartRatio, 1.0, duration )

        return self

    def crossFadeTo(self, fadeInAction, duration, warp=False ):
        return fadeInAction.crossFadeFrom( self, duration, warp)

    def stopFading(self):
        weightInterpolant = self._weightInterpolant

        if weightInterpolant is not None:
            self._weightInterpolant = None
            self._mixer._takeBackControlInterpolant( weightInterpolant )

        return self

    # Time Scale Control

    # set the time scale stopping any scheduled warping
    # although .paused = True yields an effective time scale of zero, self
    # method does *not* change .paused, because it would be confusing
    def setEffectiveTimeScale(self, timeScale ):
        self.timeScale = timeScale
        self._effectiveTimeScale = 0 if self.paused else timeScale
        return self.stopWarping()

    # return the time scale considering warping and .paused
    def getEffectiveTimeScale(self):
        return self._effectiveTimeScale

    def setDuration(self, duration ):
        self.timeScale = self._clip.duration / duration
        return self.stopWarping()

    def syncWith(self, action ):
        self.time = action.time
        self.timeScale = action.timeScale
        return self.stopWarping()

    def halt(self, duration ):
        return self.warp( self._effectiveTimeScale, 0, duration )

    def warp(self, startTimeScale, endTimeScale, duration ):
        mixer = self._mixer
        now = mixer.time
        interpolant = self._timeScaleInterpolant

        timeScale = self.timeScale

        if interpolant is None:
            interpolant = mixer._lendControlInterpolant()
            self._timeScaleInterpolant = interpolant

        times = interpolant.parameterPositions
        values = interpolant.sampleValues

        times[ 0 ] = now
        times[ 1 ] = now + duration

        values[ 0 ] = startTimeScale / timeScale
        values[ 1 ] = endTimeScale / timeScale

        return self

    def stopWarping(self):
        timeScaleInterpolant = self._timeScaleInterpolant

        if timeScaleInterpolant is not None:
            self._timeScaleInterpolant = None
            self._mixer._takeBackControlInterpolant( timeScaleInterpolant )

        return self

    # Object Accessors
    def getMixer(self):
        return self._mixer

    def getClip(self):
        return self._clip

    def getRoot(self):
        return self._localRoot or self._mixer._root

    # Interna
    def _update(self, time, deltaTime, timeDirection, accuIndex ):
        # called by the mixer

        if not self.enabled:
            # call ._updateWeight() to update ._effectiveWeight

            self._updateWeight( time )
            return

        startTime = self._startTime

        if startTime is not None:
            # check for scheduled start of action

            timeRunning = ( time - startTime ) * timeDirection
            if timeRunning < 0 or timeDirection == 0:
                return # yet to come / don't decide when delta = 0

            # start

            self._startTime = None # unschedule
            deltaTime = timeDirection * timeRunning

        # apply time scale and advance time

        deltaTime *= self._updateTimeScale( time )
        clipTime = self._updateTime( deltaTime )

        # note: _updateTime may disable the action resulting in
        # an effective weight of 0

        weight = self._updateWeight( time )

        if weight > 0:
            interpolants = self._interpolants
            propertyMixers = self._propertyBindings

            for j in range(len(interpolants)):
                interpolants[ j ].evaluate( clipTime )
                propertyMixers[ j ].accumulate( accuIndex, weight )

    def _updateWeight(self, time ):
        weight = 0

        if self.enabled:
            weight = self.weight
            interpolant = self._weightInterpolant

            if interpolant is not None:
                interpolantValue = interpolant.evaluate( time )[ 0 ]
                weight *= interpolantValue

                if time > interpolant.parameterPositions[ 1 ]:
                    self.stopFading()

                    if interpolantValue == 0:
                        # faded out, disable
                        self.enabled = False

        self._effectiveWeight = weight
        return weight

    def _updateTimeScale(self, time ):
        timeScale = 0

        if not self.paused:
            timeScale = self.timeScale

            interpolant = self._timeScaleInterpolant

            if interpolant is not None:
                interpolantValue = interpolant.evaluate( time )[ 0 ]

                timeScale *= interpolantValue

                if time > interpolant.parameterPositions[ 1 ]:
                    self.stopWarping()

                    if timeScale == 0:
                        # motion has halted, pause
                        self.paused = True
                    else:
                        # warp done - apply final time scale
                        self.timeScale = timeScale

        self._effectiveTimeScale = timeScale
        return timeScale

    def _updateTime(self, deltaTime ):
        time = self.time + deltaTime

        if deltaTime == 0:
            return time
        duration = self._clip.duration

        loop = self.loop
        loopCount = self._loopCount

        if loop == LoopOnce:
            if loopCount == -1:
                # just started

                self._loopCount = 0
                self._setEndings( True, True, False )

            handle_stop = False
            if time >= duration:
                time = duration
            elif time < 0:
                time = 0
            else:
                handle_stop = True
            
            if not handle_stop:
                if self.clampWhenFinished:
                    self.paused = True
                else:
                    self.enabled = False

                self._mixer.dispatchEvent( {
                    'type': 'finished',
                    'action': self,
                    'direction': -1 if deltaTime < 0 else 1
                } )

        else:     # repetitive Repeat or PingPong
            pingPong = ( loop == LoopPingPong )

            if loopCount == -1:
                # just started

                if deltaTime >= 0:
                    loopCount = 0

                    self._setEndings(True, self.repetitions == 0, pingPong )

                else:
                    # when looping in reverse direction, the initial
                    # transition through zero counts as a repetition,
                    # so leave loopCount at -1

                    self._setEndings(self.repetitions == 0, True, pingPong )

            if time >= duration or time < 0:
                # wrap around

                loopDelta = math.floor( time / duration ) # signed
                time -= duration * loopDelta

                loopCount += abs( loopDelta )

                pending = self.repetitions - loopCount

                if pending < 0:
                    # have to stop (switch state, clamp time, fire event)

                    if self.clampWhenFinished:
                        self.paused = True
                    else:
                        self.enabled = False

                    time = duration if deltaTime > 0 else 0

                    self._mixer.dispatchEvent( {
                        'type': 'finished',
                        'action': self,
                        'direction': 1 if deltaTime > 0 else -1
                    } )

                else:
                    # keep running

                    if pending == 0:
                        # entering the last round

                        atStart = deltaTime < 0
                        self._setEndings( atStart, not atStart, pingPong )

                    else:
                        self._setEndings( False, False, pingPong )

                    self._loopCount = loopCount

                    self._mixer.dispatchEvent( {
                        'type': 'loop', 
                        'action': self, 
                        'loopDelta': loopDelta
                    } )

            if pingPong and ( loopCount & 1 ) == 1:
                # invert time for the "pong round"

                self.time = time
                return duration - time

        self.time = time
        return time

    def _setEndings(self, atStart, atEnd, pingPong ):
        settings = self._interpolantSettings

        if pingPong:
            settings['endingStart']     = ZeroSlopeEnding
            settings['endingEnd']        = ZeroSlopeEnding

        else:
            # assuming for LoopOnce atStart == atEnd == True
            if atStart:
                settings['endingStart'] = ZeroSlopeEnding if self.zeroSlopeAtStart else ZeroCurvatureEnding

            else:
                settings['endingStart'] = WrapAroundEnding

            if atEnd:
                settings['endingEnd'] = ZeroSlopeEnding if self.zeroSlopeAtEnd else ZeroCurvatureEnding

            else:
                settings['endingEnd']      = WrapAroundEnding
                
    def _scheduleFading(self, duration, weightNow, weightThen ):
        mixer = self._mixer
        now = mixer.time
        interpolant = self._weightInterpolant

        if interpolant is None:
            interpolant = mixer._lendControlInterpolant()
            self._weightInterpolant = interpolant

        times = interpolant.parameterPositions
        values = interpolant.sampleValues

        times[ 0 ] = now
        values[ 0 ] = weightNow
        times[ 1 ] = now + duration    
        values[ 1 ] = weightThen

        return self
