"""
 *
 * Reusable set of Tracks that represent an animation.
 *
 * @author Ben Houston / http:#clara.io/
 * @author David Sarno / http:#lighthaus.us/
"""
import re
import THREE._Math as _Math
from THREE.KeyframeTrack import *
from THREE.AnimationUtils import *


class AnimationClip:
    def __init__(self, name, duration, tracks ):
        self.name = name
        self.tracks = tracks
        self.duration = duration if ( duration is not None ) else - 1

        self.uuid = _Math.generateUUID()

        # self means it should figure out its duration by scanning the tracks
        if self.duration < 0:
            self.resetDuration()

        self.optimize()

    def parse( json ):
        tracks = []
        jsonTracks = json.tracks,
        frameTime = 1.0 / ( json.fps or 1.0 )

        for i in range(len(jsonTracks)):
            tracks.append( KeyframeTrack.parse( jsonTracks[ i ] ).scale( frameTime ) )

        return AnimationClip( json.name, json.duration, tracks )

    def toJSON( clip ):
        tracks = []
        clipTracks = clip.tracks

        json = {
            'name': clip.name,
            'duration': clip.duration,
            'tracks': tracks
        }

        for i in range(len(clipTracks)):
            tracks.append( KeyframeTrack.toJSON( clipTracks[ i ] ) )

        return json

    def CreateFromMorphTargetSequence( name, morphTargetSequence, fps, noLoop ):
        numMorphTargets = len(morphTargetSequence)
        tracks = []

        for i in range(numMorphTargets):
            times = []
            values = []

            times.extend([
                    ( i + numMorphTargets - 1 ) % numMorphTargets,
                    i,
                    ( i + 1 ) % numMorphTargets 
                    ])

            values.extend([ 0, 1, 0 ])

            order = AnimationUtils.getKeyframeOrder( times )
            times = AnimationUtils.sortedArray( times, 1, order )
            values = AnimationUtils.sortedArray( values, 1, order )

            # if there is a key at the first frame, duplicate it as the
            # last frame as well for perfect loop.
            if not noLoop and times[ 0 ] == 0:
                times.append( numMorphTargets )
                values.append( values[ 0 ] )

            tracks.append(
                    NumberKeyframeTrack(
                        '.morphTargetInfluences[' + morphTargetSequence[ i ].name + ']',
                        times, values
                        ).scale( 1.0 / fps )
                    )

        return AnimationClip( name, - 1, tracks )

    def findByName( objectOrClipArray, name ):
        clipArray = objectOrClipArray

        if not isinstance(objectOrClipArray, list):
            o = objectOrClipArray
            clipArray = o.geometry and o.geometry.animations or o.animations

        for i in range(len(clipArray)):
            if clipArray[ i ].name == name:
                return clipArray[ i ]

        return None

    def CreateClipsFromMorphTargetSequences( morphTargets, fps, noLoop=None):
        animationToMorphTargets = {}

        # tested with https:#regex101.com/ on trick sequences
        # such flamingo_flyA_003, flamingo_run1_003, crdeath0059
        pattern = "^([\w-]*?)([\d]+)$"

        # sort morph target names into animation groups based
        # patterns like Walk_001, Walk_002, Run_001, Run_002
        for i in range(len(morphTargets)):
            morphTarget = morphTargets[ i ]
            parts = re.search(pattern, morphTarget.name)

            if parts is not None:
                name = parts.group( 1 )

                if name not in animationToMorphTargets:
                    animationToMorphTargets[ name ] = animationMorphTargets = []

                animationMorphTargets.append( morphTarget )

        clips = []

        for name in animationToMorphTargets:
            clips.append( AnimationClip.CreateFromMorphTargetSequence( name, animationToMorphTargets[ name ], fps, noLoop ) )

        return clips

    # parse the animation.hierarchy format
    def parseAnimation( animation, bones ):
        if not animation:
            raise RuntimeError( 'THREE.AnimationClip: No animation in JSONLoader data.' )

        def addNonemptyTrack( trackType, trackName, animationKeys, propertyName, destTracks ):
            # only return track if there are actually keys.
            if len(animationKeys) != 0:
                times = []
                values = []

                AnimationUtils.flattenJSON( animationKeys, times, values, propertyName )

                # empty keys are filtered out, so check again
                if len(times) != 0:
                    destTracks.append( trackType( trackName, times, values ) )

        tracks = []

        clipName = animation.name or 'default'
        # automatic length determination in AnimationClip.
        duration = len(animation) or - 1
        fps = animation.fps or 30

        hierarchyTracks = animation.hierarchy or []

        for h in range(len(hierarchyTracks)):
            animationKeys = hierarchyTracks[ h ].keys

            # skip empty tracks
            if not animationKeys or len(animationKeys) == 0:
                continue

            # process morph targets
            if animationKeys[ 0 ].morphTargets:
                # figure out all morph targets used in self track
                morphTargetNames = {}

                for k in range(len(animationKeys)):
                    if animationKeys[ k ].morphTargets:
                        for m in range(len(animationKeys[ k ].morphTargets)):
                            morphTargetNames[ animationKeys[ k ].morphTargets[ m ] ] = - 1

                # create a track for each morph target with all zero
                # morphTargetInfluences except for the keys in which
                # the morphTarget is named.
                for morphTargetName in morphTargetNames:
                    times = []
                    values = []

                    for m in range(len(animationKeys[ k ].morphTargets)):
                        animationKey = animationKeys[ k ]

                        times.append( animationKey.time )
                        values.append( 1 if ( animationKey.morphTarget == morphTargetName ) else 0 )

                    tracks.append( NumberKeyframeTrack( '.morphTargetInfluence[' + morphTargetName + ']', times, values ) )

                duration = morphTargetNames.length * ( fps or 1.0 )

            else:
                # ...assume skeletal animation

                boneName = '.bones[' + bones[ h ].name + ']'

                addNonemptyTrack(
                        VectorKeyframeTrack, boneName + '.position',
                        animationKeys, 'pos', tracks )

                addNonemptyTrack(
                        QuaternionKeyframeTrack, boneName + '.quaternion',
                        animationKeys, 'rot', tracks )

                addNonemptyTrack(
                        VectorKeyframeTrack, boneName + '.scale',
                        animationKeys, 'scl', tracks )

        if len(tracks) == 0:
            return None

        clip = AnimationClip( clipName, duration, tracks )

        return clip

    def resetDuration(self):
        tracks = self.tracks
        duration = 0

        for i in range(len(tracks)):
            track = self.tracks[ i ]

            duration = max( duration, track.times[ len(track.times) - 1 ] )

        self.duration = duration

    def trim(self):
        for i in range(len(self.tracks)):
            self.tracks[ i ].trim( 0, self.duration )

        return self

    def optimize(self):
        for i in range(len(self.tracks)):
            self.tracks[ i ].optimize()

        return self

