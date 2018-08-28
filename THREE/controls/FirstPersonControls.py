"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author paulirish / http://paulirish.com/
 */
"""
from THREE.pyOpenGL.EventManager import *
from THREE.math.Vector3 import *
import THREE._Math as _Math


class FirstPersonControls(EventManager):
    def __init__(self, object, container ):
        super().__init__()
        self.object = object
        self.target = Vector3( 0, 0, 0 )

        self.container = container

        self.enabled = True

        self.movementSpeed = 1.0
        self.lookSpeed = 0.005

        self.lookVertical = True
        self.autoForward = False

        self.activeLook = True

        self.heightSpeed = False
        self.heightCoef = 1.0
        self.heightMin = 0.0
        self.heightMax = 1.0

        self.constrainVertical = False
        self.verticalMin = 0
        self.verticalMax = math.pi

        self.autoSpeedFactor = 0.0

        self.mouseX = 0
        self.mouseY = 0

        self.lat = 0
        self.lon = 0
        self.phi = 0
        self.theta = 0

        self.moveForward = False
        self.moveBackward = False
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False

        self.mouseDragOn = False

        self.viewHalfX = 0
        self.viewHalfY = 0

        def onMouseDown(event, p):
            event.preventDefault()
            event.stopPropagation()

            if self.activeLook:
                if event.button == 0:
                    self.moveForward = True
                elif event.button == 2:
                    self.moveBackward = True

            self.mouseDragOn = True

        def onMouseUp(event, p):
            event.preventDefault()
            event.stopPropagation()

            if self.activeLook:
                if event.button == 0: 
                    self.moveForward = False
                elif event.button == 2:
                    self.moveBackward = False

            self.mouseDragOn = False

        def onMouseMove(event, p):
            self.mouseX = event.pageX - self.viewHalfX
            self.mouseY = event.pageY - self.viewHalfY

        def onKeyDown(event, p):
            # //event.preventDefault()
            if event.keyCode in (273, 87):   # up, >
                self.moveForward = True

            elif event.keyCode in (275, 65): # left, A
                self.moveLeft = True

            elif event.keyCode in (274, 83): # down, S
                self.moveBackward = True

            elif event.keyCode in (276, 68): # right, D
                self.moveRight = True

            elif event.keyCode == 82: # R
                self.moveUp = True

            elif event.keyCode == 70: # /*F*/
                self.moveDown = True

        def onKeyUp( event, p ):
            if event.keyCode in (273, 87):  # up, >
                self.moveForward = False

            elif event.keyCode in (275, 65):  # left, A
                self.moveLeft = False

            elif event.keyCode in (274, 83):  # down, S
                self.moveBackward = False

            elif event.keyCode in (276, 68):  # right, D
                self.moveRight = False

            elif event.keyCode == 82:  # R
                self.moveUp = False

            elif event.keyCode == 70:  # /*F*/
                self.moveDown = False

        def contextmenu(event ):
            event.preventDefault()
                
        self.container.addEventListener( 'contextmenu', contextmenu, False )
        self.container.addEventListener( 'mousemove', onMouseMove, False )
        self.container.addEventListener( 'mousedown', onMouseDown, False )
        self.container.addEventListener( 'mouseup', onMouseUp, False )

        self.container.addEventListener( 'keydown', onKeyDown, False )
        self.container.addEventListener( 'keyup', onKeyUp, False )

        self.handleResize(container.clientWidth, container.clientHeight)

    def handleResize(self, width, height):
        self.viewHalfX = width / 2
        self.viewHalfY = height / 2


    def update(self, delta ):
        if self.enabled == False:
            return

        if self.heightSpeed:
            y = _Math.clamp( self.object.position.y, self.heightMin, self.heightMax )
            heightDelta = y - self.heightMin

            self.autoSpeedFactor = delta * ( heightDelta * self.heightCoef )
        else:
            self.autoSpeedFactor = 0.0

        actualMoveSpeed = delta * self.movementSpeed

        if self.moveForward or ( self.autoForward and not self.moveBackward ):
            self.object.translateZ( - ( actualMoveSpeed + self.autoSpeedFactor ) )
        if self.moveBackward:
            self.object.translateZ( actualMoveSpeed )

        if self.moveLeft:
            self.object.translateX( - actualMoveSpeed )
        if self.moveRight:
            self.object.translateX( actualMoveSpeed )

        if self.moveUp:
            self.object.translateY( actualMoveSpeed )
        if self.moveDown:
            self.object.translateY( - actualMoveSpeed )

        actualLookSpeed = delta * self.lookSpeed

        if not self.activeLook:
            actualLookSpeed = 0

        verticalLookRatio = 1

        if self.constrainVertical:
            verticalLookRatio = math.pi / ( self.verticalMax - self.verticalMin )

        self.lon += self.mouseX * actualLookSpeed
        if self.lookVertical:
            self.lat -= self.mouseY * actualLookSpeed * verticalLookRatio

        self.lat = max( - 85, min( 85, self.lat ) )
        self.phi = _Math.degToRad( 90 - self.lat )

        self.theta = _Math.degToRad( self.lon )

        if self.constrainVertical:
            self.phi = _Math.mapLinear( self.phi, 0, math.pi, self.verticalMin, self.verticalMax )

        targetPosition = self.target
        position = self.object.position

        targetPosition.x = position.x + 100 * math.sin( self.phi ) * math.cos( self.theta )
        targetPosition.y = position.y + 100 * math.cos( self.phi )
        targetPosition.z = position.z + 100 * math.sin( self.phi ) * math.sin( self.theta )

        self.object.lookAt( targetPosition )

    def dispose(self):
        for event in self.events.keys():
            self.domElement.removeEventListener(event, self.events[event])
