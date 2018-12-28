"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author bhouston / http://clara.io
 */
"""
from THREE.math.Plane import *
from THREE.objects.BoundingSphere import *

from THREE.cython.cFrustum import cFrustum_intersectsSphere

_cython = True

_p = Vector3()
_sphere = BoundingSphere()


class Frustum:
    def __init__(self, p0=None, p1=None, p2=None, p3=None, p4=None, p5=None ):
        self.planes = [
            p0 if p0 else Plane(),
            p1 if p1 else Plane(),
            p2 if p2 else Plane(),
            p3 if p3 else Plane(),
            p4 if p4 else Plane(),
            p5 if p5 else Plane(),
        ]
        self.updated = True        # was the frustum updated since the last frame
        self._cache = {}            # if the frusturm was not updated and the object were not updated,
                                    # pick the intersection from the cache
        self.visible_spheres = []
        self.invisible_spheres = []

    def is_updated(self):
        u = self.updated
        self.updated = False
        return u

    def set(self, p0, p1, p2, p3, p4, p5 ):
        planes = self.planes

        planes[ 0 ].copy( p0 )
        planes[ 1 ].copy( p1 )
        planes[ 2 ].copy( p2 )
        planes[ 3 ].copy( p3 )
        planes[ 4 ].copy( p4 )
        planes[ 5 ].copy( p5 )

        self.updated = True
        return self

    def clone(self):
        return type(self)().copy( self )

    def copy(self, frustum ):
        planes = self.planes

        for i in range(6):
            planes[ i ].copy( frustum.planes[ i ] )

        self.updated = True
        return self

    def setFromMatrix(self, m ):
        planes = self.planes

        # only update the frustum if the camera moved since last frame
        if m.is_updated():
            me = m.elements
            me0 = me[ 0 ]; me1 = me[ 1 ]; me2 = me[ 2 ]; me3 = me[ 3 ]
            me4 = me[ 4 ]; me5 = me[ 5 ]; me6 = me[ 6 ]; me7 = me[ 7 ]
            me8 = me[ 8 ]; me9 = me[ 9 ]; me10 = me[ 10 ]; me11 = me[ 11 ]
            me12 = me[ 12 ]; me13 = me[ 13 ]; me14 = me[ 14 ]; me15 = me[ 15 ]

            planes[ 0 ].setComponents( me3 - me0, me7 - me4, me11 - me8, me15 - me12 ).normalize()
            planes[ 1 ].setComponents( me3 + me0, me7 + me4, me11 + me8, me15 + me12 ).normalize()
            planes[ 2 ].setComponents( me3 + me1, me7 + me5, me11 + me9, me15 + me13 ).normalize()
            planes[ 3 ].setComponents( me3 - me1, me7 - me5, me11 - me9, me15 - me13 ).normalize()
            planes[ 4 ].setComponents( me3 - me2, me7 - me6, me11 - me10, me15 - me14 ).normalize()
            planes[ 5 ].setComponents( me3 + me2, me7 + me6, me11 + me10, me15 + me14 ).normalize()
            self.updated = True

        return self

    def reset_visible_spheres(self):
        self.visible_spheres.clear()
        self.invisible_spheres.clear()

    @staticmethod
    def optimize_spheres(sphere, r, spheres):
        # the _sphere is entirely visible
        # extrapolate the biggest visible sphere from it center
        new_sphere = Sphere(sphere.center.clone(), r)

        # optimize the spheres (check if some are included in others)
        for i in range(len(spheres) - 1, -1, -1):
            s = spheres[i]

            if s.isIncludedIn(new_sphere):
                del spheres[i]

        spheres.append(new_sphere)

        spheres.sort(key=lambda sphere: sphere.radius, reverse=True)

    def intersectsObject(self, object):
        geometry = object.geometry

        # only compute the intersection if
        #   the camera moved
        #   or the object moved
        #   or the object is not yet in the cache
        if self.updated or object.matrixWorld.updated or object.id not in self._cache:
            if geometry.boundingSphere is None:
                geometry.computeBoundingSphere()

            _sphere.copy( geometry.boundingSphere )
            _sphere.applyMatrix4( object.matrixWorld )

            # check if the object is in an existing visible sphere
            found = False
            for s in self.visible_spheres:
                if _sphere.isIncludedIn(s):
                    self._cache[object.id] = 1
                    found = True
                    break

            if not found:
                # check if the object is in an existing invisible sphere
                for s in self.invisible_spheres:
                    if _sphere.isIncludedIn(s):
                        self._cache[object.id] = -1
                        found = True
                        break

                if not found:
                    r = self.intersectsSphere(_sphere)

                    if r >= 0:
                        self.optimize_spheres(_sphere, r, self.visible_spheres)
                    else:
                        self.optimize_spheres(_sphere, -r, self.invisible_spheres)

                    self._cache[object.id] = r

            self._cache[object.id] = self.intersectsSphere( _sphere)
        return self._cache[object.id] >= 0

    def intersectsOctree(self, octree):
        # only compute the intersection if
        #   the camera moved
        #   or the object moved
        #   or the object is not yet in the cache
        if self.updated or octree.matrixWorld.is_updated() or octree.id not in self._cache:
            _sphere.copy(octree.boundingSphere)
            self._cache[octree.id] = self.intersectsSphereOctree(_sphere)

        return self._cache[octree.id]

    def intersectsSphereOctree(self, sphere ):
        """
        Optimization based on http://blog.bwhiting.co.uk/?p=355
        :param sphere:
        :return:
        """
        planes = self.planes
        center = sphere.center
        negRadius = - sphere.radius

        for p in range(6):

            plane = planes[p]
            distance = plane.distanceToPoint( center )

            if distance < negRadius:
                return -1
            elif distance < sphere.radius:
                return 0

        return 1

    def intersectsSprite(self, sprite):
        sphere = _sphere

        sphere.center.set( 0, 0, 0 )
        sphere.radius = 0.7071067811865476
        sphere.applyMatrix4( sprite.matrixWorld )

        return self.intersectsSphere( sphere )

    def intersectsSphere(self, sphere):
        global _cython

        if False:
            return cFrustum_intersectsSphere(self.planes, sphere)
        else:
            return self._intersectsSphere(sphere)

    def _intersectsSphere(self, sphere ):
        """
        Optimization based on http://blog.bwhiting.co.uk/?p=355
        :param sphere:
        :return:
        """
        planes = self.planes
        center = sphere.center
        negRadius = - sphere.radius

        shortest = float("+inf")    # shortest distance to a plance
                                    # equivalent to the biggest entirely visible sphere
        for p in range(6):
            plane = planes[p]
            distance = plane.distanceToPoint( center )

            if distance < negRadius:
                return distance

            if distance < shortest:
                shortest = distance

        return shortest

    def intersectsBox(self, box):
        planes = self.planes

        for i in range(6):
            plane = planes[ i ]

            # corner at max distance
            _p.x = box.max.x if plane.normal.x > 0 else box.min.x
            _p.y = box.max.y if plane.normal.y > 0 else box.min.y
            _p.z = box.max.z if plane.normal.z > 0 else box.min.z

            if plane.distanceToPoint( _p ) < 0:
                return False

        return True

    def containsPoint(self, point ):
        planes = self.planes

        for i in range(6):
            if planes[ i ].distanceToPoint( point ) < 0:
                return False

        return True
