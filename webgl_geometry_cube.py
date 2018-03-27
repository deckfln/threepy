"""
        <title>three.js webgl - geometry - cube</title>
"""
import random
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.mesh1 = None

        
def init(params):
    params.container = pyOpenGL(params)

    params.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 1000)
    params.camera.position.z = 400

    params.scene = THREE.Scene()
    texture = THREE.TextureLoader().load('textures/dirt.png')

    geometry = THREE.BoxBufferGeometry(200, 200, 200)
    material = THREE.MeshBasicMaterial({'map': texture})

    params.mesh = THREE.Mesh(geometry, material)
    params.scene.add(params.mesh)

    params.mesh1 = THREE.Mesh(geometry, material)
    params.mesh1.position.x = 50
    params.mesh1.position.y = 50
    params.scene.add(params.mesh1)

    params.renderer = params.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    params.renderer.setSize( window.innerWidth, window.innerHeight )

    # //

    params.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )

    
def animate(params):
    params.mesh.rotation.x += 0.005
    params.mesh.rotation.y += 0.01

    params.renderer.render( params.scene, params.camera )

    
def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
