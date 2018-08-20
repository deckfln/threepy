"""
    /**
     * @author bhouston / http://clara.io
     * @author WestLangley / http://github.com/WestLangley
     */
"""
import math
from THREE.Vector3 import *
from THREE.Sphere import *


class Box3:
    def __init__(self, min=None, max=None ):
        self.min = min
        if min is None:
            self.min = Vector3(float('+inf'), float('+inf'), float('+inf'))
        self.max = max
        if max is None:
            self.max = Vector3(float('-inf'), float('-inf'), float('-inf'))

        self.isBox3 = True

    def set(self, min, max ):
        self.min.copy( min )
        self.max.copy( max )

        return self

    def setFromArray(self, array ):
        minX = float('+inf')
        minY = float('+inf')
        minZ = float('+inf')

        maxX = float('-inf')
        maxY = float('-inf')
        maxZ = float('-inf')

        for i in range(0, array.length,3 ):
            x = array[ i ]
            y = array[ i + 1 ]
            z = array[ i + 2 ]

            if x < minX: minX = x
            if y < minY: minY = y
            if z < minZ: minZ = z

            if x > maxX: maxX = x
            if y > maxY: maxY = y
            if z > maxZ: maxZ = z

        self.min.set( minX, minY, minZ )
        self.max.set( maxX, maxY, maxZ )

        return self

    def setFromBufferAttribute(self, attribute ):
        minX = float('+inf')
        minY = float('+inf')
        minZ = float('+inf')

        maxX = float('-inf')
        maxY = float('-inf')
        maxZ = float('-inf')

        for i in range(0, len(attribute.array) - 2, attribute.itemSize):
            x = attribute.array[i]
            y = attribute.array[i + 1]
            z = attribute.array[i + 2]

            if x < minX: minX = x
            if y < minY: minY = y
            if z < minZ: minZ = z

            if x > maxX: maxX = x
            if y > maxY: maxY = y
            if z > maxZ: maxZ = z

        self.min.set( minX, minY, minZ )
        self.max.set( maxX, maxY, maxZ )

        return self

    def setFromPoints(self, points ):
        self.makeEmpty()

        for point in points:
            self.expandByPoint( point )

        return self

    def setFromCenterAndSize(self, center, size):
        v1 = Vector3()

        halfSize = v1.copy( size ).multiplyScalar( 0.5 )

        self.min.copy( center ).sub( halfSize )
        self.max.copy( center ).add( halfSize )

        return self

    def setFromObject(self, object ):
        self.makeEmpty()
        return self.expandByObject( object )

    def clone(self):
        return type(self)().copy( self )

    def copy(self, box ):
        self.min.copy( box.min )
        self.max.copy( box.max )

        return self

    def makeEmpty(self):
        self.min.np[0] = self.min.np[1] = self.min.np[2] = float('+inf')
        self.max.np[0] = self.max.np[1] = self.max.np[2] = float('-inf')

        return self

    def isEmpty(self):
        # // self is a more robust check for empty than ( volume <= 0 ) because volume can get positive with two negative axes
        return ( self.max.x < self.min.x ) or ( self.max.y < self.min.y ) or ( self.max.z < self.min.z )

    def getCenter(self, target):
        if self.isEmpty():
            return target.set( 0, 0, 0 )
        return target.addVectors( self.min, self.max ).multiplyScalar( 0.5 )

    def getSize(self, target):
        if self.isEmpty():
            return target.set( 0, 0, 0 )
        return target.subVectors( self.max, self.min )

    def expandByPoint(self, point ):
        self.min.min( point )
        self.max.max( point )

        return self

    def expandByVector(self, vector ):
        self.min.sub( vector )
        self.max.add( vector )

        return self

    def expandByScalar(self, scalar ):
        self.min.addScalar( - scalar )
        self.max.addScalar( scalar )

        return self

    def expandByObject(self, object):
        # // Computes the world-axis-aligned bounding box of an object (including its children),
        #// accounting for both the object's, and children's, world transforms

        object.updateMatrixWorld( True )

        # TODO: FDE fix it in python
        def _traverse_box3(node, scope):
            v1 = Vector3()
            geometry = node.geometry
            if geometry is not None:
                if geometry.my_class(isGeometry):
                    vertices = geometry.vertices
                    for vertice in vertices:
                        v1.copy(vertice)
                        v1.applyMatrix4(node.matrixWorld)
                        scope.expandByPoint(v1)
                elif geometry.my_class(isBufferGeometry):
                    attribute = geometry.attributes.position
                    if attribute is not None:
                        for i in range(attribute.count):
                            v1.fromBufferAttribute(attribute, i).applyMatrix4(node.matrixWorld)
                            self.expandByPoint(v1)

        object.traverse( _traverse_box3, self)

        return self

    def containsPoint(self, point ):
        # TODO: FDE recheck this
        return point.x < self.min.x or point.x > self.max.x or\
            point.y < self.min.y or point.y > self.max.y or\
            point.z < self.min.z or point.z > self.max.z

    def containsBox(self, box ):
            return self.min.x <= box.min.x and box.max.x <= self.max.x and\
                self.min.y <= box.min.y and box.max.y <= self.max.y and\
                self.min.z <= box.min.z and box.max.z <= self.max.z

    def getParameter(self, point, target):
        # // This can potentially have a divide by zero if the box
        # // has a size dimension of 0.

        return target.set(
            ( point.x - self.min.x ) / ( self.max.x - self.min.x ),
            ( point.y - self.min.y ) / ( self.max.y - self.min.y ),
            ( point.z - self.min.z ) / ( self.max.z - self.min.z )
        )

    def intersectsBox(self, box ):
        # // using 6 splitting planes to rule out intersections.
        # TODO FDE recheck it
        return box.max.x < self.min.x or box.min.x > self.max.x or\
            box.max.y < self.min.y or box.min.y > self.max.y or\
            box.max.z < self.min.z or box.min.z > self.max.z

    def intersectsSphere(self, sphere):
            closestPoint = Vector3()
            # // Find the point on the AABB closest to the sphere center.
            self.clampPoint( sphere.center, closestPoint )

            # // If that point is inside the sphere, the AABB and sphere intersect.
            return closestPoint.distanceToSquared( sphere.center ) <= ( sphere.radius * sphere.radius )

    def intersectsPlane(self, plane ):
        # // We compute the minimum and maximum dot product values. If those values
        # // are on the same side (back or front) of the plane, then there is no intersection.
        if plane.normal.x > 0:

            min = plane.normal.x * self.min.x
            max = plane.normal.x * self.max.x
        else:
            min = plane.normal.x * self.max.x
            max = plane.normal.x * self.min.x

        if plane.normal.y > 0:
            min += plane.normal.y * self.min.y
            max += plane.normal.y * self.max.y
        else:
            min += plane.normal.y * self.max.y
            max += plane.normal.y * self.min.y

        if plane.normal.z > 0:
            min += plane.normal.z * self.min.z
            max += plane.normal.z * self.max.z
        else:
            min += plane.normal.z * self.max.z
            max += plane.normal.z * self.min.z

        return ( min <= plane.constant and max >= plane.constant )

    def intersectsTriangle( self, triangle):
        # triangle centered vertices
        v0 = Vector3()
        v1 = Vector3()
        v2 = Vector3()

        # triangle edge vectors
        f0 = Vector3()
        f1 = Vector3()
        f2 = Vector3()

        testAxis = Vector3()

        center = Vector3()
        extents = Vector3()

        triangleNormal = Vector3()

        def satForAxes( axes ):
            j = axes.length - 3
            for i in range(0, j, 3):
                testAxis.fromArray( axes, i )
                # project the aabb onto the seperating axis
                r = extents.x * abs( testAxis.x ) + extents.y * abs( testAxis.y ) + extents.z * abs( testAxis.z )
                # project all 3 vertices of the triangle onto the seperating axis
                p0 = v0.dot( testAxis )
                p1 = v1.dot( testAxis )
                p2 = v2.dot( testAxis )
                # actual test, basically see if either of the most extreme of the triangle points intersects r
                if max( - max( p0, p1, p2 ), min( p0, p1, p2 ) ) > r:
                    # points of the projected triangle are outside the projected half-length of the aabb
                    # the axis is seperating and we can exit
                    return False

                return True

        if self.isEmpty():
            return False

        # compute box center and extents
        self.getCenter( center )
        extents.subVectors( self.max, center )

        # translate triangle to aabb origin
        v0.subVectors( triangle.a, center )
        v1.subVectors( triangle.b, center )
        v2.subVectors( triangle.c, center )

        # compute edge vectors for triangle
        f0.subVectors( v1, v0 )
        f1.subVectors( v2, v1 )
        f2.subVectors( v0, v2 )

        # test against axes that are given by cross product combinations of the edges of the triangle and the edges of the aabb
        # make an axis testing of each of the 3 sides of the aabb against each of the 3 sides of the triangle = 9 axis of separation
        # axis_ij = u_i x f_j (u0, u1, u2 = face normals of aabb = x,y,z axes vectors since aabb is axis aligned)
        axes = [
            0, - f0.z, f0.y, 0, - f1.z, f1.y, 0, - f2.z, f2.y,
            f0.z, 0, - f0.x, f1.z, 0, - f1.x, f2.z, 0, - f2.x,
            - f0.y, f0.x, 0, - f1.y, f1.x, 0, - f2.y, f2.x, 0
        ]
        if not satForAxes( axes ):
            return False

        # test 3 face normals from the aabb
        axes = [ 1, 0, 0, 0, 1, 0, 0, 0, 1 ]
        if not satForAxes( axes ):
            return False

        # finally testing the face normal of the triangle
        # use already existing triangle edge vectors here
        triangleNormal.crossVectors( f0, f1 )
        axes = [ triangleNormal.x, triangleNormal.y, triangleNormal.z ]
        return satForAxes( axes )

    def clampPoint(self, point, optionalTarget=None ):
        result = optionalTarget or Vector3()
        return result.copy( point ).clamp( self.min, self.max )

    def distanceToPoint(self, point):
        v1 = Vector3()
        clampedPoint = v1.copy( point ).clamp( self.min, self.max )
        return clampedPoint.sub( point ).length()

    def getBoundingSphere(self, target):
        v1 = Vector3()
        self.getCenter( target.center )
        target.radius = self.getSize( v1 ).length() * 0.5
        return target

    def intersect(self, box ):
        self.min.max( box.min )
        self.max.min( box.max )

        # // ensure that if there is no overlap, the result is fully empty, not slightly empty with non-inf/+inf values that will cause subsequence intersects to erroneously return valid values.
        if self.isEmpty():
            self.makeEmpty()

        return self

    def union(self, box ):
        self.min.min( box.min )
        self.max.max( box.max )

        return self

    def applyMatrix4(self, matrix):
        # // transform of empty box is an empty box.
        if self.isEmpty():
            return self

        m = matrix.elements

        xax = m[0] * self.min.x
        xay = m[1] * self.min.x
        xaz = m[2] * self.min.x
        xbx = m[0] * self.max.x
        xby = m[1] * self.max.x
        xbz = m[2] * self.max.x
        yax = m[4] * self.min.y
        yay = m[5] * self.min.y
        yaz = m[6] * self.min.y
        ybx = m[4] * self.max.y
        yby = m[5] * self.max.y
        ybz = m[6] * self.max.y
        zax = m[8] * self.min.z
        zay = m[9] * self.min.z
        zaz = m[10] * self.min.z
        zbx = m[8] * self.max.z
        zby = m[9] * self.max.z
        zbz = m[10] * self.max.z

        self.min.x = min(xax, xbx) + min(yax, ybx) + min(zax, zbx) + m[12]
        self.min.y = min(xay, xby) + min(yay, yby) + min(zay, zby) + m[13]
        self.min.z = min(xaz, xbz) + min(yaz, ybz) + min(zaz, zbz) + m[14]
        self.max.x = max(xax, xbx) + max(yax, ybx) + max(zax, zbx) + m[12]
        self.max.y = max(xay, xby) + max(yay, yby) + max(zay, zby) + m[13]
        self.max.z = max(xaz, xbz) + max(yaz, ybz) + max(zaz, zbz) + m[14]

        return self

    def translate(self, offset ):
        self.min.add( offset )
        self.max.add( offset )

        return self

    def equals(self, box ):
        return box.min.equals( self.min ) and box.max.equals( self.max )