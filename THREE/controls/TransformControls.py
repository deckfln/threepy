"""
* @author arodic / https:#github.com/arodic
"""
from THREE.pyOpenGL.EventManager import *
from THREE import *
from THREE.core.Object3D import *
from THREE.core.Raycaster import *
from THREE.cameras.PerspectiveCamera import *
from THREE.cameras.OrthographicCamera import *

_tempVector = Vector3()
_tempVector2 = Vector3()
_tempQuaternion = Quaternion()
_tempQuaternion2 = Quaternion()
_zeroVector = Vector3(0, 0, 0)
_lookAtMatrix = Matrix4()

_unit = {
    "X": Vector3(1, 0, 0),
    "Y": Vector3(0, 1, 0),
    "Z": Vector3(0, 0, 1)
}
_identityQuaternion = Quaternion()
_alignVector = Vector3()
_dirVector = Vector3()
_positionStart = Vector3()
_quaternionStart = Quaternion()
_scaleStart = Vector3()
_tempEuler = THREE.Euler()
_unitX = THREE.Vector3(1, 0, 0)
_unitY = THREE.Vector3(0, 1, 0)
_unitZ = THREE.Vector3(0, 0, 1)
_tempMatrix = THREE.Matrix4()


class TransformControls(Object3D, EventManager):
    isTransformControls = True
    
    def __init__(self, camera, domElement):
        Object3D.__init__(self)
        EventManager.__init__(self)

        self.visible = False

        self.gizmo = TransformControlsGizmo()
        self.add(self.gizmo)

        self.plane = TransformControlsPlane()
        self.add(self.plane)

        self.domElement = domElement

        # Define properties with getters/setter
        # Setting the defined property will automatically trigger change event
        # Defined properties are passed down to gizmo and plane

        self.camera = camera
        self.object = None
        self.axis = None
        self.mode = "translate"
        self.translationSnap = None
        self.rotationSnap = None
        self.space = "world"
        self.size = 1
        self.dragging = False

        self.changeEvent = {"type": "change"}
        self.mouseDownEvent = {"type": "mousedown", 'mode': None}
        self.mouseUpEvent = {"type": "mouseup", "mode": self.mode}
        self.objectChangeEvent = {"type": "objectChange"}

        # Reusable utility variables

        self.ray = Raycaster()

        self.pointStart = Vector3()
        self.pointEnd = Vector3()
        self.rotationAxis = Vector3()
        self.rotationAngle = 0

        self.cameraPosition = Vector3()
        self.cameraQuaternion = Quaternion()
        self.cameraScale = Vector3()

        self.parentPosition = Vector3()
        self.parentQuaternion = Quaternion()
        self.parentScale = Vector3()

        self.worldPositionStart = Vector3()
        self.worldQuaternionStart = Quaternion()
        self.worldScaleStart = Vector3()

        self.worldPosition = Vector3()
        self.worldQuaternion = Quaternion()
        self.worldScale = Vector3()

        self.eye = Vector3()
        self.debug = False

        # TODO: remove properties unused in plane and gizmo
        def onContext(event):
            """ mouse / touch event handlers"""
            event.preventDefault()

        def onPointerHover(event,param):
            # event.preventDefault()
            self.pointerHover(self.getPointer(event), event)

        def onPointerDown(event, param):
            event.preventDefault()
            event.stopPropagation()

            self.pointerHover(self.getPointer(event), event)
            self.pointerDown(self.getPointer(event), event)

        def onPointerMove(event, param):
            event.preventDefault()
            event.stopPropagation()
            self.pointerMove(self.getPointer(event))

        def onPointerUp(event, param):
            event.preventDefault()  # Prevent MouseEvent on mobile
            self.pointerUp(self.getPointer(event), event)

        domElement.addEventListener("mousedown", onPointerDown, False)
        domElement.addEventListener("touchstart",onPointerDown, False)
        domElement.addEventListener("mousemove", onPointerHover, False)
        domElement.addEventListener("touchmove", onPointerHover, False)
        domElement.addEventListener("mousemove", onPointerMove, False)
        domElement.addEventListener("touchmove", onPointerMove, False)
        domElement.addEventListener("mouseup", onPointerUp, False)
        domElement.addEventListener("mouseleave", onPointerUp, False)
        domElement.addEventListener("mouseout", onPointerUp, False)
        domElement.addEventListener("touchend", onPointerUp, False)
        domElement.addEventListener("touchcancel", onPointerUp, False)
        domElement.addEventListener("touchleave", onPointerUp, False)
        domElement.addEventListener("contextmenu", onContext, False)

    def dispose(self):
        self.domElement.removeEventListener("mousedown")
        self.domElement.removeEventListener("touchstart")
        self.domElement.removeEventListener("mousemove")
        self.domElement.removeEventListener("touchmove")
        self.domElement.removeEventListener("mousemove")
        self.domElement.removeEventListener("touchmove")
        self.domElement.removeEventListener("mouseup")
        self.domElement.removeEventListener("mouseleave")
        self.domElement.removeEventListener("mouseout")
        self.domElement.removeEventListener("touchend")
        self.domElement.removeEventListener("touchcancel")
        self.domElement.removeEventListener("touchleave")
        self.domElement.removeEventListener("contextmenu")

    def attach(self, object):
        """ Set current object """
        self.object = object
        self.visible = True

    def detach(self):
        """ Detatch from object """
        self.object = None
        self.visible = False
        self.axis = None

    def updateMatrixWorld(self, force=False, self_matrixWorld_is_updated=False):
        """ updateMatrixWorld  updates key transformation variables """

        if self.object is not None:
            self.object.updateMatrixWorld()
            self.object.parent.matrixWorld.decompose(self.parentPosition, self.parentQuaternion, self.parentScale)
            self.object.matrixWorld.decompose(self.worldPosition, self.worldQuaternion, self.worldScale)

        self.camera.updateMatrixWorld()
        self.camera.matrixWorld.decompose(self.cameraPosition, self.cameraQuaternion, self.cameraScale)

        if isinstance(self.camera, PerspectiveCamera):
            self.eye.copy(self.cameraPosition).sub(self.worldPosition).normalize()

        elif isinstance(self.camera, OrthographicCamera):
            self.eye.copy(self.cameraPosition).normalize()

        super().updateMatrixWorld(force, self_matrixWorld_is_updated)

    def pointerHover(self, pointer, event):
        if self.object is None or self.dragging:  #FIXME or (pointer.button != 0):
            return

        self.ray.setFromCamera(pointer, self.camera)
        intersects = []
        objs = self.gizmo.picker[self.mode].children
        self.ray.intersectObjects(objs, True, intersects)
        intersect = intersects[0] if len(intersects) > 0 else False

        if intersect:
            self.axis = intersect.object.name
        else:
            self.axis = None

    def pointerDown(self, pointer, event):
        if self.object is None or self.dragging == True or (pointer.button is not None and pointer.button != 0):
            return

        if (pointer.button == 0 or pointer.button is None) and self.axis is not None:
            self.ray.setFromCamera(pointer, self.camera)

            intersects = []
            self.ray.intersectObjects([self.plane], True, intersects)
            planeIntersect = intersects[0] if len(intersects) > 0 else False

            if planeIntersect:
                space = self.space

                if self.mode == 'scale':
                    space = 'local'
                elif self.axis == 'E' or  self.axis == 'XYZE' or  self.axis == 'XYZ':
                    space = 'world'

                if space == 'local' and self.mode == 'rotate':
                    snap = self.rotationSnap

                    if self.axis == 'X' and snap:
                        self.object.rotation.x = round(self.object.rotation.x / snap) * snap
                    if self.axis == 'Y' and snap:
                        self.object.rotation.y = round(self.object.rotation.y / snap) * snap
                    if self.axis == 'Z' and snap:
                        self.object.rotation.z = round(self.object.rotation.z / snap) * snap

                self.object.updateMatrixWorld()
                self.object.parent.updateMatrixWorld()

                _positionStart.copy(self.object.position)
                _quaternionStart.copy(self.object.quaternion)
                _scaleStart.copy(self.object.scale)

                self.object.matrixWorld.decompose(self.worldPositionStart, self.worldQuaternionStart, self.worldScaleStart)

                self.pointStart.copy(planeIntersect.point).sub(self.worldPositionStart)

                if space == 'local':
                    self.pointStart.applyQuaternion(self.worldQuaternionStart.clone().inverse())

            self.dragging = True
            event.mode = self.mode
            self.dispatchEvent(event)

    def pointerMove(self, pointer):
        global _tempVector
        global _tempVector2
        global _tempQuaternion
        global _quaternionStart

        axis = self.axis
        mode = self.mode
        object = self.object
        space = self.space

        if mode == 'scale':
            space = 'local'
        elif axis == 'E' or  axis == 'XYZE' or  axis == 'XYZ':
            space = 'world'

        if object is None or axis is None or not self.dragging or (pointer.button is not None and pointer.button != 0):
            return

        self.ray.setFromCamera(pointer, self.camera)

        intersects = []
        self.ray.intersectObjects([self.plane], True, intersects)
        planeIntersect = intersects[0] if len(intersects) > 0 else False

        if not planeIntersect:
            return

        self.pointEnd.copy(planeIntersect.point).sub(self.worldPositionStart)

        if space == 'local':
            self.pointEnd.applyQuaternion(self.worldQuaternionStart.clone().inverse())

        if mode == 'translate':
            if axis.find('X') == -1:
                self.pointEnd.x = self.pointStart.x
            if axis.find('Y') == -1:
                self.pointEnd.y = self.pointStart.y
            if axis.find('Z') == -1:
                self.pointEnd.z = self.pointStart.z

            # Apply translate

            if space == 'local':
                object.position.copy(self.pointEnd).sub(self.pointStart).applyQuaternion(_quaternionStart)
            else:
                object.position.copy(self.pointEnd).sub(self.pointStart)

            object.position.add(_positionStart)

            # Apply translation snap

            if self.translationSnap:
                if space == 'local':
                    object.position.applyQuaternion(_tempQuaternion.copy(_quaternionStart).inverse())

                    if axis.find('X') != -1:
                        object.position.x = round(object.position.x / self.translationSnap) * self.translationSnap

                    if axis.find('Y') != -1:
                        object.position.y = round(object.position.y / self.translationSnap) * self.translationSnap

                    if axis.find('Z') != -1:
                        object.position.z = round(object.position.z / self.translationSnap) * self.translationSnap

                    object.position.applyQuaternion(_quaternionStart)

                if space == 'world':
                    if object.parent:
                        object.position.add(_tempVector.setFromMatrixPosition(object.parent.matrixWorld))

                    if axis.find('X') != -1:
                        object.position.x = round(object.position.x / self.translationSnap) * self.translationSnap

                    if axis.find('Y') != -1:
                        object.position.y = round(object.position.y / self.translationSnap) * self.translationSnap

                    if axis.find('Z') != -1:
                        object.position.z = round(object.position.z / self.translationSnap) * self.translationSnap

                    if object.parent:
                        object.position.sub(_tempVector.setFromMatrixPosition(object.parent.matrixWorld))

        elif mode == 'scale':
            if axis.find('XYZ') != -1:
                d = self.pointEnd.length() / self.pointStart.length()

                if self.pointEnd.dot(self.pointStart) < 0:
                    d *= -1

                _tempVector.set(d, d, d)

            else:
                _tempVector.copy(self.pointEnd).divide(self.pointStart)

                if axis.find('X') == -1:
                    _tempVector.x = 1
                if axis.find('Y') == -1:
                    _tempVector.y = 1
                if axis.find('Z') == -1:
                    _tempVector.z = 1

            # Apply scale

            object.scale.copy(_scaleStart).multiply(_tempVector)

        elif mode == 'rotate':
            ROTATION_SPEED = 20 / self.worldPosition.distanceTo(_tempVector.setFromMatrixPosition(self.camera.matrixWorld))

            quaternion = self.worldQuaternion if self.space == "local" else _identityQuaternion

            if axis == 'E':
                _tempVector.copy(self.pointEnd).cross(self.pointStart)
                self.rotationAxis.copy(self.eye)
                rotationAngle = self.pointEnd.angleTo(self.pointStart) * (1 if _tempVector.dot(self.eye) < 0 else -1)

            elif axis == 'XYZE':
                _tempVector.copy(self.pointEnd).sub(self.pointStart).cross(self.eye).normalize()
                self.rotationAxis.copy(_tempVector)
                rotationAngle = self.pointEnd.sub(self.pointStart).dot(_tempVector.cross(self.eye)) * ROTATION_SPEED

            elif axis == 'X' or axis == 'Y' or axis == 'Z':
                unit = _unit[axis]

                _alignVector.copy(unit).applyQuaternion(quaternion)

                self.rotationAxis.copy(unit)

                _tempVector = unit.clone()
                _tempVector2 = self.pointEnd.clone().sub(self.pointStart)
                if space == 'local':
                    _tempVector.applyQuaternion(quaternion)
                    _tempVector2.applyQuaternion(self.worldQuaternionStart)

                rotationAngle = _tempVector2.dot(_tempVector.cross(self.eye).normalize()) * ROTATION_SPEED

            # Apply rotation snap

            if self.rotationSnap:
                rotationAngle = round(rotationAngle / self.rotationSnap) * self.rotationSnap

            self.rotationAngle = rotationAngle

            # Apply rotate

            if space == 'local':
                object.quaternion.copy(_quaternionStart)
                object.quaternion.multiply(_tempQuaternion.setFromAxisAngle(self.rotationAxis, rotationAngle))

            else:
                object.quaternion.copy(_tempQuaternion.setFromAxisAngle(self.rotationAxis, rotationAngle))
                object.quaternion.multiply(_quaternionStart)

        self.dispatchEvent(self.changeEvent)
        self.dispatchEvent(self.objectChangeEvent)

    def pointerUp(self, pointer, event):
        if pointer.button is not None and pointer.button != 0:
            return

        if self.dragging and (self.axis is not None):
            event.mode = self.mode
            self.dispatchEvent(event)

        self.dragging = False

        if pointer.button is None:
            self.axis = None

    def getPointer(self, event):
        """ normalize mouse / touch pointer and remap {x,y} to view space."""
        class _Pointer:
            def __init__(self, x, y, button):
                self.x  = x
                self.y = y
                self.button = button

        rect = self.domElement.getBoundingClientRect()

        return _Pointer(
            (event.clientX - rect.left) / rect.width * 2 - 1,
            - (event.clientY - rect.top) / rect.height * 2 + 1,
            event.button
        )

    # TODO: depricate

    def getMode(self):
        return self.mode

    def setMode(self, mode):
        self.mode = mode

    def setTranslationSnap(self, translationSnap):
        self.translationSnap = translationSnap

    def setRotationSnap(self, rotationSnap):
        self.rotationSnap = rotationSnap

    def setSize(self, size):
        self.size = size

    def setSpace(self, space):
        self.space = space

    def update(self):
        print('THREE.TransformControls: update function has been depricated.')


