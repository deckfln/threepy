"""
        <title>three.js webgl - geometry - cube</title>
"""
import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(mango_dir)

import random
import math
import sys
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
        self.container = None
        self.mesh = None
        self.mesh1 = None

        
def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 1000)
    p.camera.position.z = 400

    p.scene = THREE.Scene()
    texture = THREE.TextureLoader().load('textures/crate.gif')

    light = THREE.PointLight( 0xffffff )
    light.position.copy( p.camera.position )
    p.scene.add( light )

    geometry = THREE.BoxBufferGeometry(200, 200, 200)
    material = THREE.MeshLambertMaterial({'map': texture})

    p.mesh = THREE.Mesh(geometry, material)
    p.scene.add(p.mesh)

    p.mesh1 = THREE.Mesh(geometry, material)
    p.mesh1.position.x = 50
    p.mesh1.position.y = 50
    p.mesh1.name = "extras"
    p.scene.add(p.mesh1)

    p.renderer = p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    # //

    p.container.addEventListener( 'resize', onWindowResize, False )

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    
def animate(p):
    p.mesh.rotation.x += 0.005
    p.mesh.rotation.y += 0.01

    p.renderer.render( p.scene, p.camera )
    p.gui.update()

    
def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
