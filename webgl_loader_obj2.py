"""
        <title>three.js webgl - OBJLoader2</title>
"""
import sys
import os

import THREE
from THREE.controls.TrackballControls import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.loaders.OBJLoader2 import *
from THREE.loaders.MTLLoader import *


class _camera:
        def __init__(self):
            self.posCamera = THREE.Vector3(0.0, 175.0, 500.0)
            self.posCameraTarget = THREE.Vector3(0, 0, 0)
            self.near = 0.1
            self.far = 10000
            self.fov = 45


class OBJLoader2Example:

    def __init__(self):
        self.renderer = None
        self.container = None
        self.aspectRatio = 1

        self.scene = None
        self.cameraDefaults = _camera()

        self.camera = None
        self.cameraTarget = self.cameraDefaults.posCameraTarget

        self.controls = None

        self.flatShading = False
        self.doubleSide = False

        self.cube = None
        self.pivot = None

        self.feedbackArray = [10]

    def initGL (self):
        self.container = pyOpenGL(self)
        self.container.addEventListener('resize', self.resizeDisplayGL, False)
        self.renderer = THREE.pyOpenGLRenderer({'antialias': True})
        self.recalcAspectRatio()

        self.scene = THREE.Scene()
        self.scene.background = THREE.Color( 0x050505 )

        self.camera = THREE.PerspectiveCamera( self.cameraDefaults.fov, self.aspectRatio, self.cameraDefaults.near, self.cameraDefaults.far )
        self.resetCamera()
        self.controls = TrackballControls( self.camera, self.container )

        ambientLight = THREE.AmbientLight( 0x404040 )
        directionalLight1 = THREE.DirectionalLight( 0xC0C090 )
        directionalLight2 = THREE.DirectionalLight( 0xC0C090 )

        directionalLight1.position.set( -100, -50, 100 )
        directionalLight2.position.set( 100, 50, -100 )

        self.scene.add( directionalLight1 )
        self.scene.add( directionalLight2 )
        self.scene.add( ambientLight )

        helper = THREE.GridHelper( 1200, 60, 0xFF4444, 0x404040 )
        self.scene.add( helper )

        geometry = THREE.BoxGeometry( 10, 10, 10 )
        material = THREE.MeshNormalMaterial()
        self.cube = THREE.Mesh( geometry, material )
        self.cube.position.set( 0, 0, 0 )
        self.scene.add( self.cube )

        self.pivot = THREE.Object3D()
        self.pivot.name = 'Pivot'
        self.scene.add( self.pivot )

    def Validator(self):
         OBJLoader2._getValidator()

    def initPostGL (self):
        return True

    def loadObj (self, objDef ):
        self.scene.add( objDef.pivot )
        scope = self
        scope._reportProgress( 'Loading: ' + objDef.fileObj, objDef.instanceNo )

        def onLoad(materials):
            materials.preload()

            scope.pivot.add(objDef.pivot)
            objLoader = OBJLoader2()
            objLoader.setSceneGraphBaseNode(objDef.pivot)
            objLoader.setMaterials(materials.materials)
            objLoader.setPath(objDef.path)
            objLoader.setDebug(False, False)

            def onProgress(event):
                if event.lengthComputable:
                    percentComplete = event.loaded / event.total * 100
                    output = 'Download of "' + objDef.fileObj + '": ' + round(percentComplete) + '%'
                    scope._reportProgress(output, objDef.instanceNo)

            def onError(event):
                output = 'Error of type "' + event.type + '" occurred when trying to load: ' + event.src
                scope._reportProgress(output, objDef.instanceNo)

            def onSuccess(object3d):
                print('Loading complete. Meshes were attached to: %s' % object3d.name)

            scope._reportProgress('', objDef.instanceNo)

            objLoader.load(objDef.fileObj, onSuccess, onProgress, onError)

        if objDef.fileMtl is not None:
            mtlLoader = MTLLoader()
            mtlLoader.setPath( objDef.texturePath )
            mtlLoader.setCrossOrigin( 'anonymous' )
            mtlLoader.load( objDef.fileMtl, onLoad)
        else:
            onLoad(MaterialCreator())

    def _reportProgress(self, text, instanceNo ):
        self.feedbackArray.append(text)
        print( 'Progress: ' + text )

    def resizeDisplayGL (self, event=None, app=None):
        self.controls.handleResize(window.innerWidth, window.innerHeight)

        self.recalcAspectRatio()
        self.renderer.setSize( window.innerWidth, window.innerHeight, False )

        self.updateCamera()

    def recalcAspectRatio (self):
        self.aspectRatio = window.innerWidth / window.innerHeight

    def resetCamera (self):
        self.camera.position.copy( self.cameraDefaults.posCamera )
        self.cameraTarget.copy( self.cameraDefaults.posCameraTarget )

        self.updateCamera()

    def updateCamera (self):
        self.camera.aspect = self.aspectRatio
        self.camera.lookAt( self.cameraTarget )
        self.camera.updateProjectionMatrix()

    def render (self, app=None):
        if not self.renderer.autoClear:
            self.renderer.clear()

        self.controls.update()

        self.cube.rotation.x += 0.05
        self.cube.rotation.y += 0.05

        self.renderer.render( self.scene, self.camera )

    def scopetraversal(self, material):
        material.flatShading = scope.flatShading
        material.needsUpdate = True

    def alterShading (self):
        scope = self
        scope.flatShading = not scope.flatShading
        print( 'Enabling flat shading' if scope.flatShading else 'Enabling smooth shading')

        def scopeTraverse (object3d ):
            scope.traverseScene( object3d )

        scope.pivot.traverse( scopeTraverse )

    def alterDouble (self):
        scope = self
        scope.doubleSide = not scope.doubleSide
        print( 'Enabling DoubleSide materials' if scope.doubleSide else 'Enabling FrontSide materials')

        def scopetraversal(material ):
            material.side = THREE.DoubleSide if scope.doubleSide else THREE.FrontSide

        def scopeTraverse (object3d ):
            scope.traverseScene( object3d )

        scope.pivot.traverse( scopeTraverse )

    def traverseScene (self, object3d ):
        if isinstance(object3d.material, THREE.MultiMaterial ):
            materials = object3d.material.materials
            for name in materials:
                if hasattr(materials, 'name' ):
                    self.traversal( materials[ name ] )

        elif object3d.material:
            self.traversal( object3d.material )


def onWindowResize(event, app):
    app.resizeDisplayGL()


class _loadObj:
    def __init__(self, path, file, pivot, texturePath=None, fileMtl=None, instance=0):
        self.path = path
        self.fileObj = file
        self.pivot = pivot
        self.instanceNo = instance
        self.texturePath = texturePath
        self.fileMtl = fileMtl


def main(argv=None):
    app = OBJLoader2Example()

    app.initGL()
    app.resizeDisplayGL()
    app.initPostGL()

    pivotA = THREE.Object3D()
    pivotA.name = 'PivotA'
    pivotA.position.set(-50, 0, 0)
    app.loadObj(_loadObj('obj/female02/', 'female02_vertex_colors.obj', pivotA))

    pivotB = THREE.Object3D()
    pivotB.name = 'PivotB'
    pivotB.position.set(50, 0, 0)
    app.loadObj(_loadObj('obj/female02/', 'female02.obj',  pivotB, 'obj/female02/', 'female02.mtl', 1))

    app.container.addEventListener('animationRequest', app.render)
    return app.container.loop()


if __name__ == "__main__":
    sys.exit(main())