class TransformControlsGizmo(Object3D):
    isTransformControlsGizmo = True
    
    def __init__(self):
        super().__init__()

        self.type = 'TransformControlsGizmo'

        # shared materials

        gizmoMaterial = THREE.MeshBasicMaterial({
            "depthTest": False,
            "depthWrite": False,
            "transparent": True,
            "side": THREE.DoubleSide,
            "fog": False
       })

        gizmoLineMaterial = THREE.LineBasicMaterial({
            "depthTest": False,
            "depthWrite": False,
            "transparent": True,
            "linewidth": 1,
            "fog": False
       })

        # Make unique material for each axis/color

        matInvisible = gizmoMaterial.clone()
        matInvisible.opacity = 0.15

        mathelper = gizmoMaterial.clone()
        mathelper.opacity = 0.33

        matRed = gizmoMaterial.clone()
        matRed.color.set(0xff0000)

        matGreen = gizmoMaterial.clone()
        matGreen.color.set(0x00ff00)

        matBlue = gizmoMaterial.clone()
        matBlue.color.set(0x0000ff)

        matWhiteTransperent = gizmoMaterial.clone()
        matWhiteTransperent.opacity = 0.25

        matYellowTransparent = matWhiteTransperent.clone()
        matYellowTransparent.color.set(0xffff00)

        matCyanTransparent = matWhiteTransperent.clone()
        matCyanTransparent.color.set(0x00ffff)

        matMagentaTransparent = matWhiteTransperent.clone()
        matMagentaTransparent.color.set(0xff00ff)

        matYellow = gizmoMaterial.clone()
        matYellow.color.set(0xffff00)

        matLineRed = gizmoLineMaterial.clone()
        matLineRed.color.set(0xff0000)

        matLineGreen = gizmoLineMaterial.clone()
        matLineGreen.color.set(0x00ff00)

        matLineBlue = gizmoLineMaterial.clone()
        matLineBlue.color.set(0x0000ff)

        matLineCyan = gizmoLineMaterial.clone()
        matLineCyan.color.set(0x00ffff)

        matLineMagenta = gizmoLineMaterial.clone()
        matLineMagenta.color.set(0xff00ff)

        matLineBlue = gizmoLineMaterial.clone()
        matLineBlue.color.set(0x0000ff)

        matLineYellow = gizmoLineMaterial.clone()
        matLineYellow.color.set(0xffff00)

        matLineGray = gizmoLineMaterial.clone()
        matLineGray.color.set(0x787878)

        matLineYellowTransparent = matLineYellow.clone()
        matLineYellowTransparent.opacity = 0.25

        # reusable geometry

        arrowGeometry = THREE.CylinderBufferGeometry(0, 0.05, 0.2, 12, 1, False)

        scaleHandleGeometry = THREE.BoxBufferGeometry(0.125, 0.125, 0.125)

        lineGeometry = THREE.BufferGeometry()
        lineGeometry.addAttribute('position', THREE.Float32BufferAttribute([0, 0, 0,    1, 0, 0], 3))

        def CircleGeometry(radius, arc):
            geometry = THREE.BufferGeometry()
            vertices = []

            for i in range(0, int(64 * arc + 1)):
                vertices.extend([0, math.cos(i / 32 * math.pi) * radius, math.sin(i / 32 * math.pi) * radius])

            geometry.addAttribute('position', THREE.Float32BufferAttribute(vertices, 3))

            return geometry

        def TranslateHelperGeometry(radius = None, arc = None):
            """ Special geometry for transform helper. If scaled with position vector it spans from [0,0,0] to position"""
            geometry = THREE.BufferGeometry()

            geometry.addAttribute('position', THREE.Float32BufferAttribute([0, 0, 0, 1, 1, 1], 3))

            return geometry

        # Gizmo definitions - custom hierarchy definitions for setupGizmo() function

        gizmoTranslate = {
            "X": [
                [THREE.Mesh(arrowGeometry, matRed), [1, 0, 0], [0, 0, -math.pi / 2], None, 'fwd'],
                [THREE.Mesh(arrowGeometry, matRed), [1, 0, 0], [0, 0, math.pi / 2], None, 'bwd'],
                [THREE.Line(lineGeometry, matLineRed)]
           ],
            "Y": [
                [THREE.Mesh(arrowGeometry, matGreen), [0, 1, 0], None, None, 'fwd'],
                [THREE.Mesh(arrowGeometry, matGreen), [0, 1, 0], [math.pi, 0, 0], None, 'bwd'],
                [THREE.Line(lineGeometry, matLineGreen), None, [0, 0, math.pi / 2]]
           ],
            "Z": [
                [THREE.Mesh(arrowGeometry, matBlue), [0, 0, 1], [math.pi / 2, 0, 0], None, 'fwd'],
                [THREE.Mesh(arrowGeometry, matBlue), [0, 0, 1], [-math.pi / 2, 0, 0], None, 'bwd'],
                [THREE.Line(lineGeometry, matLineBlue), None, [0, -math.pi / 2, 0]]
           ],
            "XYZ": [
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.1, 0), matWhiteTransperent), [0, 0, 0], [0, 0, 0]]
           ],
            "XY": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.295, 0.295), matYellowTransparent), [0.15, 0.15, 0]],
                [THREE.Line(lineGeometry, matLineYellow), [0.18, 0.3, 0], None, [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineYellow), [0.3, 0.18, 0], [0, 0, math.pi / 2], [0.125, 1, 1]]
           ],
            "YZ": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.295, 0.295), matCyanTransparent), [0, 0.15, 0.15], [0, math.pi / 2, 0]],
                [THREE.Line(lineGeometry, matLineCyan), [0, 0.18, 0.3], [0, 0, math.pi / 2], [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineCyan), [0, 0.3, 0.18], [0, -math.pi / 2, 0], [0.125, 1, 1]]
           ],
            "XZ": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.295, 0.295), matMagentaTransparent), [0.15, 0, 0.15], [-math.pi / 2, 0, 0]],
                [THREE.Line(lineGeometry, matLineMagenta), [0.18, 0, 0.3], None, [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineMagenta), [0.3, 0, 0.18], [0, -math.pi / 2, 0], [0.125, 1, 1]]
           ]
       }

        pickerTranslate = {
            "X": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 1, 4, 1, False), matInvisible), [0.6, 0, 0], [0, 0, -math.pi / 2]]
           ],
            "Y": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 1, 4, 1, False), matInvisible), [0, 0.6, 0]]
           ],
            "Z": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 1, 4, 1, False), matInvisible), [0, 0, 0.6], [math.pi / 2, 0, 0]]
           ],
            "XYZ": [
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.2, 0), matInvisible)]
           ],
            "XY": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.4, 0.4), matInvisible), [0.2, 0.2, 0]]
           ],
            "YZ": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.4, 0.4), matInvisible), [0, 0.2, 0.2], [0, math.pi / 2, 0]]
           ],
            "XZ": [
                [THREE.Mesh(THREE.PlaneBufferGeometry(0.4, 0.4), matInvisible), [0.2, 0, 0.2], [-math.pi / 2, 0, 0]]
           ]
       }

        helperTranslate = {
            "START": [
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.01, 2), mathelper), None, None, None, 'helper']
           ],
            "END": [
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.01, 2), mathelper), None, None, None, 'helper']
           ],
            "DELTA": [
                [THREE.Line(TranslateHelperGeometry(), mathelper), None, None, None, 'helper']
           ],
            "X": [
                [THREE.Line(lineGeometry, mathelper.clone()), [-1e3, 0, 0], None, [1e6, 1, 1], 'helper']
           ],
            "Y": [
                [THREE.Line(lineGeometry, mathelper.clone()), [0, -1e3, 0], [0, 0, math.pi / 2], [1e6, 1, 1], 'helper']
           ],
            "Z": [
                [THREE.Line(lineGeometry, mathelper.clone()), [0, 0, -1e3], [0, -math.pi / 2, 0], [1e6, 1, 1], 'helper']
           ]
       }

        gizmoRotate = {
            "X": [
                [THREE.Line(CircleGeometry(1, 0.5), matLineRed)],
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.04, 0), matRed), [0, 0, 0.99], None, [1, 3, 1]],
           ],
            "Y": [
                [THREE.Line(CircleGeometry(1, 0.5), matLineGreen), None, [0, 0, -math.pi / 2]],
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.04, 0), matGreen), [0, 0, 0.99], None, [3, 1, 1]],
           ],
            "Z": [
                [THREE.Line(CircleGeometry(1, 0.5), matLineBlue), None, [0, math.pi / 2, 0]],
                [THREE.Mesh(THREE.OctahedronBufferGeometry(0.04, 0), matBlue), [0.99, 0, 0], None, [1, 3, 1]],
           ],
            "E": [
                [THREE.Line(CircleGeometry(1.25, 1), matLineYellowTransparent), None, [0, math.pi / 2, 0]],
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.03, 0, 0.15, 4, 1, False), matLineYellowTransparent), [1.17, 0, 0], [0, 0, -math.pi / 2], [1, 1, 0.001]],
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.03, 0, 0.15, 4, 1, False), matLineYellowTransparent), [-1.17, 0, 0], [0, 0, math.pi / 2], [1, 1, 0.001]],
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.03, 0, 0.15, 4, 1, False), matLineYellowTransparent), [0, -1.17, 0], [math.pi, 0, 0], [1, 1, 0.001]],
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.03, 0, 0.15, 4, 1, False), matLineYellowTransparent), [0, 1.17, 0], [0, 0, 0], [1, 1, 0.001]],
           ],
            "XYZE": [
                [THREE.Line(CircleGeometry(1, 1), matLineGray), None, [0, math.pi / 2, 0]]
           ]
       }

        helperRotate = {
            "AXIS": [
                [THREE.Line(lineGeometry, mathelper.clone()), [-1e3, 0, 0], None, [1e6, 1, 1], 'helper']
           ]
       }

        pickerRotate = {
            "X": [
                [THREE.Mesh(THREE.TorusBufferGeometry(1, 0.1, 4, 24), matInvisible), [0, 0, 0], [0, -math.pi / 2, -math.pi / 2]],
           ],
            "Y": [
                [THREE.Mesh(THREE.TorusBufferGeometry(1, 0.1, 4, 24), matInvisible), [0, 0, 0], [math.pi / 2, 0, 0]],
           ],
            "Z": [
                [THREE.Mesh(THREE.TorusBufferGeometry(1, 0.1, 4, 24), matInvisible), [0, 0, 0], [0, 0, -math.pi / 2]],
           ],
            "E": [
                [THREE.Mesh(THREE.TorusBufferGeometry(1.25, 0.1, 2, 24), matInvisible)]
           ],
            "XYZE": [
                [THREE.Mesh(THREE.SphereBufferGeometry(0.7, 10, 8), matInvisible)]
           ]
       }

        gizmoScale = {
            "X": [
                [THREE.Mesh(scaleHandleGeometry, matRed), [0.8, 0, 0], [0, 0, -math.pi / 2]],
                [THREE.Line(lineGeometry, matLineRed), None, None, [0.8, 1, 1]]
           ],
            "Y": [
                [THREE.Mesh(scaleHandleGeometry, matGreen), [0, 0.8, 0]],
                [THREE.Line(lineGeometry, matLineGreen), None, [0, 0, math.pi / 2], [0.8, 1, 1]]
           ],
            "Z": [
                [THREE.Mesh(scaleHandleGeometry, matBlue), [0, 0, 0.8], [math.pi / 2, 0, 0]],
                [THREE.Line(lineGeometry, matLineBlue), None, [0, -math.pi / 2, 0], [0.8, 1, 1]]
           ],
            "XY": [
                [THREE.Mesh(scaleHandleGeometry, matYellowTransparent), [0.85, 0.85, 0], None, [2, 2, 0.2]],
                [THREE.Line(lineGeometry, matLineYellow), [0.855, 0.98, 0], None, [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineYellow), [0.98, 0.855, 0], [0, 0, math.pi / 2], [0.125, 1, 1]]
           ],
            "YZ": [
                [THREE.Mesh(scaleHandleGeometry, matCyanTransparent), [0, 0.85, 0.85], None, [0.2, 2, 2]],
                [THREE.Line(lineGeometry, matLineCyan), [0, 0.855, 0.98], [0, 0, math.pi / 2], [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineCyan), [0, 0.98, 0.855], [0, -math.pi / 2, 0], [0.125, 1, 1]]
           ],
            "XZ": [
                [THREE.Mesh(scaleHandleGeometry, matMagentaTransparent), [0.85, 0, 0.85], None, [2, 0.2, 2]],
                [THREE.Line(lineGeometry, matLineMagenta), [0.855, 0, 0.98], None, [0.125, 1, 1]],
                [THREE.Line(lineGeometry, matLineMagenta), [0.98, 0, 0.855], [0, -math.pi / 2, 0], [0.125, 1, 1]]
           ],
            "XYZX": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.125, 0.125, 0.125), matWhiteTransperent), [1.1, 0, 0]],
           ],
            "XYZY": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.125, 0.125, 0.125), matWhiteTransperent), [0, 1.1, 0]],
           ],
            "XYZZ": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.125, 0.125, 0.125), matWhiteTransperent), [0, 0, 1.1]],
           ]
       }

        pickerScale = {
            "X": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 0.8, 4, 1, False), matInvisible), [0.5, 0, 0], [0, 0, -math.pi / 2]]
           ],
            "Y": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 0.8, 4, 1, False), matInvisible), [0, 0.5, 0]]
           ],
            "Z": [
                [THREE.Mesh(THREE.CylinderBufferGeometry(0.2, 0, 0.8, 4, 1, False), matInvisible), [0, 0, 0.5], [math.pi / 2, 0, 0]]
           ],
            "XY": [
                [THREE.Mesh(scaleHandleGeometry, matInvisible), [0.85, 0.85, 0], None, [3, 3, 0.2]],
           ],
            "YZ": [
                [THREE.Mesh(scaleHandleGeometry, matInvisible), [0, 0.85, 0.85], None, [0.2, 3, 3]],
           ],
            "XZ": [
                [THREE.Mesh(scaleHandleGeometry, matInvisible), [0.85, 0, 0.85], None, [3, 0.2, 3]],
           ],
            "XYZX": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.2, 0.2, 0.2), matInvisible), [1.1, 0, 0]],
           ],
            "XYZY": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.2, 0.2, 0.2), matInvisible), [0, 1.1, 0]],
           ],
            "XYZZ": [
                [THREE.Mesh(THREE.BoxBufferGeometry(0.2, 0.2, 0.2), matInvisible), [0, 0, 1.1]],
           ]
       }

        helperScale = {
            "X": [
                [THREE.Line(lineGeometry, mathelper.clone()), [-1e3, 0, 0], None, [1e6, 1, 1], 'helper']
           ],
            "Y": [
                [THREE.Line(lineGeometry, mathelper.clone()), [0, -1e3, 0], [0, 0, math.pi / 2], [1e6, 1, 1], 'helper']
           ],
            "Z": [
                [THREE.Line(lineGeometry, mathelper.clone()), [0, 0, -1e3], [0, -math.pi / 2, 0], [1e6, 1, 1], 'helper']
           ]
       }

        def setupGizmo(gizmoMap):
            """ Special geometry for transform helper. If scaled with position vector it spans from [0,0,0] to position"""
            gizmo = THREE.Object3D()

            for name in gizmoMap:
                for i in range(len(gizmoMap[name]) - 1, -1, -1):
                    lst = gizmoMap[name][i]
                    object = lst[0].clone()

                    # name and tag properties are essential for picking and updating logic.
                    object.name = name
                    object.tag  = ""

                    if len(lst) > 1:
                        position = lst[1]
                        if position is not None:
                            object.position.set(position[0], position[1], position[2])

                        if len(lst) > 2:
                            rotation = lst[2]
                            if rotation is not None :
                                object.rotation.set(rotation[0], rotation[1], rotation[2])

                            if len(lst) > 3:
                                scale = lst[3]
                                if scale is not None:
                                    object.scale.set(scale[0], scale[1], scale[2])

                                if len(lst) > 4:
                                    tag = lst[4]
                                    object.tag = tag

                    object.updateMatrix()

                    tempGeometry = object.geometry.clone()
                    tempGeometry.applyMatrix(object.matrix)
                    object.geometry = tempGeometry

                    object.position.set(0, 0, 0)
                    object.rotation.set(0, 0, 0)
                    object.scale.set(1, 1, 1)

                    gizmo.add(object)

            return gizmo

        # Reusable utility variables

        tempVector = THREE.Vector3(0, 0, 0)
        alignVector = THREE.Vector3(0, 1, 0)
        zeroVector = THREE.Vector3(0, 0, 0)
        lookAtMatrix = THREE.Matrix4()
        tempQuaternion = THREE.Quaternion()
        tempQuaternion2 = THREE.Quaternion()
        identityQuaternion = THREE.Quaternion()

        unitX = THREE.Vector3(1, 0, 0)
        unitY = THREE.Vector3(0, 1, 0)
        unitZ = THREE.Vector3(0, 0, 1)

        # Gizmo creation

        self.gizmo = {}
        self.picker = {}
        self.helper = {}

        self.gizmo["translate"] = setupGizmo(gizmoTranslate)
        self.gizmo["rotate"] = setupGizmo(gizmoRotate)
        self.gizmo["scale"] = setupGizmo(gizmoScale)
        self.picker["translate"] = setupGizmo(pickerTranslate)
        self.picker["rotate"] = setupGizmo(pickerRotate)
        self.picker["scale"] = setupGizmo(pickerScale)
        self.helper["translate"] = setupGizmo(helperTranslate)
        self.helper["rotate"] = setupGizmo(helperRotate)
        self.helper["scale"] = setupGizmo(helperScale)

        self.add(self.gizmo["translate"])
        self.add(self.gizmo["rotate"])
        self.add(self.gizmo["scale"])
        self.add(self.picker["translate"])
        self.add(self.picker["rotate"])
        self.add(self.picker["scale"])
        self.add(self.helper["translate"])
        self.add(self.helper["rotate"])
        self.add(self.helper["scale"])

        # Pickers should be hidden always

        self.picker["translate"].visible = False
        self.picker["rotate"].visible = False
        self.picker["scale"].visible = False

    def updateMatrixWorld(self, force=False, parent_matrixWorld_is_updated=True):
        """ updateMatrixWorld will update transformations and appearance of individual handles"""
        global _tempQuaternion
        global _tempQuaternion2
        global _tempVector
        global _tempEuler
        global _identityQuaternion
        global _alignVector
        global _unitX
        global _unitY
        global _zeroVector
        global _lookAtMatrix

        space = self.parent.space
        mode = self.parent.mode
        axis = self.parent.axis
        eye = self.parent.eye
        worldPosition = self.parent.worldPosition
        worldPositionStart = self.parent.worldPositionStart
        worldQuaternionStart = self.parent.worldQuaternionStart
        size = self.parent.size
        dragging = self.parent.dragging
        rotationAxis = self.parent.rotationAxis

        if mode == 'scale':
            space = 'local' # scale always oriented to local rotation

        quaternion = self.parent.worldQuaternion if space == "local" else _identityQuaternion

        # Show only gizmos for current transform mode

        self.gizmo["translate"].visible = mode == "translate"
        self.gizmo["rotate"].visible = mode == "rotate"
        self.gizmo["scale"].visible = mode == "scale"

        self.helper["translate"].visible = mode == "translate"
        self.helper["rotate"].visible = mode == "rotate"
        self.helper["scale"].visible = mode == "scale"


        handles = []
        handles.extend(self.picker[mode].children)
        handles.extend(self.gizmo[mode].children)
        handles.extend(self.helper[mode].children)

        for i in range(len(handles)):
            handle = handles[i]

            # hide aligned to camera

            handle.visible = True
            handle.rotation.set(0, 0, 0)
            handle.position.copy(self.parent.worldPosition)

            eyeDistance = self.parent.worldPosition.distanceTo(self.parent.cameraPosition)
            handle.scale.set(1, 1, 1).multiplyScalar(eyeDistance * size / 7)

            # TODO: simplify helpers and consider decoupling from gizmo

            if hasattr(handle, 'tag') and handle.tag == 'helper':
                handle.visible = False

                if handle.name == 'AXIS':
                    handle.position.copy(self.parent.worldPositionStart)
                    handle.visible = not axis

                    if axis == 'X':
                        _tempQuaternion.setFromEuler(_tempEuler.set(0, 0, 0))
                        handle.quaternion.copy(quaternion).multiply(_tempQuaternion)

                        if abs(_alignVector.copy(_unitX).applyQuaternion(quaternion).dot(eye)) > 0.9:
                            handle.visible = False

                    if axis == 'Y':
                        _tempQuaternion.setFromEuler(_tempEuler.set(0, 0, math.pi / 2))
                        handle.quaternion.copy(quaternion).multiply(_tempQuaternion)

                        if abs(_alignVector.copy(_unitY).applyQuaternion(quaternion).dot(eye)) > 0.9:
                            handle.visible = False

                    if axis == 'Z':
                        _tempQuaternion.setFromEuler(_tempEuler.set(0, math.pi / 2, 0))
                        handle.quaternion.copy(quaternion).multiply(_tempQuaternion)

                        if abs(_alignVector.copy(_unitZ).applyQuaternion(quaternion).dot(eye)) > 0.9:
                            handle.visible = False

                    if axis == 'XYZE':
                        _tempQuaternion.setFromEuler(_tempEuler.set(0, math.pi / 2, 0))
                        _alignVector.copy(rotationAxis)
                        handle.quaternion.setFromRotationMatrix(_lookAtMatrix.lookAt(_zeroVector, _alignVector, _unitY))
                        handle.quaternion.multiply(_tempQuaternion)
                        handle.visible = dragging

                    if axis == 'E':
                        handle.visible = False

                elif handle.name == 'START':
                    handle.position.copy(worldPositionStart)
                    handle.visible = dragging

                elif handle.name == 'END':
                    handle.position.copy(worldPosition)
                    handle.visible = dragging

                elif handle.name == 'DELTA':
                    handle.position.copy(worldPositionStart)
                    handle.quaternion.copy(worldQuaternionStart)
                    _tempVector.set(1e-10, 1e-10, 1e-10).add(worldPositionStart).sub(worldPosition).multiplyScalar(-1)
                    _tempVector.applyQuaternion(worldQuaternionStart.clone().inverse())
                    handle.scale.copy(_tempVector)
                    handle.visible = dragging

                else:
                    handle.quaternion.copy(quaternion)

                    if dragging:
                        handle.position.copy(worldPositionStart)

                    else:
                        handle.position.copy(worldPosition)

                    if axis:
                        handle.visible = axis.find(handle.name) != -1

                # If updating helper, skip rest of the loop
                continue

            # Align handles to current local or world rotation

            handle.quaternion.copy(quaternion)

            if mode == 'translate' or mode == 'scale':
                # Hide translate and scale axis facing the camera

                AXIS_HIDE_TRESHOLD = 0.99
                PLANE_HIDE_TRESHOLD = 0.2
                AXIS_FLIP_TRESHOLD = -0.4

                if handle.name == 'X' or handle.name == 'XYZX':
                    if abs(_alignVector.copy(_unitX).applyQuaternion(quaternion).dot(eye)) > AXIS_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                if handle.name == 'Y' or handle.name == 'XYZY':
                    if abs(_alignVector.copy(_unitY).applyQuaternion(quaternion).dot(eye)) > AXIS_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                if handle.name == 'Z' or handle.name == 'XYZZ':
                    if abs(_alignVector.copy(_unitZ).applyQuaternion(quaternion).dot(eye)) > AXIS_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                if handle.name == 'XY':
                    if abs(_alignVector.copy(_unitZ).applyQuaternion(quaternion).dot(eye)) < PLANE_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                if handle.name == 'YZ':
                    if abs(_alignVector.copy(_unitX).applyQuaternion(quaternion).dot(eye)) < PLANE_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                if handle.name == 'XZ':
                    if abs(_alignVector.copy(_unitY).applyQuaternion(quaternion).dot(eye)) < PLANE_HIDE_TRESHOLD:
                        handle.scale.set(1e-10, 1e-10, 1e-10)
                        handle.visible = False

                # Flip translate and scale axis ocluded behind another axis

                if handle.name.find('X') != -1:
                    if _alignVector.copy(_unitX).applyQuaternion(quaternion).dot(eye) < AXIS_FLIP_TRESHOLD:
                        if handle.tag == 'fwd':
                            handle.visible = False
                        else:
                            handle.scale.x *= -1
                    elif handle.tag == 'bwd':
                        handle.visible = False

                if handle.name.find('Y') != -1:
                    if _alignVector.copy(_unitY).applyQuaternion(quaternion).dot(eye) < AXIS_FLIP_TRESHOLD:
                        if handle.tag == 'fwd':
                            handle.visible = False
                        else:
                            handle.scale.y *= -1
                    elif handle.tag == 'bwd':
                        handle.visible = False

                if handle.name.find('Z') != -1:
                    if _alignVector.copy(_unitZ).applyQuaternion(quaternion).dot(eye) < AXIS_FLIP_TRESHOLD:
                        if handle.tag == 'fwd':
                            handle.visible = False
                        else:
                            handle.scale.z *= -1
                    elif handle.tag == 'bwd':
                        handle.visible = False

            elif mode == 'rotate':
                # Align handles to current local or world rotation

                _tempQuaternion2.copy(quaternion)
                _alignVector.copy(eye).applyQuaternion(_tempQuaternion.copy(quaternion).inverse())

                if handle.name.find("E") != - 1:
                    handle.quaternion.setFromRotationMatrix(_lookAtMatrix.lookAt(eye, _zeroVector, _unitY))

                if handle.name == 'X':
                    _tempQuaternion.setFromAxisAngle(_unitX, math.atan2(-_alignVector.y, _alignVector.z))
                    _tempQuaternion.multiplyQuaternions(_tempQuaternion2, _tempQuaternion)
                    handle.quaternion.copy(_tempQuaternion)

                if handle.name == 'Y':
                    _tempQuaternion.setFromAxisAngle(_unitY, math.atan2(_alignVector.x, _alignVector.z))
                    _tempQuaternion.multiplyQuaternions(_tempQuaternion2, _tempQuaternion)
                    handle.quaternion.copy(_tempQuaternion)

                if handle.name == 'Z':
                    _tempQuaternion.setFromAxisAngle(_unitZ, math.atan2(_alignVector.y, _alignVector.x))
                    _tempQuaternion.multiplyQuaternions(_tempQuaternion2, _tempQuaternion)
                    handle.quaternion.copy(_tempQuaternion)

            # highlight selected axis

            ud = handle.material.userData

            if 'opacity' in ud:
                _o = ud['opacity']
            else:
                _o = handle.material.opacity
            ud['opacity'] = _o

            if 'color' in ud:
                _o = ud['color']
            else:
                _o = handle.material.color.clone()
            ud['color'] = _o

            handle.material.color.copy(handle.material.userData['color'])
            handle.material.opacity = handle.material.userData['opacity']

            if axis:
                if handle.name == axis:
                    handle.material.opacity = 1.0
                    handle.material.color.lerp(THREE.Color(1, 1, 1), 0.5)
                else:
                    f = False
                    for a in axis:
                        if handle.name == a:
                            handle.material.opacity = 1.0
                            handle.material.color.lerp(THREE.Color(1, 1, 1), 0.5)
                            f = True
                            break

                    if not f:
                        handle.material.opacity *= 0.05

        super().updateMatrixWorld(force, parent_matrixWorld_is_updated)


