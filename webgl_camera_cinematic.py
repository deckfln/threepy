"""
        <title>three.js webgl-camera cinematic</title>
"""
import sys
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.Constants import *
import THREE._Math as _Math
from THREE.cameras.CinematicCamera import *


container = None
camera = None
scene = None
raycaster = None
renderer = None

mouse = THREE.Vector2()
INTERSECTED = None
radius = 100
theta = 0


def init():
    global container, camera, scene, raycaster, renderer, raycaster
    container = pyOpenGL()

    camera = CinematicCamera( 60, container.clientWidth / container.clientHeight, 1, 1000 )
    camera.setLens(5)
    camera.position.set(2, 1, 500)

    scene = THREE.Scene()
    scene.background = THREE.Color( 0xf0f0f0 )

    scene.add( THREE.AmbientLight( 0xffffff, 0.3 ) )

    light = THREE.DirectionalLight( 0xffffff, 0.35 )
    light.position.set( 1, 1, 1 ).normalize()
    scene.add( light )

    geometry = THREE.BoxGeometry( 20, 20, 20 )

    for i in range(1500):
        object = THREE.Mesh( geometry, THREE.MeshLambertMaterial( { 'color': random.random() * 0xffffff } ) )

        object.position.x = random.random() * 800 - 400
        object.position.y = random.random() * 800 - 400
        object.position.z = random.random() * 800 - 400

        scene.add( object )

    raycaster = THREE.Raycaster()

    renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    renderer.setSize( container.clientWidth, container.clientHeight )

    container.addEventListener( 'mousemove', onDocumentMouseMove, False )
    container.addEventListener( 'resize', onWindowResize, False )

    effectController  = {
        'focalLength': 15,
        # // jsDepthCalculation: true,
        # // shaderFocus: false,
        # //
        'fstop': 2.8,
        # // maxblur: 1.0,
        # //
        'showFocus': False,
        'focalDepth': 3,
        # // manualdof: false,
        # // vignetting: false,
        # // depthblur: false,
        # //
        # // threshold: 0.5,
        # // gain: 2.0,
        # // bias: 0.5,
        # // fringe: 0.7,
        # //
        # // focalLength: 35,
        # // noise: true,
        # // pentagon: false,
        # //
        # // dithering: 0.0001
    }

    def matChanger():
        for e in effectController:
            if e in camera.postprocessing.bokeh_uniforms:
                camera.postprocessing.bokeh_uniforms[ e ].value = effectController[ e ]

        camera.postprocessing.bokeh_uniforms[ 'znear' ].value = camera.near
        camera.postprocessing.bokeh_uniforms[ 'zfar' ].value = camera.far
        camera.setLens(effectController['focalLength'], camera.frameHeight ,effectController['fstop'], camera.coc)
        effectController['focalDepth'] = camera.postprocessing.bokeh_uniforms["focalDepth"].value

    matChanger()

    container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event):
    global camera, scene, renderer, container
    height = event.height
    width = event.width
    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)


def onDocumentMouseMove( event ):
    global camera, scene, renderer, container,mouse
    event.preventDefault()

    mouse.x = ( event.clientX / container.clientWidth ) * 2 - 1
    mouse.y = - ( event.clientY / container.clientHeight ) * 2 + 1


def animate():
    render()


def render():
    global camera, scene, renderer, container, mouse
    global theta, INTERSECTED, raycaster

    theta += 0.1

    camera.position.x = radius * math.sin( _Math.degToRad( theta ) )
    camera.position.y = radius * math.sin( _Math.degToRad( theta ) )
    camera.position.z = radius * math.cos( _Math.degToRad( theta ) )
    camera.lookAt( scene.position )

    camera.updateMatrixWorld()

    # // find intersections

    raycaster.setFromCamera( mouse, camera )

    intersects = raycaster.intersectObjects( scene.children )

    if len(intersects) > 0:
        targetDistance = intersects[ 0 ].distance
        
        # // Using Cinematic camera focusAt method
        camera.focusAt(targetDistance)

        if INTERSECTED != intersects[ 0 ].object:
            if INTERSECTED:
                INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex )

            INTERSECTED = intersects[ 0 ].object
            INTERSECTED.currentHex = INTERSECTED.material.emissive.getHex()
            INTERSECTED.material.emissive.setHex( 0xff0000 )
    else:
        if INTERSECTED:
            INTERSECTED.material.emissive.setHex( INTERSECTED.currentHex )

        INTERSECTED = None

    if camera.postprocessing.enabled:
        # //rendering Cinematic Camera effects
        camera.renderCinematic(scene, renderer)
    else:
        scene.overrideMaterial = None

        renderer.clear()
        renderer.render( scene, camera )


def main(argv=None):
    global container
    init()
    container.addEventListener( 'animationRequest', animate)
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
