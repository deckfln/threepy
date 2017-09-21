import THREE.UniformsUtils as UniformsUtils
import THREE._Math as _Math
from THREE.RootObject import *
from THREE.Constants import *
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Vector4 import *
from THREE.Quaternion import *
from THREE.Matrix4 import *
from THREE.Matrix3 import *
from THREE.Plane import *
from THREE.Euler import *
from THREE.Layers import *
from THREE.Sphere import *
from THREE.Box3 import *
from THREE.Frustum import *
from THREE.pyOpenGLAttributes import *
from THREE.BufferGeometry import *
from THREE.BoxBufferGeometry import *
from THREE.BufferAttribute import *
from THREE.Color import *
from THREE.Object3D import *
from THREE.Camera import *
from THREE.ShaderChunk import *
from THREE.Material import *
from THREE.ShaderMaterial import *
from THREE.MeshBasicMaterial import *
from THREE.Face3 import *
from THREE.Mesh import *
from THREE.Scene import *
from THREE.pyOpenGLProperties import *
from THREE.pyOpenGLClipping import *
from THREE.pyOpenGLStates import *
from THREE.pyOpenGLLights import *
from THREE.pyOpenGLGeometries import *
from THREE.pyOpenGLBufferRenderer import *
from THREE.pyOpenGLIndexedBufferRenderer import *
from THREE.pyOpenGLObjects import *
from THREE.pyOpenGLRenderLists import *
from THREE.Uniforms import *
from THREE.pyOpenGL import *
from THREE.pyOpenGLProgram import *
from THREE.pyOpenGLPrograms import *
from THREE.pyOpenGLRenderer import *


global ShaderLib

"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""


def arrayMax(array):
    if len(array) == 0:
        return float('-inf')

    m = array[0]

    for i in range(len(array)):
        if array[i] > m:
            m = array[i]

    return m
