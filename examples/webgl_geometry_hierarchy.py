"""
<title>three.js webgl - geometry hierarchy</title>
"""

import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )
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

    p.camera = THREE.PerspectiveCamera( 60, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 500

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xffffff )
    p.scene.fog = THREE.Fog( 0xffffff, 1, 10000 )

    ambientLight = THREE.AmbientLight(0x222222)
    p.scene.add(ambientLight)

    geometry = THREE.BoxBufferGeometry( 100, 100, 100 )
    material = THREE.MeshNormalMaterial()

    p.group = THREE.Group()

    for i in range(1000):
        mesh = THREE.Mesh( geometry, material )
        # mesh.frustumCulled = False
        mesh.position.x = random.random() * 2000 - 1000
        mesh.position.y = random.random() * 2000 - 1000
        mesh.position.z = random.random() * 2000 - 1000

        mesh.rotation.x = random.random() * 2 * math.pi
        mesh.rotation.y = random.random() * 2 * math.pi

        mesh.matrixAutoUpdate = False
        mesh.updateMatrix()

        p.group.add( mesh )

    p.scene.add( p.group )

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def onDocumentMouseMove(event, p ):
    p.mouseX = ( event.clientX - p.windowHalfX ) * 10
    p.mouseY = ( event.clientY - p.windowHalfY ) * 10


def animate(p):
    render(p)
    p.gui.update()


def render(p: Params):
    time = datetime.now().timestamp() * 1

    rx = math.sin( time * 0.7 ) * 0.5
    ry = math.sin( time * 0.3 ) * 0.5
    rz = math.sin( time * 0.2 ) * 0.5

    #p.camera.position.x += ( p.mouseX - p.camera.position.x ) * 0.05
    #p.camera.position.y += ( - p.mouseY - p.camera.position.y ) * 0.05
    p.camera.position.x += math.sin(time * 0.7) * 50
    p.camera.position.y += math.sin(time * 0.3) * 50

    p.camera.lookAt( p.scene.position )

    p.group.rotation.x = rx
    p.group.rotation.y = ry
    p.group.rotation.z = rz

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.start_benchmark()
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
