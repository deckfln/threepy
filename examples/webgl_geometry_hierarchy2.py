"""
        <title>three.js webgl - geometry hierarchy 2</title>
"""

import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(mango_dir)


import math
import random
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.root = None
        self.group = None
        self.mouseX = 0
        self.mouseY = 0
        self.windowHalfX = window.innerWidth / 2
        self.windowHalfY = window.innerHeight / 2


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.container.addEventListener('mousemove', onDocumentMouseMove)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 15000)
    p.camera.position.z = 500

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(0xffffff)

    p.geometry = THREE.BoxBufferGeometry(100, 100, 100)
    material = THREE.MeshNormalMaterial()

    p.root = THREE.Mesh(p.geometry, material)
    p.root.position.x = 1000
    p.scene.add(p.root)

    amount = 200
    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.x = 100

        parent.add(object)
        parent = object

    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.x = - 100

        parent.add(object)
        parent = object

    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.y = - 100

        parent.add(object)
        parent = object

    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.y = 100

        parent.add(object)
        parent = object

    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.z = - 100

        parent.add(object)
        parent = object

    parent = p.root

    for i in range(amount):
        object = THREE.Mesh(p.geometry, material)
        object.position.z = 100

        parent.add(object)
        parent = object

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)


def onDocumentMouseMove(event, p):
    p.mouseX = (event.clientX - p.windowHalfX) * 10
    p.mouseY = (event.clientY - p.windowHalfY) * 10


def animate(p):
    render(p)
    p.gui.update()


def render(p):
    time = datetime.now().timestamp() * 1

    rx = math.sin(time * 0.7) * 0.2
    ry = math.sin(time * 0.3) * 0.1
    rz = math.sin(time * 0.2) * 0.1

    p.camera.position.x += (p.mouseX - p.camera.position.x) * 0.05
    p.camera.position.y += (- p.mouseY - p.camera.position.y) * 0.05

    p.camera.lookAt(p.scene.position)

    def fn(obj, scope):
        obj.rotation.x = rx
        obj.rotation.y = ry
        obj.rotation.z = rz

    p.root.traverse(fn)

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    p = Params()

    init(p)
    p.container.start_benchmark()
    p.container.addEventListener('animationRequest', animate)
    return p.container.loop()


if __name__ == "__main__":
    sys.exit(main())
