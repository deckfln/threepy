"""
/**
 * @author tschw
 */
"""

from THREE.math.Plane import *
from THREE.renderers.pyOpenGL.pyOpenGLUniforms import *

class pyOpenGLClipping:
    def __init__(self):
        self.globalState = None
        self.numGlobalPlanes = 0
        self.localClippingEnabled = False
        self.renderingShadows = False

        self.uniform = Uniform({ 'value': None, 'needsUpdate': False })

        self.numPlanes = 0
        self.numIntersection = 0

    def init(self, planes, enableLocalClipping, camera ):
        enabled = len(planes) != 0  or enableLocalClipping or self.numGlobalPlanes != 0 or self.localClippingEnabled
            # // enable state of previous frame - the clipping code has to
            # // run another frame in order to reset the state:

        self.localClippingEnabled = enableLocalClipping

        self.globalState = self.projectPlanes( planes, camera, 0 )
        self.numGlobalPlanes = len(planes)

        return enabled

    def beginShadows(self):
        self.renderingShadows = True
        self.projectPlanes( )

    def endShadows(self):
        self.renderingShadows = False
        self.resetGlobalState()

    def setState(self, planes, clipIntersection, clipShadows, camera, cache, fromCache ):
        if not self.localClippingEnabled or planes is None or len(planes) == 0 or self.renderingShadows and not clipShadows:
            # // there's no local clipping

            if self.renderingShadows:
                # // there's no global clipping
                self.projectPlanes( )
            else:
                self.resetGlobalState()
        else:
            nGlobal = 0 if self.renderingShadows else self.numGlobalPlanes
            lGlobal = nGlobal * 4

            dstArray = cache.clippingState

            self.uniform.value = dstArray # // ensure unique state

            dstArray = self.projectPlanes( planes, camera, lGlobal, fromCache )

            for i in range(lGlobal):
                dstArray[ i ] = self.globalState[ i ]

            cache.clippingState = dstArray
            self.numIntersection = self.numPlanes if clipIntersection else 0
            self.numPlanes += nGlobal

    def resetGlobalState(self):
        if self.globalState and (self.uniform.value is None or self.uniform.value != self.globalState):
            self.uniform.value = self.globalState
            self.uniform.needsUpdate = self.numGlobalPlanes > 0

        self.numPlanes = self.numGlobalPlanes
        self.numIntersection = 0

    def projectPlanes(self, planes=None, camera=None, dstOffset=0, skipTransform=False ):
        nPlanes = len(planes) if planes else 0
        dstArray = None

        if nPlanes != 0:
            dstArray = self.uniform.value
            if skipTransform != True or dstArray is None:
                flatSize = dstOffset + nPlanes * 4
                viewMatrix = camera.matrixWorldInverse

                viewNormalMatrix = Matrix3().getNormalMatrix( viewMatrix )

                if dstArray is None or len(dstArray) < flatSize:
                    dstArray = np.zeros(flatSize, 'f' )

                i4 = dstOffset
                for i in range(nPlanes):
                    plane = Plane().copy( planes[ i ] ).applyMatrix4( viewMatrix, viewNormalMatrix )

                    plane.normal.toArray( dstArray, i4 )
                    dstArray[ i4 + 3 ] = plane.constant

                    i4 += 4

            self.uniform.value = dstArray
            self.uniform.needsUpdate = True

        self.numPlanes = nPlanes
        
        return dstArray