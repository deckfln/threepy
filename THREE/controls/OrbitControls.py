"""
/**
 * @author qiao / https:# //github.com/qiao
 * @author mrdoob / http:# //mrdoob.com
 * @author alteredq / http:# //alteredqualia.com/
 * @author WestLangley / http:# //github.com/WestLangley
 * @author erich666 / http:# //erichaines.com
 */
"""

"""
# // This set of controls performs orbiting, dollying (zooming), and panning.
# // Unlike TrackballControls, it maintains the "up" direction object.up (+Y by default).
# //
# //    Orbit - left mouse / touch: one finger move
# //    Zoom - middle mouse, or mousewheel / touch: two finger spread or squish
# //    Pan - right mouse, or arrow keys / touch: three finger swipe
"""
from THREE.pyOpenGL.EventManager import *
from THREE.math.Vector3 import *


class OrbitControls(EventManager):
    _STATE_NONE = -1
    _STATE_ROTATE = 0
    _STATE_DOLLY = 1
    _STATE_PAN = 2
    _STATE_TOUCH_ROTATE = 3
    _STATE_TOUCH_DOLLY = 4
    _STATE_TOUCH_PAN = 5

    def __init__(self, object, domElement ):
        super().__init__()
        self.object = object

        self.domElement = domElement

        # // Set to False to disable self control
        self.enabled = True

        # // "target" sets the location of focus, where the object orbits around
        self.target = THREE.Vector3()

        # // How far you can dolly in and out ( PerspectiveCamera only )
        self.minDistance = 0
        self.maxDistance = float("+Inf")

        # // How far you can zoom in and out ( OrthographicCamera only )
        self.minZoom = 0
        self.maxZoom = float("+Inf")

        # // How far you can orbit vertically, upper and lower limits.
        # // Range is 0 to math.pi radians.
        self.minPolarAngle = 0     # // radians
        self.maxPolarAngle = math.pi     # // radians

        # // How far you can orbit horizontally, upper and lower limits.
        # // If set, must be a sub-interval of the interval [ - math.pi, math.pi ].
        self.minAzimuthAngle = - float("+Inf")     # // radians
        self.maxAzimuthAngle = float("+Inf")     # // radians

        # // Set to True to enable damping (inertia)
        # // If damping is enabled, you must call controls.update() in your animation loop
        self.enableDamping = False
        self.dampingFactor = 0.25

        # // This option actually enables dollying in and out; left as "zoom" for backwards compatibility.
        # // Set to False to disable zooming
        self.enableZoom = True
        self.zoomSpeed = 1.0

        # // Set to False to disable rotating
        self.enableRotate = True
        self.rotateSpeed = 1.0

        # // Set to False to disable panning
        self.enablePan = True
        self.keyPanSpeed = 7.0        # // pixels moved per arrow key push

        # // Set to True to automatically rotate around the target
        # // If auto-rotate is enabled, you must call controls.update() in your animation loop
        self.autoRotate = False
        self.autoRotateSpeed = 2.0     # // 30 seconds per round when fps is 60

        # // Set to False to disable use of the keys
        self.enableKeys = True

        # // The four arrow keys
        self.keys = { 'LEFT': 37, 'UP': 38, 'RIGHT': 39, 'BOTTOM': 40 }

        # // Mouse buttons
        self.mouseButtons = { 'ORBIT': THREE.MOUSE['LEFT'], 'ZOOM': THREE.MOUSE['MIDDLE'], 'PAN': THREE.MOUSE['RIGHT'] }

        # // for reset
        self.target0 = self.target.clone()
        self.position0 = self.object.position.clone()
        self.zoom0 = self.object.zoom

        # //
        # // internals
        # //
        self.changeEvent = { 'type': 'change' }
        self.startEvent = { 'type': 'start' }
        self.endEvent = { 'type': 'end' }

        self.state = self._STATE_NONE

        self.EPS = 0.000001

        # // current position in self.spherical coordinates
        self.spherical = THREE.Spherical()
        self.sphericalDelta = THREE.Spherical()

        self.scale = 1
        self.panOffset = THREE.Vector3()
        self.zoomChanged = False

        self.rotateStart = THREE.Vector2()
        self.rotateEnd = THREE.Vector2()
        self.rotateDelta = THREE.Vector2()

        self.panStart = THREE.Vector2()
        self.panEnd = THREE.Vector2()
        self.panDelta = THREE.Vector2()

        self.dollyStart = THREE.Vector2()
        self.dollyEnd = THREE.Vector2()
        self.dollyDelta = THREE.Vector2()

        # //
        # //
        # // event handlers - FSM: listen for events and reset self.state
        # //

        def onMouseDown(event, params):
            if self.enabled == False:
                return

            event.preventDefault()

            if event.button == self.mouseButtons['ORBIT']:
                if self.enableRotate == False:
                    return

                self.handleMouseDownRotate(event)
                self.state = self._STATE_ROTATE

            elif event.button == self.mouseButtons['ZOOM']:
                if self.enableZoom == False:
                    return

                self.handleMouseDownDolly(event)

                self.state = self._STATE_DOLLY

            elif event.button == self.mouseButtons['PAN']:
                if self.enablePan == False:
                    return

                self.handleMouseDownPan(event)

                self.state = self._STATE_PAN

            if self.state != self._STATE_NONE:
                self.domElement.addEventListener('mousemove', onMouseMove, False)
                self.domElement.addEventListener('mouseup', onMouseUp, False)

                self.dispatchEvent(self.startEvent)

        def onMouseMove(event, params):
            if self.enabled == False:
                return

            event.preventDefault()

            if self.state == self._STATE_ROTATE:
                if self.enableRotate == False:
                    return
                self.handleMouseMoveRotate(event)
            elif self.state == self._STATE_DOLLY:
                if self.enableZoom == False:
                    return

                self.handleMouseMoveDolly(event)

            elif self.state == self._STATE_PAN:
                if self.enablePan == False:
                    return

                self.handleMouseMovePan(event)

        def onMouseUp(event, params):
            if self.enabled == False:
                return

            self.handleMouseUp(event)

            self.domElement.removeEventListener('mousemove', onMouseMove, False)
            self.domElement.removeEventListener('mouseup', onMouseUp, False)

            self.dispatchEvent(self.endEvent)

            self.state = self._STATE_NONE

        def onMouseWheel(event, params):
            if self.enabled == False or self.enableZoom == False or (
                    self.state != self._STATE_NONE and self.state != self._STATE_ROTATE):
                return

            event.preventDefault()
            event.stopPropagation()

            self.handleMouseWheel(event)

            self.dispatchEvent(self.startEvent)   # // not sure why these are here...
            self.dispatchEvent(self.endEvent)

        def onKeyDown(event, params):
            if self.enabled == False or self.enableKeys == False or self.enablePan == False:
                return

            self.handleKeyDown(event)

        def onTouchStart(event, params):
            if self.enabled == False:
                return

            if event.touches.length == 1:  # // one-fingered touch: rotate
                if self.enableRotate == False:
                    return

                self.handleTouchStartRotate(event)

                self.state = self._STATE_TOUCH_ROTATE

            elif event.touches.length == 2:  # // two-fingered touch: dolly
                if self.enableZoom == False:
                    return

                self.handleTouchStartDolly(event)

                self.state = self._STATE_TOUCH_DOLLY

            elif event.touches.length == 3:  # // three-fingered touch: pan
                if self.enablePan == False:
                    return

                self.handleTouchStartPan(event)

                self.state = self._STATE_TOUCH_PAN

            else:
                self.state = self._STATE_NONE

            if self.state != self._STATE_NONE:
                self.dispatchEvent(self.startEvent)

        def onTouchMove(event, params):
            if self.enabled == False:
                return

            event.preventDefault()
            event.stopPropagation()

            if event.touches.length == 1:  # // one-fingered touch: rotate
                if self.enableRotate == False:
                    return
                if self.state != self._STATE_TOUCH_ROTATE:
                    return  # // is self needed?...

                self.handleTouchMoveRotate(event)
            elif event.touches.length == 2:  # // two-fingered touch: dolly
                if self.enableZoom == False:
                    return
                if self.state != self._STATE_TOUCH_DOLLY:
                    return  # // is self needed?...

                self.handleTouchMoveDolly(event)

            elif event.touches.length == 3:  # // three-fingered touch: pan
                if self.enablePan == False:
                    return
                if self.state != self._STATE_TOUCH_PAN:
                    return  # // is self needed?...

                self.handleTouchMovePan(event)

            else:
                self.state = self._STATE_NONE

        def onTouchEnd(event, params):
            if self.enabled == False:
                return

            self.handleTouchEnd(event)

            self.dispatchEvent(self.endEvent)

            self.state = self._STATE_NONE

        def onContextMenu(event, params):
            if self.enabled == False:
                return

            event.preventDefault()


        self.events = {
            'contextmenu': onContextMenu,

            'mousedown': onMouseDown,
            'wheel': onMouseWheel,

            'touchstart': onTouchStart,
            'touchend': onTouchEnd,
            'touchmove': onTouchMove,

            'keydown': onKeyDown
        }
        for event in self.events.keys():
            self.domElement.addEventListener(event, self.events[event])

        # // force an update at start

        self.update()
    
    # //
    # // public methods
    # //

    def getPolarAngle(self):
        return self.spherical.phi

    def getAzimuthalAngle(self):
        return self.spherical.theta

    def saveState(self):
        self.target0.copy( self.target )
        self.position0.copy( self.object.position )
        self.zoom0 = self.object.zoom

    def reset(self):

        self.target.copy( self.target0 )
        self.object.position.copy( self.position0 )
        self.object.zoom = self.zoom0

        self.object.updateProjectionMatrix()
        self.dispatchEvent( self.changeEvent )

        self.update()

        self.state = self._STATE_NONE

    # // self method is exposed, but perhaps it would be better if we can make it private...
    def update(self):
        offset = THREE.Vector3()

        # // so camera.up is the orbit axis
        quat = THREE.Quaternion().setFromUnitVectors( self.object.up, THREE.Vector3( 0, 1, 0 ) )
        quatInverse = quat.clone().inverse()

        lastPosition = THREE.Vector3()
        lastQuaternion = THREE.Quaternion()

        position = self.object.position

        offset.copy( position ).sub( self.target )

        # // rotate offset to "y-axis-is-up" space
        offset.applyQuaternion( quat )

        # // angle from z-axis around y-axis
        self.spherical.setFromVector3( offset )

        if self.autoRotate and self.state == self._STATE_NONE:
            self.rotateLeft( self.getAutoRotationAngle() )

        self.spherical.theta += self.sphericalDelta.theta
        self.spherical.phi += self.sphericalDelta.phi

        # // restrict theta to be between desired limits
        self.spherical.theta = max( self.minAzimuthAngle, min( self.maxAzimuthAngle, self.spherical.theta ) )

        # // restrict phi to be between desired limits
        self.spherical.phi = max( self.minPolarAngle, min( self.maxPolarAngle, self.spherical.phi ) )

        self.spherical.makeSafe()


        self.spherical.radius *= self.scale

        # // restrict radius to be between desired limits
        self.spherical.radius = max( self.minDistance, min( self.maxDistance, self.spherical.radius ) )

        # // move target to panned location
        self.target.add( self.panOffset )

        offset.setFromSpherical( self.spherical )

        # // rotate offset back to "camera-up-vector-is-up" space
        offset.applyQuaternion( quatInverse )

        position.copy( self.target ).add( offset )

        self.object.lookAt( self.target )

        if self.enableDamping:
            self.sphericalDelta.theta *= ( 1 - self.dampingFactor )
            self.sphericalDelta.phi *= ( 1 - self.dampingFactor )
        else:
            self.sphericalDelta.set( 0, 0, 0 )

        self.scale = 1
        self.panOffset.set( 0, 0, 0 )

        # // update condition is:
        # // min(camera displacement, camera rotation in radians)^2 > self.EPS
        # // using small-angle approximation cos(x/2) = 1 - x^2 / 8

        if self.zoomChanged or \
            lastPosition.distanceToSquared( self.object.position ) > self.EPS or \
            8 * ( 1 - lastQuaternion.dot( self.object.quaternion ) ) > self.EPS:

            self.dispatchEvent( self.changeEvent )

            lastPosition.copy( self.object.position )
            lastQuaternion.copy( self.object.quaternion )
            self.zoomChanged = False

            return True

        return False

    def dispose(self):
        for event in self.events.keys():
            self.domElement.removeEventListener(event, self.events[event])
        # //self.dispatchEvent( { type: 'dispose' } ); # // should self be added here?

    def getAutoRotationAngle(self):
        return 2 * math.pi / 60 / 60 * self.autoRotateSpeed

    def getZoomScale(self):
        return math.pow( 0.95, self.zoomSpeed )

    def rotateLeft(self, angle ):
        self.sphericalDelta.theta -= angle

    def rotateUp(self, angle ):
        self.sphericalDelta.phi -= angle

    def panLeft(self, distance, objectMatrix):
        v = THREE.Vector3()

        v.setFromMatrixColumn( objectMatrix, 0 )     # // get X column of objectMatrix
        v.multiplyScalar( - distance )

        self.panOffset.add( v )

    def panUp(self, distance, objectMatrix):
        v = THREE.Vector3()

        v.setFromMatrixColumn( objectMatrix, 1 )     # // get Y column of objectMatrix
        v.multiplyScalar( distance )

        self.panOffset.add( v )

    # // deltaX and deltaY are in pixels; right and down are positive
    def pan(self, deltaX, deltaY):
        offset = THREE.Vector3()

        element = self.domElement

        if self.object.isPerspectiveCamera:
            # // perspective
            position = self.object.position
            offset.copy( position ).sub( self.target )
            targetDistance = offset.length()

            # // half of the fov is center to top of screen
            targetDistance *= math.tan( ( self.object.fov / 2 ) * math.pi / 180.0 )

            # // we actually don't use screenWidth, since perspective camera is fixed to screen height
            self.panLeft( 2 * deltaX * targetDistance / element.clientHeight, self.object.matrix )
            self.panUp( 2 * deltaY * targetDistance / element.clientHeight, self.object.matrix )

        elif self.object.isOrthographicCamera:
            # // orthographic
            self.panLeft( deltaX * ( self.object.right - self.object.left ) / self.object.zoom / element.clientWidth, self.object.matrix )
            self.panUp( deltaY * ( self.object.top - self.object.bottom ) / self.object.zoom / element.clientHeight, self.object.matrix )

        else:
            # // camera neither orthographic nor perspective
            print( 'WARNING: OrbitControls.js encountered an unknown camera type - pan disabled.' )
            self.enablePan = False

    def dollyIn(self, dollyScale ):
        if self.object.isPerspectiveCamera:
            self.scale /= dollyScale

        elif self.object.isOrthographicCamera:
            self.object.zoom = max( self.minZoom, min( self.maxZoom, self.object.zoom * dollyScale ) )
            self.object.updateProjectionMatrix()
            self.zoomChanged = True

        else:
            print( 'WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled.' )
            self.enableZoom = False

    def dollyOut(self, dollyScale ):
        if self.object.isPerspectiveCamera:
            self.scale *= dollyScale

        elif self.object.isOrthographicCamera:
            self.object.zoom = max( self.minZoom, min( self.maxZoom, self.object.zoom / dollyScale ) )
            self.object.updateProjectionMatrix()
            self.zoomChanged = True

        else:
            print( 'WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled.' )
            self.enableZoom = False

    # //
    # // event callbacks - update the object self.state
    # //

    def handleMouseDownRotate(self, event ):
        # //console.log( 'handleMouseDownRotate' )
        self.rotateStart.set( event.clientX, event.clientY )

    def handleMouseDownDolly(self, event ):
        # //console.log( 'handleMouseDownDolly' )
        self.dollyStart.set( event.clientX, event.clientY )

    def handleMouseDownPan(self, event ):
        # //console.log( 'handleMouseDownPan' )
        self.panStart.set( event.clientX, event.clientY )

    def handleMouseMoveRotate(self, event ):
        # //console.log( 'handleMouseMoveRotate' )
        self.rotateEnd.set( event.clientX, event.clientY )
        self.rotateDelta.subVectors( self.rotateEnd, self.rotateStart )

        element = self.domElement

        # // rotating across whole screen goes 360 degrees around
        self.rotateLeft( 2 * math.pi * self.rotateDelta.x / element.clientWidth * self.rotateSpeed )

        # // rotating up and down along whole screen attempts to go 360, but limited to 180
        self.rotateUp( 2 * math.pi * self.rotateDelta.y / element.clientHeight * self.rotateSpeed )

        self.rotateStart.copy( self.rotateEnd )

        self.update()

    def handleMouseMoveDolly(self, event ):
        # //console.log( 'handleMouseMoveDolly' )
        self.dollyEnd.set( event.clientX, event.clientY )

        self.dollyDelta.subVectors( self.dollyEnd, self.dollyStart )

        if self.dollyDelta.y > 0:
            self.dollyIn( self.getZoomScale() )

        elif self.dollyDelta.y < 0:
            self.dollyOut( self.getZoomScale() )

        self.dollyStart.copy( self.dollyEnd )

        self.update()

    def handleMouseMovePan(self, event ):
        # //console.log( 'handleMouseMovePan' )

        self.panEnd.set( event.clientX, event.clientY )

        self.panDelta.subVectors( self.panEnd, self.panStart )

        self.pan( self.panDelta.x, self.panDelta.y )

        self.panStart.copy( self.panEnd )

        self.update()

    def handleMouseUp(self, event ):
        # // console.log( 'handleMouseUp' )
        return True

    def handleMouseWheel(self, event ):
        # // console.log( 'handleMouseWheel' )
        if event.deltaY < 0:
            self.dollyOut( self.getZoomScale() )

        elif event.deltaY > 0:
            self.dollyIn( self.getZoomScale() )

        self.update()

    def handleKeyDown(self, event ):
        # //console.log( 'handleKeyDown' )
        if event.keyCode == self.keys['UP']:
                self.pan( 0, self.keyPanSpeed )
                self.update()
        elif event.keyCode == self.keys['BOTTOM']:
                self.pan( 0, - self.keyPanSpeed )
                self.update()
        elif event.keyCode == self.keys['LEFT']:
                self.pan( self.keyPanSpeed, 0 )
                self.update()
        elif event.keyCode == self.keys['RIGHT']:
                self.pan( - self.keyPanSpeed, 0 )
                self.update()

    def handleTouchStartRotate(self, event ):
        # //console.log( 'handleTouchStartRotate' )
        self.rotateStart.set( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY )

    def handleTouchStartDolly(self, event ):
        # //console.log( 'handleTouchStartDolly' )
        dx = event.touches[ 0 ].pageX - event.touches[ 1 ].pageX
        dy = event.touches[ 0 ].pageY - event.touches[ 1 ].pageY

        distance = math.sqrt( dx * dx + dy * dy )

        self.dollyStart.set( 0, distance )

    def handleTouchStartPan(self, event ):
        # //console.log( 'handleTouchStartPan' )
        self.panStart.set( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY )

    def handleTouchMoveRotate(self, event ):
        # //console.log( 'handleTouchMoveRotate' )
        self.rotateEnd.set( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY )
        self.rotateDelta.subVectors( self.rotateEnd, self.rotateStart )

        element = self.domElement

        # // rotating across whole screen goes 360 degrees around
        self.rotateLeft( 2 * math.pi * self.rotateDelta.x / element.clientWidth * self.rotateSpeed )

        # // rotating up and down along whole screen attempts to go 360, but limited to 180
        self.rotateUp( 2 * math.pi * self.rotateDelta.y / element.clientHeight * self.rotateSpeed )

        self.rotateStart.copy( self.rotateEnd )

        self.update()

    def handleTouchMoveDolly(self, event ):
        # //console.log( 'handleTouchMoveDolly' )
        dx = event.touches[ 0 ].pageX - event.touches[ 1 ].pageX
        dy = event.touches[ 0 ].pageY - event.touches[ 1 ].pageY

        distance = math.sqrt( dx * dx + dy * dy )

        self.dollyEnd.set( 0, distance )

        self.dollyDelta.subVectors( self.dollyEnd, self.dollyStart )

        if self.dollyDelta.y > 0:
            self.dollyOut( self.getZoomScale() )

        elif self.dollyDelta.y < 0:
            self.dollyIn( self.getZoomScale() )

        self.dollyStart.copy( self.dollyEnd )

        self.update()

    def handleTouchMovePan(self, event ):
        # //console.log( 'handleTouchMovePan' )
        self.panEnd.set( event.touches[ 0 ].pageX, event.touches[ 0 ].pageY )

        self.panDelta.subVectors( self.panEnd, self.panStart )

        self.pan( self.panDelta.x, self.panDelta.y )

        self.panStart.copy( self.panEnd )

        self.update()

    def handleTouchEnd(self, event ):
        # //console.log( 'handleTouchEnd' )
        return True

    def getCenter(self):
        return self.target

    # // backward compatibility

    def noZoomGet(self):
        print( 'THREE.OrbitControls: .noZoom has been deprecated. Use .enableZoom instead.' )
        return not self.enableZoom

    def noZoomSet(self, value):
        print( 'THREE.OrbitControls: .noZoom has been deprecated. Use .enableZoom instead.' )
        self.enableZoom = not value

    center = property(getCenter)
    noZoom = property(noZoomGet, noZoomSet)

    def noRotateGet(self):
        print( 'THREE.OrbitControls: .noRotate has been deprecated. Use .enableRotate instead.' )
        return not self.enableRotate
    
    def noRotateSet(self, value):
        print( 'THREE.OrbitControls: .noRotate has been deprecated. Use .enableRotate instead.' )
        self.enableRotate = not value

    noRotate = property(noRotateGet, noRotateSet)

    def noPanGet(self):
        print( 'THREE.OrbitControls: .noPan has been deprecated. Use .enablePan instead.' )
        return not self.enablePan
        
    def noPanSet(self, value):
        print( 'THREE.OrbitControls: .noPan has been deprecated. Use .enablePan instead.' )
        self.enablePan = not value

    noPan = property(noPanGet, noPanSet)

    def noKeyGet(self):
        print( 'THREE.OrbitControls: .noKeys has been deprecated. Use .enableKeys instead.' )
        return not self.enableKeys
        
    def noKeySet(self, value):
        print( 'THREE.OrbitControls: .noKeys has been deprecated. Use .enableKeys instead.' )
        self.enableKeys = not value

    noKey = property(noKeyGet, noKeySet)
    
    def staticMovingGet(self):
        print( 'THREE.OrbitControls: .staticMoving has been deprecated. Use .enableDamping instead.' )
        return not self.enableDamping

    def staticMovingSet(self, value):
        print( 'THREE.OrbitControls: .staticMoving has been deprecated. Use .enableDamping instead.' )
        self.enableDamping = not value

    staticMoving = property(staticMovingGet, staticMovingSet)

    def dynamicDampingFactorGet(self):
        print( 'THREE.OrbitControls: .dynamicDampingFactor has been renamed. Use .dampingFactor instead.' )
        return self.dampingFactor
        
    def dynamicDampingFactorSet(self, value):
        print( 'THREE.OrbitControls: .dynamicDampingFactor has been renamed. Use .dampingFactor instead.' )
        self.dampingFactor = value

    dynamicDampingFactor = property(dynamicDampingFactorGet, dynamicDampingFactorSet)
