"""
        <title>three.js webgl - buffergeometry - lines - indexed</title>
"""        
import math
import random
from datetime import datetime
from THREE import *


camera = None
scene = None
renderer = None

mesh = None
parent_node = None

WIDTH = 800
HEIGHT = 600


def init():
    global camera, scene, renderer, parent_node

    camera = THREE.PerspectiveCamera( 27, WIDTH / HEIGHT, 1, 10000 )
    camera.position.z = 9000

    scene = THREE.Scene()

    geometry = THREE.BufferGeometry()
    material = THREE.LineBasicMaterial({ 'vertexColors': THREE.VertexColors })

    positions = []
    next_positions_index = 0
    colors = []
    indices_array = []

    # //

    iteration_count = 4
    rangle = 60 * math.pi / 180.0

    def add_vertex(v):
        nonlocal next_positions_index
        if next_positions_index == 0xffff:
            raise RuntimeError("Too many points")

        positions.extend([v.x, v.y, v.z])
        colors.extend([random.random()*0.5+0.5, random.random()*0.5+0.5, 1])
        next_positions_index += 1

    # // simple Koch curve
    def snowflake_iteration(p0, p4, depth):
        depth -= 1
        if depth < 0:
            i = next_positions_index-1    # // p0 already there
            add_vertex(p4)
            indices_array.extend([i, i+1])
            return

        v = p4.clone().sub(p0)
        v_tier = v.clone().multiplyScalar(1.0/3.0)
        p1 = p0.clone().add(v_tier)

        angle = math.atan2(v.y, v.x) + rangle
        length = v_tier.length()
        p2 = p1.clone()
        p2.x += math.cos(angle) * length
        p2.y += math.sin(angle) * length

        p3 = p0.clone().add(v_tier).add(v_tier)

        snowflake_iteration(p0, p1, depth)
        snowflake_iteration(p1, p2, depth)
        snowflake_iteration(p2, p3, depth)
        snowflake_iteration(p3, p4, depth)

    def snowflake(points, loop, x_offset):
        for iteration in range(iteration_count):
            add_vertex(points[0])
            for p_index in range(len(points) - 1):
                snowflake_iteration(points[p_index], points[p_index+1], iteration)

            if loop:
                snowflake_iteration(points[len(points)-1], points[0], iteration)

            # // translate input curve for next iteration
            for p_index in range(len(points)):
                points[p_index].x += x_offset

    y = 0
    snowflake(
        [
            THREE.Vector3(0, y+0, 0),
            THREE.Vector3(500, y+0, 0)
        ],
        False, 600)

    y += 600
    snowflake(
        [
            THREE.Vector3(0, y+0, 0),
            THREE.Vector3(250, y+400, 0),
            THREE.Vector3(500, y+0, 0)
        ],
        True, 600)

    y += 600
    snowflake(
        [
            THREE.Vector3(0, y+0, 0),
            THREE.Vector3(500, y, 0),
            THREE.Vector3(500, y+500, 0),
            THREE.Vector3(0, y+500, 0)
        ],
        True, 600)

    y += 1000
    snowflake(
        [
            THREE.Vector3(250, y+0, 0),
            THREE.Vector3(500, y+0, 0),
            THREE.Vector3(250, y+0, 0),
            THREE.Vector3(250, y+250, 0),
            THREE.Vector3(250, y+0, 0),
            THREE.Vector3(0, y, 0),
            THREE.Vector3(250, y+0, 0),
            THREE.Vector3(250, y-250, 0),
            THREE.Vector3(250, y+0, 0)
        ],
        False, 600)
    # // --------------------------------

    geometry.setIndex( indices_array )
    geometry.addAttribute( 'position', THREE.Float32BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'color', THREE.Float32BufferAttribute( colors, 3 ) )
    geometry.computeBoundingSphere()

    mesh = THREE.LineSegments( geometry, material )
    mesh.position.x -= 1200
    mesh.position.y -= 1200

    parent_node = THREE.Object3D()
    parent_node.add(mesh)

    scene.add( parent_node )

    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    return renderer


def animate():
    render()


def render():
    global mesh, renderer, parent_node
    time = datetime.now().timestamp() * 0.1

    parent_node.rotation.z = time * 0.5

    renderer.render( scene, camera )


def reshape(width, height):
    """window reshape callback."""
    global camera, renderer

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    glViewport(0, 0, width, height)


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()


def keyboard(c, x=0, y=0):
    """keyboard callback."""

    if c == b'q':
        sys.exit(0)

    glutPostRedisplay()


"""
"""


def main(argv=None):
    global renderer, camera, scene

    renderer = init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
