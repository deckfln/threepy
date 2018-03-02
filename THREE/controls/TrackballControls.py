"""
/**
 * @author Eberhard Graether / http:# //egraether.com/
 * @author Mark Lundin     / http:# //mark-lundin.com
 * @author Simone Manini / http:# //daron1337.github.io
 * @author Luca Antiga     / http:# //lantiga.github.io
 */
"""
import math
import THREE.Vector3
from THREE.pyOpenGL.EventManager import *


class TrackballControls(EventManager):
    _STATE_NONE = -1
    _STATE_ROTATE = 0
    _STATE_ZOOM = 1
    _STATE_PAN = 2
    _STATE_TOUCH_ROTATE = 3
    _STATE_TOUCH_ZOOM_PAN = 4

    def __init__(self, object, document):
        super().__init__()

        self.object = object
        self.domElement = document

        class _screen:
            def __init__(self):
                self.left = 0
                self.top = 0
                self.width = 0
                self.height = 0

        # // API

        self.enabled = True

        self.screen = _screen()

        self.rotateSpeed = 1.0
        self.zoomSpeed = 1.2
        self.panSpeed = 0.3

        self.noRotate = False
        self.noZoom = False
        self.noPan = False

        self.staticMoving = False
        self.dynamicDampingFactor = 0.2

        self.minDistance = 0
        self.maxDistance = float("+Inf")

        self.keys = [ 65,  # /*A*/,
                      83,  # /*S*/,
                      68   # /*D*/
                      ]

        # // internals

        self.target = THREE.Vector3()

        self.EPS = 0.000001

        self.lastPosition = THREE.Vector3()

        self._state = self._STATE_NONE
        self._prevState = self._STATE_NONE

        self._eye = THREE.Vector3()

        self._movePrev = THREE.Vector2()
        self._moveCurr = THREE.Vector2()

        self._lastAxis = THREE.Vector3()
        self._lastAngle = 0

        self._zoomStart = THREE.Vector2()
        self._zoomEnd = THREE.Vector2()

        self._touchZoomDistanceStart = 0
        self._touchZoomDistanceEnd = 0

        self._panStart = THREE.Vector2()
        self._panEnd = THREE.Vector2()

        # // for reset

        self.target0 = self.target.clone()
        self.position0 = self.object.position.clone()
        self.up0 = self.object.up.clone()

        # // events

        self.changeEvent = { 'type': 'change' }
        self.startEvent = { 'type': 'start' }
        self.endEvent = { 'type': 'end' }

        # // listeners

        def keydown(event, params):
            if not self.enabled:
                return

            self.domElement.removeEventListener('keydown', keydown)

            self._prevState = self._state

            if self._state != self._STATE_NONE:
                return

            elif event.keyCode == self.keys[self._STATE_ROTATE] and not self.noRotate:
                self._state = self._STATE_ROTATE

            elif event.keyCode == self.keys[self._STATE_ZOOM] and not self.noZoom:
                self._state = self._STATE_ZOOM

            elif event.keyCode == self.keys[self._STATE_PAN] and not self.noPan:
                self._state = self._STATE_PAN

        def keyup(event, params):
            if not self.enabled:
                return

            self._state = self._prevState

            self.domElement.addEventListener('keydown', keydown, False)

        def mousedown(event, params):
            if not self.enabled:
                return

            event.preventDefault()
            event.stopPropagation()

            if self._state == self._STATE_NONE:
                self._state = event.button

            if self._state == self._STATE_ROTATE and not self.noRotate:
                self._moveCurr.copy(self.getMouseOnCircle(event.pageX, event.pageY))
                self._movePrev.copy(self._moveCurr)

            elif self._state == self._STATE_ZOOM and not self.noZoom:
                self._zoomStart.copy(self.getMouseOnScreen(event.pageX, event.pageY))
                self._zoomEnd.copy(self._zoomStart)

            elif self._state == self._STATE_PAN and not self.noPan:
                self._panStart.copy(self.getMouseOnScreen(event.pageX, event.pageY))
                self._panEnd.copy(self._panStart)

            self.domElement.addEventListener('mousemove', mousemove, False)
            self.domElement.addEventListener('mouseup', mouseup, False)

            self.dispatchEvent(self.startEvent)

        def mousemove(event, params):
            if not self.enabled:
                return

            event.preventDefault()
            event.stopPropagation()

            if self._state == self._STATE_ROTATE and not self.noRotate:
                self._movePrev.copy(self._moveCurr)
                self._moveCurr.copy(self.getMouseOnCircle(event.pageX, event.pageY))

            elif self._state == self._STATE_ZOOM and not self.noZoom:
                self._zoomEnd.copy(self.getMouseOnScreen(event.pageX, event.pageY))

            elif self._state == self._STATE_PAN and not self.noPan:
                self._panEnd.copy(self.getMouseOnScreen(event.pageX, event.pageY))

        def mouseup(event, params):
            if not self.enabled:
                return

            event.preventDefault()
            event.stopPropagation()

            self._state = self._STATE_NONE

            document.removeEventListener('mousemove', mousemove)
            document.removeEventListener('mouseup', mouseup)
            self.dispatchEvent(self.endEvent)

        def mousewheel(event, params):
            if not self.enabled:
                return

            event.preventDefault()
            event.stopPropagation()

            if event.deltaMode == 2:
                # // Zoom in pages
                self._zoomStart.y -= event.deltaY * 0.025

            elif event.deltaMode == 1:
                # // Zoom in lines
                self._zoomStart.y -= event.deltaY * 0.01
            else:
                # // undefined, 0, assume pixels
                self._zoomStart.y -= event.deltaY * 0.00025

            self.dispatchEvent(self.startEvent)
            self.dispatchEvent(self.endEvent)

        def touchstart(event, params):
            if not self.enabled:
                return

            if event.touches.length == 1:
                self._state = self._STATE_TOUCH_ROTATE
                self._moveCurr.copy(self.getMouseOnCircle(event.touches[0].pageX, event.touches[0].pageY))
                self._movePrev.copy(self._moveCurr)
            else:  # // 2 or more
                self._state = self._STATE_TOUCH_ZOOM_PAN
                dx = event.touches[0].pageX - event.touches[1].pageX
                dy = event.touches[0].pageY - event.touches[1].pageY
                self._touchZoomDistanceEnd = self._touchZoomDistanceStart = math.sqrt(dx * dx + dy * dy)

                x = (event.touches[0].pageX + event.touches[1].pageX) / 2
                y = (event.touches[0].pageY + event.touches[1].pageY) / 2
                self._panStart.copy(self.getMouseOnScreen(x, y))
                self._panEnd.copy(self._panStart)

            self.dispatchEvent(self.startEvent)

        def touchmove(event, params):
            if not self.enabled:
                return

            event.preventDefault()
            event.stopPropagation()

            if event.touches.length == 1:
                self._movePrev.copy(self._moveCurr)
                self._moveCurr.copy(self.getMouseOnCircle(event.touches[0].pageX, event.touches[0].pageY))
            else:  # // 2 or more
                dx = event.touches[0].pageX - event.touches[1].pageX
                dy = event.touches[0].pageY - event.touches[1].pageY
                self._touchZoomDistanceEnd = math.sqrt(dx * dx + dy * dy)

                x = (event.touches[0].pageX + event.touches[1].pageX) / 2
                y = (event.touches[0].pageY + event.touches[1].pageY) / 2
                self._panEnd.copy(self.getMouseOnScreen(x, y))

        def touchend(event, params):
            if not self.enabled:
                return

            if event.touches.length == 0:
                self._state = self._STATE_NONE
            elif event.touches.length == 1:
                self._state = self._STATE_TOUCH_ROTATE
                self._moveCurr.copy(self.getMouseOnCircle(event.touches[0].pageX, event.touches[0].pageY))
                self._movePrev.copy(self._moveCurr)

            self.dispatchEvent(self.endEvent)

        def contextmenu(event, params):
            if not self.enabled:
                return

            event.preventDefault()

        self.domElement.addEventListener( 'contextmenu', contextmenu, False )
        self.domElement.addEventListener( 'mousedown', mousedown, False )
        self.domElement.addEventListener( 'wheel', mousewheel, False )

        self.domElement.addEventListener( 'touchstart', touchstart, False )
        self.domElement.addEventListener( 'touchend', touchend, False )
        self.domElement.addEventListener( 'touchmove', touchmove, False )

        self.domElement.addEventListener( 'keydown', keydown, False )
        self.domElement.addEventListener( 'keyup', keyup, False )

        self.screen.width = self.domElement.clientWidth
        self.screen.height = self.domElement.clientHeight

        # // force an update at start
        self.update()

    # // methods

    def handleResize(self, width, height):
        self.screen.left = 0
        self.screen.top = 0
        self.screen.width = width
        self.screen.height = height

    def getMouseOnScreen(self, pageX, pageY):
        vector = THREE.Vector2()

        vector.set(
            ( pageX - self.screen.left ) / self.screen.width,
            ( pageY - self.screen.top ) / self.screen.height
        )

        return vector

    def getMouseOnCircle(self, pageX, pageY):
        vector = THREE.Vector2()

        vector.set(
            ( ( pageX - self.screen.width * 0.5 - self.screen.left ) / ( self.screen.width * 0.5 ) ),
            ( ( self.screen.height + 2 * ( self.screen.top - pageY ) ) / self.screen.width ) # // screen.width intentional
        )

        return vector

    def rotateCamera(self):
        axis = THREE.Vector3()
        quaternion = THREE.Quaternion()
        eyeDirection = THREE.Vector3()
        objectUpDirection = THREE.Vector3()
        objectSidewaysDirection = THREE.Vector3()
        moveDirection = THREE.Vector3()

        moveDirection.set( self._moveCurr.x - self._movePrev.x, self._moveCurr.y - self._movePrev.y, 0 )
        angle = moveDirection.length()

        if angle:
            self._eye.copy( self.object.position ).sub( self.target )

            eyeDirection.copy( self._eye ).normalize()
            objectUpDirection.copy( self.object.up ).normalize()
            objectSidewaysDirection.crossVectors( objectUpDirection, eyeDirection ).normalize()

            objectUpDirection.setLength( self._moveCurr.y - self._movePrev.y )
            objectSidewaysDirection.setLength( self._moveCurr.x - self._movePrev.x )

            moveDirection.copy( objectUpDirection.add( objectSidewaysDirection ) )

            axis.crossVectors( moveDirection, self._eye ).normalize()

            angle *= self.rotateSpeed
            quaternion.setFromAxisAngle( axis, angle )

            self._eye.applyQuaternion( quaternion )
            self.object.up.applyQuaternion( quaternion )

            self._lastAxis.copy( axis )
            self._lastAngle = angle
        elif not self.staticMoving and self._lastAngle:
            self._lastAngle *= math.sqrt( 1.0 - self.dynamicDampingFactor )
            self._eye.copy( self.object.position ).sub( self.target )
            quaternion.setFromAxisAngle( self._lastAxis, self._lastAngle )
            self._eye.applyQuaternion( quaternion )
            self.object.up.applyQuaternion( quaternion )

        self._movePrev.copy( self._moveCurr )

    def zoomCamera(self):
        if self._state == self._STATE_TOUCH_ZOOM_PAN:
            factor = self._touchZoomDistanceStart / self._touchZoomDistanceEnd
            self._touchZoomDistanceStart = self._touchZoomDistanceEnd
            self._eye.multiplyScalar( factor )
        else:
            factor = 1.0 + ( self._zoomEnd.y - self._zoomStart.y ) * self.zoomSpeed

            if factor != 1.0 and factor > 0.0:
                self._eye.multiplyScalar( factor )

            if self.staticMoving:
                self._zoomStart.copy( self._zoomEnd )
            else:
                self._zoomStart.y += ( self._zoomEnd.y - self._zoomStart.y ) * self.dynamicDampingFactor

    def panCamera(self):
        mouseChange = THREE.Vector2()
        objectUp = THREE.Vector3()
        pan = THREE.Vector3()

        mouseChange.copy( self._panEnd ).sub( self._panStart )

        if mouseChange.lengthSq():
                mouseChange.multiplyScalar( self._eye.length() * self.panSpeed )

        pan.copy( self._eye ).cross( self.object.up ).setLength( mouseChange.x )
        pan.add( objectUp.copy( self.object.up ).setLength( mouseChange.y ) )

        self.object.position.add( pan )
        self.target.add( pan )

        if self.staticMoving:
            self._panStart.copy( self._panEnd )
        else:
            self._panStart.add( mouseChange.subVectors( self._panEnd, self._panStart ).multiplyScalar( self.dynamicDampingFactor ) )

    def checkDistances(self):
        if not self.noZoom or not self.noPan:
            if self._eye.lengthSq() > self.maxDistance * self.maxDistance:
                self.object.position.addVectors( self.target, self._eye.setLength( self.maxDistance ) )
                self._zoomStart.copy( self._zoomEnd )

            if self._eye.lengthSq() < self.minDistance * self.minDistance:
                self.object.position.addVectors( self.target, self._eye.setLength( self.minDistance ) )
                self._zoomStart.copy( self._zoomEnd )

    def update(self, timer=None):
        # TODO FDE : some examples are calling it with a timer, but the javascrip code has no such variable
        self._eye.subVectors( self.object.position, self.target )

        if not self.noRotate:
            self.rotateCamera()

        if not self.noZoom:
            self.zoomCamera()

        if not self.noPan:
            self.panCamera()

        self.object.position.addVectors( self.target, self._eye )

        self.checkDistances()

        self.object.lookAt( self.target )

        if self.lastPosition.distanceToSquared( self.object.position ) > self.EPS:
            self.dispatchEvent( self.changeEvent )
            self.lastPosition.copy( self.object.position )

    def reset(self):
        self._state = self._STATE_NONE
        self._prevState = self._STATE_NONE

        self.target.copy( self.target0 )
        self.object.position.copy( self.position0 )
        self.object.up.copy( self.up0 )

        self._eye.subVectors( self.object.position, self.target )

        self.object.lookAt( self.target )

        self.dispatchEvent( self.changeEvent )

        self.lastPosition.copy( self.object.position )

    def dispose(self):
        for event in self.events.keys():
            self.domElement.removeEventListener(event, self.events[event])
