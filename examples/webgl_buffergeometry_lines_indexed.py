"""
        <title>three.js webgl - buffergeometry - lines - indexed</title>
"""        
import math
import random
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mesh = None
        self.parent_node = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 2750

    p.scene = THREE.Scene()

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

    p.mesh = THREE.LineSegments( geometry, material )
    p.mesh.position.x -= 1200
    p.mesh.position.y -= 1200

    p.parent_node = THREE.Object3D()
    p.parent_node.add(p.mesh)

    p.scene.add( p.parent_node )

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    time = datetime.now().timestamp()

    p.parent_node.rotation.z = time * 0.5

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
