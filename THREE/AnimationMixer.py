"""
 *
 * Player for AnimationClips.
 *
 *
 * @author Ben Houston / http:#clara.io/
 * @author David Sarno / http:#lighthaus.us/
 * @author tschw
"""
import numpy as np

from THREE.pyOpenGL.EventManager import *
from THREE.javascriparray import *
from THREE.AnimationClip import *
from THREE.PropertyMixer import *
from THREE.PropertyBinding import *
from THREE.AnimationAction import *


class _stat:
        def __init__(self, parent):
            self.parent = parent
            self.actions = None
            self.bindings = None
            self.controlInterpolants = None

        def actions_get_total(self):
            return len(self.parent._actions)

        def actions_getinUse(self):
            return self.parent._nActiveActions

        def bindings_gettotal(self):
            return len(self.parent._bindings)

        def bindings_getinUse(self):
            return self.parent._nActiveBindings

        def controlInterpolants_gettotal(self):
            return len(self.parent._controlInterpolants)

        def controlInterpolants_getinUse(self):
            return self.parent._nActiveControlInterpolants


class _actionsForClip:
    def __init__(self, action):
            self.knownActions = [action]
            self.actionByRoot = {}


class AnimationMixer(EventManager):
    def __init__(self, root ):
        super().__init__()
        self._root = root
        self._initMemoryManager()
        self._accuIndex = 0

        self.time = 0

        self.timeScale = 1.0

        self._controlInterpolantsResultBuffer = Float32Array( 1 )

    def _bindAction(self, action, prototypeAction ):
        root = action._localRoot or self._root
        tracks = action._clip.tracks
        nTracks = len(tracks)
        bindings = action._propertyBindings
        interpolants = action._interpolants
        rootUuid = root.uuid
        bindingsByRoot = self._bindingsByRootAndName

        if rootUuid not in bindingsByRoot:
            bindingsByName = {}
            bindingsByRoot[ rootUuid ] = bindingsByName
        else:
            bindingsByName = bindingsByRoot[rootUuid]

        for i in range(nTracks):
            track = tracks[ i ]
            trackName = track.name

            if trackName in bindingsByName:
                binding = bindingsByName[trackName]
                bindings[ i ] = binding
            else:
                binding = bindings[ i ]

                if binding is not None:
                    # existing binding, make sure the cache knows

                    if binding._cacheIndex is None:
                        binding.referenceCount += 1
                        self._addInactiveBinding( binding, rootUuid, trackName )

                    continue

                path = prototypeAction and prototypeAction._propertyBindings[ i ].binding.parsedPath

                binding = PropertyMixer(
                    PropertyBinding.create( root, trackName, path ),
                    track.ValueTypeName, track.getValueSize() )

                binding.referenceCount += 1
                self._addInactiveBinding( binding, rootUuid, trackName )

                bindings[ i ] = binding

            interpolants[ i ].resultBuffer = binding.buffer

    def _activateAction(self, action ):
        if not self._isActiveAction( action ):
            if action._cacheIndex is None:
                # this action has been forgotten by the cache, but the user
                # appears to be still using it -> rebind

                rootUuid = ( action._localRoot or self._root ).uuid
                clipUuid = action._clip.uuid
                actionsForClip = self._actionsByClip[ clipUuid ]

                self._bindAction( action,
                    actionsForClip and actionsForClip.knownActions[ 0 ] )

                self._addInactiveAction( action, clipUuid, rootUuid )

            bindings = action._propertyBindings

            # increment reference counts / sort out state
            for i in range(len(bindings)):
                binding = bindings[ i ]

                if binding.useCount == 0:
                    self._lendBinding( binding )
                    binding.saveOriginalState()
                binding.useCount += 1

            self._lendAction( action )

    def _deactivateAction(self, action ):
        if self._isActiveAction( action ):
            bindings = action._propertyBindings

            # decrement reference counts / sort out state
            for i in range(len(bindings)):
                binding = bindings[ i ]

                binding.useCount -= 1
                if  binding.useCount == 0:
                    binding.restoreOriginalState()
                    self._takeBackBinding( binding )

            self._takeBackAction( action )

    # Memory manager

    def _initMemoryManager(self):
        self._actions = []     # 'nActiveActions' followed by inactive ones
        self._nActiveActions = 0

        self._actionsByClip = {}
        # inside:
        # {
        #         knownActions: Array< AnimationAction >    - used as prototypes
        #         actionByRoot: AnimationAction            - lookup
        # }


        self._bindings = []     # 'nActiveBindings' followed by inactive ones
        self._nActiveBindings = 0

        self._bindingsByRootAndName = {}     # inside: Map< name, PropertyMixer >


        self._controlInterpolants = []     # same game as above
        self._nActiveControlInterpolants = 0

        scope = self

        self.stats = _stat(self)

    # Memory management for AnimationAction objects

    def _isActiveAction(self, action ):
        index = action._cacheIndex
        return index is not None and index < self._nActiveActions

    def _addInactiveAction(self, action, clipUuid, rootUuid ):
        actions = self._actions
        actionsByClip = self._actionsByClip

        if clipUuid not in actionsByClip:
            actionsForClip = _actionsForClip(action)

            action._byClipCacheIndex = 0

            actionsByClip[ clipUuid ] = actionsForClip

        else:
            actionsForClip = actionsByClip[clipUuid]
            knownActions = actionsForClip.knownActions

            action._byClipCacheIndex = len(knownActions)
            knownActions.append( action )

        action._cacheIndex = len(actions)
        actions.append( action )

        actionsForClip.actionByRoot[ rootUuid ] = action

    def _removeInactiveAction(self, action ):
        actions = self._actions
        lastInactiveAction = actions[ len(actions) - 1 ]
        cacheIndex = action._cacheIndex

        lastInactiveAction._cacheIndex = cacheIndex
        actions[ cacheIndex ] = lastInactiveAction
        actions.pop()

        action._cacheIndex = None

        clipUuid = action._clip.uuid
        actionsByClip = self._actionsByClip
        actionsForClip = actionsByClip[ clipUuid ]
        knownActionsForClip = actionsForClip.knownActions

        lastKnownAction = knownActionsForClip[ knownActionsForClip.length - 1 ]

        byClipCacheIndex = action._byClipCacheIndex

        lastKnownAction._byClipCacheIndex = byClipCacheIndex
        knownActionsForClip[ byClipCacheIndex ] = lastKnownAction
        knownActionsForClip.pop()

        action._byClipCacheIndex = None

        actionByRoot = actionsForClip.actionByRoot
        rootUuid = ( action._localRoot or self._root ).uuid

        del actionByRoot[ rootUuid ]

        if len(knownActionsForClip) == 0:
            del actionsByClip[ clipUuid ]

        self._removeInactiveBindingsForAction( action )

    def _removeInactiveBindingsForAction(self, action ):
        bindings = action._propertyBindings
        for i in range(len(bindings)):
            binding = bindings[ i ]

            binding.referenceCount -= 1
            if binding.referenceCount == 0:
                self._removeInactiveBinding( binding )


    def _lendAction(self, action ):
        # [ active actions |  inactive actions  ]
        # [  active actions >| inactive actions ]
        #                 s        a
        #                  <-swap->
        #                 a        s

        actions = self._actions
        prevIndex = action._cacheIndex

        lastActiveIndex = self._nActiveActions
        self._nActiveActions += 1
        firstInactiveAction = actions[ lastActiveIndex ]

        action._cacheIndex = lastActiveIndex
        actions[ lastActiveIndex ] = action

        firstInactiveAction._cacheIndex = prevIndex
        actions[ prevIndex ] = firstInactiveAction

    def _takeBackAction(self, action ):
        # [  active actions  | inactive actions ]
        # [ active actions |< inactive actions  ]
        #        a        s
        #         <-swap->
        #        s        a

        actions = self._actions
        prevIndex = action._cacheIndex

        self._nActiveActions -= 1
        firstInactiveIndex = self._nActiveActions

        lastActiveAction = actions[ firstInactiveIndex ]

        action._cacheIndex = firstInactiveIndex
        actions[ firstInactiveIndex ] = action

        lastActiveAction._cacheIndex = prevIndex
        actions[ prevIndex ] = lastActiveAction

    # Memory management for PropertyMixer objects

    def _addInactiveBinding(self, binding, rootUuid, trackName ):
        bindingsByRoot = self._bindingsByRootAndName
        bindingByName = bindingsByRoot[ rootUuid ]

        bindings = self._bindings

        if bindingByName is None:
            bindingByName = {}
            bindingsByRoot[ rootUuid ] = bindingByName

        bindingByName[ trackName ] = binding

        binding._cacheIndex = len(bindings)
        bindings.append( binding )

    def _removeInactiveBinding(self, binding ):
        bindings = self._bindings
        propBinding = binding.binding
        rootUuid = propBinding.rootNode.uuid
        trackName = propBinding.path
        bindingsByRoot = self._bindingsByRootAndName
        bindingByName = bindingsByRoot[ rootUuid ]

        lastInactiveBinding = bindings[ len(bindings) - 1 ]
        cacheIndex = binding._cacheIndex

        lastInactiveBinding._cacheIndex = cacheIndex
        bindings[ cacheIndex ] = lastInactiveBinding
        bindings.pop()

        del bindingByName[ trackName ]

        #TODO FDE
        # suspect this means "if bindindyByName is empty, delete the root
        # remove_empty_map: {
        #    for (var _ in bindingByName )
        #        break remove_empty_map;
        #
        # delete  bindingsByRoot[rootUuid];
        #}
        if len(bindingByName) == 0:
            del  bindingsByRoot[rootUuid]

    def _lendBinding(self, binding ):
        bindings = self._bindings
        prevIndex = binding._cacheIndex

        lastActiveIndex = self._nActiveBindings
        self._nActiveBindings += 1
        firstInactiveBinding = bindings[ lastActiveIndex ]

        binding._cacheIndex = lastActiveIndex
        bindings[ lastActiveIndex ] = binding

        firstInactiveBinding._cacheIndex = prevIndex
        bindings[ prevIndex ] = firstInactiveBinding

    def _takeBackBinding(self, binding ):
        bindings = self._bindings
        prevIndex = binding._cacheIndex

        self._nActiveBindings -= 1
        firstInactiveIndex = self._nActiveBindings

        lastActiveBinding = bindings[ firstInactiveIndex ]

        binding._cacheIndex = firstInactiveIndex
        bindings[ firstInactiveIndex ] = binding

        lastActiveBinding._cacheIndex = prevIndex
        bindings[ prevIndex ] = lastActiveBinding

    # Memory management of Interpolants for weight and time scale

    def _lendControlInterpolant(self):
        interpolants = self._controlInterpolants
        self._nActiveControlInterpolants += 1
        lastActiveIndex = self._nActiveControlInterpolants
        if len(interpolants) <= lastActiveIndex:
            interpolant = LinearInterpolant(
                Float32Array( 2 ), Float32Array( 2 ),
                1, self._controlInterpolantsResultBuffer )

            interpolant.__cacheIndex = lastActiveIndex
            interpolants.append(interpolant)
        else:
            interpolant = interpolants[lastActiveIndex]

        return interpolant

    def _takeBackControlInterpolant(self, interpolant ):
        interpolants = self._controlInterpolants
        prevIndex = interpolant.__cacheIndex

        self._nActiveControlInterpolants -= 1
        firstInactiveIndex = self._nActiveControlInterpolants

        lastActiveInterpolant = interpolants[ firstInactiveIndex ]

        interpolant.__cacheIndex = firstInactiveIndex
        interpolants[ firstInactiveIndex ] = interpolant

        lastActiveInterpolant.__cacheIndex = prevIndex
        if len(interpolants) <= prevIndex:
            interpolants.append(lastActiveInterpolant)
        else:
            interpolants[ prevIndex ] = lastActiveInterpolant

    # return an action for a clip optionally using a custom root target
    # object (this method allocates a lot of dynamic memory in case a
    # previously unknown clip/root combination is specified)
    def clipAction(self, clip, optionalRoot=None ):
        root = optionalRoot or self._root
        rootUuid = root.uuid

        clipObject = AnimationClip.findByName( root, clip ) if isinstance(clip, str) else clip

        clipUuid = clipObject.uuid if clipObject is not None else clip

        prototypeAction = None

        if clipUuid in self._actionsByClip:
            actionsForClip = self._actionsByClip[clipUuid]

            if rootUuid in actionsForClip.actionByRoot:
                return actionsForClip.actionByRoot[rootUuid]

            # we know the clip, so we don't have to parse all
            # the bindings again but can just copy
            prototypeAction = actionsForClip.knownActions[ 0 ]

            # also, take the clip from the prototype action
            if clipObject is None:
                clipObject = prototypeAction._clip

        # clip must be known when specified via string
        if clipObject is None:
            return None

        # allocate all resources required to run it
        newAction = AnimationAction( self, clipObject, optionalRoot )

        self._bindAction( newAction, prototypeAction )

        # and make the action known to the memory manager
        self._addInactiveAction( newAction, clipUuid, rootUuid )

        return newAction

    # get an existing action
    def existingAction(self, clip, optionalRoot ):
        root = optionalRoot or self._root
        rootUuid = root.uuid

        clipObject = AnimationClip.findByName( root, clip ) if isinstance(clip, str) else clip

        clipUuid = clipObject.uuid if clipObject is not None else clip

        actionsForClip = self._actionsByClip[ clipUuid ]

        if actionsForClip is not None:
            return actionsForClip.actionByRoot[ rootUuid ] or None

        return None

    # deactivates all previously scheduled actions
    def stopAllAction(self):
        actions = self._actions
        nActions = self._nActiveActions
        bindings = self._bindings
        nBindings = self._nActiveBindings

        self._nActiveActions = 0
        self._nActiveBindings = 0

        for i in range(nActions):
            actions[ i ].reset()

        for i in range(nBindings):
            bindings[ i ].useCount = 0

        return self

    # advance the time and update apply the animation
    def update(self, deltaTime ):
        deltaTime *= self.timeScale

        actions = self._actions
        nActions = self._nActiveActions

        self.time += deltaTime
        time = self.time
        timeDirection = np.sign(deltaTime)

        self._accuIndex ^= 1
        accuIndex = self._accuIndex

        # run active actions

        for i in range(nActions):
            action = actions[i]
            action._update( time, deltaTime, timeDirection, accuIndex )

        # update scene graph
        for b in self._bindings:
            b.apply( accuIndex )

        return self

    # return this mixer's root target object
    def getRoot(self):
        return self._root

    # free all resources specific to a particular clip
    def uncacheClip(self, clip ):
        actions = self._actions
        clipUuid = clip.uuid
        actionsByClip = self._actionsByClip
        actionsForClip = actionsByClip[ clipUuid ]

        if actionsForClip is not None:
            # note: just calling _removeInactiveAction would mess up the
            # iteration state and also require updating the state we can
            # just throw away

            actionsToRemove = actionsForClip.knownActions

            for i in range(len(actionsToRemove)):
                action = actionsToRemove[ i ]

                self._deactivateAction( action )

                cacheIndex = action._cacheIndex
                lastInactiveAction = actions[ len(actions) - 1 ]

                action._cacheIndex = None
                action._byClipCacheIndex = None

                lastInactiveAction._cacheIndex = cacheIndex
                actions[ cacheIndex ] = lastInactiveAction
                actions.pop()

                self._removeInactiveBindingsForAction( action )

            del actionsByClip[ clipUuid ]

    # free all resources specific to a particular root target object
    def uncacheRoot(self, root ):
        rootUuid = root.uuid
        actionsByClip = self._actionsByClip

        for clipUuid in actionsByClip:
            actionByRoot = actionsByClip[ clipUuid ].actionByRoot
            action = actionByRoot[ rootUuid ]

            if action is not None:
                self._deactivateAction( action )
                self._removeInactiveAction( action )

        bindingsByRoot = self._bindingsByRootAndName
        bindingByName = bindingsByRoot[ rootUuid ]

        if bindingByName is not None:
            for trackName in bindingByName:
                binding = bindingByName[ trackName ]
                binding.restoreOriginalState()
                self._removeInactiveBinding( binding )

    # remove a targeted clip from the cache
    def uncacheAction(self, clip, optionalRoot ):
        action = self.existingAction( clip, optionalRoot )

        if action is not None:
            self._deactivateAction( action )
            self._removeInactiveAction( action )
