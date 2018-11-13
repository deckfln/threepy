"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

from THREE.core.Object3D import *


class Scene(Object3D):
    isScene = True

    def __init__(self):
        super().__init__( )

        self.type = 'Scene'

        self.background = None
        self.fog = None
        self.overrideMaterial = None
        self.instances = {}

        self.autoUpdate = True      # // checked by the renderer

    def copy(self, source, recursive=True ):
        super().copy( source, recursive )

        if source.background:
            self.background = source.background.clone()
        if source.fog:
            self.fog = source.fog.clone()
        if source.overrideMaterial:
            self.overrideMaterial = source.overrideMaterial.clone()

        self.autoUpdate = source.autoUpdate
        self.matrixAutoUpdate = source.matrixAutoUpdate

        return self

    def toJSON(self, meta=None ):
        data = super().toJSON( meta )

        if self.background:
            data.object.background = self.background.toJSON( meta )
        if self.fog:
            data.object.fog = self.fog.toJSON()

        return data