class TransformControlsPlane(Mesh):
    isTransformControlsPlane = True
    
    def __init__(self):
        super().__init__(
            THREE.PlaneBufferGeometry(100000, 100000, 2, 2),
            THREE.MeshBasicMaterial({"visible": False, "wireframe": True, "side": THREE.DoubleSide, "transparent": True, "opacity": 0.1})
       )

        self.type = 'TransformControlsPlane'

    def updateMatrixWorld(self, force=False, parent_matrixWorld_is_updated=True):
        global _identityQuaternion
        global _alignVector
        global _tempVector
        global _dirVector
        global _tempMatrix
        global _unitX
        global _unitY
        global _unitZ

        space = self.parent.space
        mode = self.parent.mode
        worldPosition = self.parent.worldPosition
        worldQuaternion = self.parent.worldQuaternion
        axis = self.parent.axis
        cameraQuaternion = self.parent.cameraQuaternion
        eye = self.parent.eye

        self.position.copy(worldPosition)

        if mode == 'scale':
            space = 'local' # scale always oriented to local rotation

        _unitX.set(1, 0, 0).applyQuaternion(worldQuaternion if space == "local" else _identityQuaternion)
        _unitY.set(0, 1, 0).applyQuaternion(worldQuaternion if space == "local" else _identityQuaternion)
        _unitZ.set(0, 0, 1).applyQuaternion(worldQuaternion if space == "local" else _identityQuaternion)

        # Align the plane for current transform mode, axis and space.

        _alignVector.copy(_unitY)

        if mode == 'translate' or mode == 'scale':
                if axis == 'X':
                    _alignVector.copy(eye).cross(_unitX)
                    _dirVector.copy(_unitX).cross(_alignVector)
                elif axis == 'Y':
                    _alignVector.copy(eye).cross(_unitY)
                    _dirVector.copy(_unitY).cross(_alignVector)
                elif axis == 'Z':
                    _alignVector.copy(eye).cross(_unitZ)
                    _dirVector.copy(_unitZ).cross(_alignVector)
                elif axis == 'XY':
                    _dirVector.copy(_unitZ)
                elif axis == 'YZ':
                    _dirVector.copy(_unitX)
                elif axis == 'XZ':
                    _alignVector.copy(_unitZ)
                    _dirVector.copy(_unitY)
                elif axis == 'XYZ' or axis == 'E':
                    _dirVector.set(0, 0, 0)
        #elif self.mode === 'rotate':
        else:
            # special case for rotate
            _dirVector.set(0, 0, 0)

        if _dirVector.length() == 0:
            # If in rotate mode, make the plane parallel to camera
            self.quaternion.copy(cameraQuaternion)

        else:
            _tempMatrix.lookAt(_tempVector.set(0, 0, 0), _dirVector, _alignVector)
            self.quaternion.setFromRotationMatrix(_tempMatrix)

        super().updateMatrixWorld(force, parent_matrixWorld_is_updated)
