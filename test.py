#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
07-attrib.py

OpenGL 2.0 rendering using vertex attributes

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""


# imports ####################################################################

import sys

from math import exp, modf
from time import time
from ctypes import sizeof, c_float, c_void_p, c_uint, c_uint16

from OpenGL.GLUT import *
from OpenGL.GL import *

import THREE as THREE
from THREE import *

# shader
vert_shader = """
uniform mat4 transformationMatrix;

varying vec4 fragmentColor;

void main() {
    gl_Position = projectionMatrix * viewMatrix * transformationMatrix * vec4(position, 1.);
//    gl_TexCoord[0] = gl_TextureMatrix[0] * vec4(tex_coord, 1.);
    
    fragmentColor = vec4(color, 1.);
}
    """
    
frag_shader = """
const float alpha_threshold = .55;

varying vec4 fragmentColor;
        
void main() {
    
    vec4 color = fragmentColor;
    gl_FragColor = color;
}
    """
    
# object #####################################################################

def flatten(*lll):
    return [u for ll in lll for l in ll for u in l]

def flatten1(*lll):
    return [l for ll in lll for l in ll]

uint_size = sizeof(c_uint)
uint16_size = sizeof(c_uint16)
float_size = sizeof(c_float)

# display ####################################################################


def screen_shot(name="screen_shot.png"):
    """window screenshot."""
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    
    import png
    png.write(open(name, "wb"), width, height, 3, data)


def reshape(width, height):
    """window reshape callback."""
    glViewport(0, 0, width, height)
    
#    glMatrixMode(GL_PROJECTION)
#    glLoadIdentity()
#    radius = .5 * min(width, height)
#    w, h = width/radius, height/radius
#    if perspective:
#       glFrustum(-w, w, -h, h, 8, 16)
#        glTranslate(0, 0, -12)
#        glScale(1.5, 1.5, 1.5)
#    else:
#        glOrtho(-w, w, -h, h, -2, 2)
    
#    glMatrixMode(GL_MODELVIEW)
#    glLoadIdentity()


def display():
    """window redisplay callback."""
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    draw_object()
    glutSwapBuffers()


# interaction ################################################################

PERSPECTIVE, LIGHTING, TEXTURING = b'p', b'l', b't'

perspective = False
lighting = False
texturing = False


def keyboard(c, x=0, y=0):
    """keyboard callback."""
    global perspective, lighting, texturing
    
    if c == PERSPECTIVE:
        perspective = not perspective
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    
    elif c == LIGHTING:
        lighting = not lighting
        glUniform1i(locations[b"lighting"], lighting)
    
    elif c == TEXTURING:
        texturing = not texturing
        glUniform1i(locations[b"texturing"], texturing)
        if texturing:
            animate_texture()
    
    elif c == b's':
        screen_shot()
    
    elif c == b'q':
        sys.exit(0)
    glutPostRedisplay()


rotating = False
scaling = False

rotation = THREE.Quaternion()
scale = 1.


def screen2space(x, y):
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    radius = min(width, height)*scale
    return (2.*x-width)/radius, -(2.*y-height)/radius


def mouse(button, state, x, y):
    global rotating, scaling, x0, y0
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)
    x0, y0 = x, y


def motion(x1, y1):
    global x0, y0, rotation, scale
    if rotating:
        p0 = screen2space(x0, y0)
        p1 = screen2space(x1, y1)
        # TODO
        # rotation = q.product(rotation, q.arcball(*p0), q.arcball(*p1))
        rotation._x += 0.01
        
    if scaling:
        scale *= exp(((x1-x0)-(y1-y0))*.01)
    x0, y0 = x1, y1
    glutPostRedisplay()


###########################


###########################

scene = None
cube = None
renderer = None
camera = None


def render():
    global renderer, scene, camera, cube
    renderer.prepare()
    renderer.render(scene, camera)
    glutSwapBuffers()


def update():
    global cube

    cube.rotation.x += 0.001
    cube.rotation.y += 0.001

    cube.updateMatrix()
    cube.updateMatrixWorld()
    render()


class pyOpenGLShadowMap:
    def __init__(self):
        self.enabled = False
        self.type = 0


class RenderTarget:
    def __init__(self):
        self.texture = None


# main #######################################################################


def main(argv=None):
    global renderer, camera, scene,cube

    if argv is None:
        argv = sys.argv

    renderer = Renderer(None, reshape, render, keyboard, mouse, motion, update)

    width, height = renderer.screen_size()

    scene = THREE.Scene()

    camera = THREE.PerspectiveCamera(45, width/height, 0.1, 20000)
    camera.position = THREE.Vector3(0, 0, 5)

    bgcube = THREE.BoxBufferGeometry(1, 1, 1, 1, 1, 1)
    colors = []
    for i in range(int(bgcube.attributes.position.count)):
        p = THREE.Vector3(bgcube.attributes.position.getX(i), bgcube.attributes.position.getY(i), bgcube.attributes.position.getZ(i))
        colors.extend([p.x+0.5, p.y+0.5, p.z+0.5])
    bgcube.addAttribute('color', Float32BufferAttribute(colors, 3))

    """
    material = THREE.ShaderMaterial({
        'vertexShader': vert_shader,
        'fragmentShader': frag_shader,
        'vertexColors': THREE.VertexColors,
        'uniforms': {
            'transformationMatrix': {'type': "m4", 'value': 0}
        }
    })
    material.uniforms.transformationMatrix.value = cube.matrixWorld
    #    material = THREE.MeshBasicMaterial({'color': 0xffff00})
    """
    texture = THREE.TextureLoader().load("crate.jpg")

    material = THREE.MeshPhongMaterial({'color': 0x7777ff,
                                          'map': texture
                                          })

    cube = THREE.Mesh(bgcube, material)
    scene.add(cube)

    groundGeom = THREE.PlaneBufferGeometry(100, 100, 4, 4)
    groundMesh = THREE.Mesh(groundGeom, THREE.MeshBasicMaterial({'color': 0x555555}))
    groundMesh.rotation.x = -math.pi / 2
    groundMesh.position.y = -5
    scene.add(groundMesh)

    # // add subtle ambient lighting var
    ambientLight = THREE.AmbientLight(0x0c0c0c)
    scene.add(ambientLight)

    # // add spotlight for the shadows
    spotLight = THREE.SpotLight(0xffffff)
    spotLight.position.set(-30, 60, 60)
    spotLight.castShadow = True
    scene.add(spotLight)

    # renderer.build(camera, cube)

    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())