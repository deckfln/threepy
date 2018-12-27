#!/usr/bin/python
"""
Octree implementation
https://github.com/jcummings2/pyoctree/blob/master/octree.py
FIXME: if all objects are at position 0,0,0 the octree will recurse forever !!!!
"""
# From: https://code.google.com/p/pynastran/source/browse/trunk/pyNastran/general/octree.py?r=949
#       http://code.activestate.com/recipes/498121-python-octree-implementation/

# UPDATED:
# Is now more like a true octree (ie: partitions space containing objects)

# Important Points to remember:
# The OctNode positions do not correspond to any object position
# rather they are seperate containers which may contain objects
# or other nodes.

# An OctNode which which holds less objects than MAX_OBJECTS_PER_CUBE
# is a LeafNode; it has no branches, but holds a list of objects contained within
# its boundaries. The list of objects is held in the leafNode's 'data' property

# If more objects are added to an OctNode, taking the object count over MAX_OBJECTS_PER_CUBE
# Then the cube has to subdivide itself, and arrange its objects in the new child nodes.
# The new octNode itself contains no objects, but its children should.

from __future__ import print_function


from THREE.math.Frustum import *
from THREE.scenes.Scene import *


_OctNodeIds = 0
_vector3 = Vector3()


class OctNode(object):
    """
    New Octnode Class, can be appended to as well i think
    """
    def __init__(self, position, size, depth, data):
        """
        OctNode Cubes have a position and size
        position is related to, but not the same as the objects the node contains.
        Branches (or children) follow a predictable pattern to make accesses simple.
        Here, - means less than 'origin' in that dimension, + means greater than.
        branch: 0 1 2 3 4 5 6 7
        x:      - - - - + + + +
        y:      - - + + - - + +
        z:      - + - + - + - +
        """
        global _OctNodeIds
        self.id = _OctNodeIds
        _OctNodeIds += 1

        self.position = position
        self.matrixWorld = Matrix4().makeTranslation(position.x, position.y, position.z)
        self.size = size
        self.depth = depth
        s = size/2
        self.boundingSphere = BoundingSphere(position, math.sqrt(s**2 + s**2))

        # All OctNodes will be leaf nodes at first
        # Then subdivided later as more objects get added
        self.isLeafNode = True

        # store our object, typically this will be one, but maybe more
        self.data = data

        # might as well give it some emtpy branches while we are here.
        self.branches = [None, None, None, None, None, None, None, None]

        half = size / 2

        # The cube's bounding coordinates
        self.lower = Vector3(position.x - half, position.y - half, position.z - half)
        self.upper = Vector3(position.x + half, position.y + half, position.z + half)

    def __str__(self):
        data_str = u", ".join((str(x) for x in self.data))
        return u"position: {0}, size: {1}, depth: {2} leaf: {3}, data: {4}".format(
            self.position, self.size, self.depth, self.isLeafNode, data_str
        )

    def delete(self):
        for branch in self.branches:
            if branch is not None:
                branch.delete()
                del branch


class Octree(object):
    """
    The octree itself, which is capable of adding and searching for nodes.
    """
    def __init__(self, worldSize, origin=Vector3(0, 0, 0), max_type="nodes", max_value=10):
        """
        Init the world bounding root cube
        all world geometry is inside this
        it will first be created as a leaf node (ie, without branches)
        this is because it has no objects, which is less than MAX_OBJECTS_PER_CUBE
        if we insert more objects into it than MAX_OBJECTS_PER_CUBE, then it will subdivide itself.
        """
        self.root = OctNode(origin, worldSize, 0, [])
        self.worldSize = worldSize
        self.limit_nodes = (max_type == "nodes")
        self.limit = max_value
        self.data = {}      # all objects stored in the octree

    @staticmethod
    def CreateNode(position, size, objects):
        """This creates the actual OctNode itself."""
        return OctNode(position, size, objects, [])

    def update(self, scene: Scene):
        while not self.__update(scene):
            # ohhh my god, the world is not big enough
            # delete everything and rebuild a new but bigger
            new_root = OctNode(self.root.position, self.worldSize, 0, [])
            self.root.delete()
            del self.root
            self.root = new_root

    def __update(self, obj3d: Object3D):
        if obj3d.my_class(isMesh | isLine | isPoints):
            if obj3d.matrixWorld.updated:
                if obj3d in self.data:
                    node = self.data[obj3d]
                    if node and node.data and obj3d in node.data:
                        node.data.remove(obj3d)

                # real position of the object in world
                _vector3.set(obj3d.matrixWorld.elements[12],
                            obj3d.matrixWorld.elements[13],
                            obj3d.matrixWorld.elements[14])
                err = self.insertNode(_vector3, obj3d)
                if err is None:
                    # ohhh my god, the world is not big enough
                    m = max(abs(_vector3.x), max(abs(_vector3.y), abs(_vector3.z)))
                    self.worldSize = m * 2 * 1.5
                    self.data[obj3d] = None
                    return False

        for i in obj3d.children:
            if i.visible:
                if not self.__update(i):
                    return False

        return True

    def insertNode(self, position, objData=None):
        """
        Add the given object to the octree if possible
        Parameters
        ----------
        position : array_like with 3 elements
            The spatial location for the object
        objData : optional
            The data to store at this position. By default stores the position.
            If the object does not have a position attribute, the object
            itself is assumed to be the position.
        Returns
        -------
        node : OctNode or None
            The node in which the data is stored or None if outside the
            octree's boundary volume.
        """
        if position.less_than(self.root.lower):
            return None
        if position.greater_than(self.root.upper):
            return None

        if objData is None:
            objData = position

        return self.__insertNode(self, self.root, self.root.size, self.root, position, objData, 0)

    def __insertNode(self, octree, root, size, parent, position, objData, depth):
        """Private version of insertNode() that is called recursively"""
        if root is not None:
            isLeafNode = root.isLeafNode

        if root is None:
            # we're inserting a single object, so if we reach an empty node, insert it here
            # Our new node will be a leaf with one object, our object
            # More may be added later, or the node maybe subdivided if too many are added
            # Find the Real Geometric centre point of our new node:
            # Found from the position of the parent node supplied in the arguments
            pos = parent.position

            # offset is halfway across the size allocated for this node
            offset = size / 2

            # find out which direction we're heading in
            branch = self.__findBranch(parent, position)

            # new center = parent position + (branch direction * offset)
            newCenter = (0, 0, 0)

            if branch == 0:
                newCenter = Vector3(pos.x - offset, pos.y - offset, pos.z - offset )
            elif branch == 1:
                newCenter = Vector3(pos.x - offset, pos.y - offset, pos.z + offset )
            elif branch == 2:
                newCenter = Vector3(pos.x - offset, pos.y + offset, pos.z - offset )
            elif branch == 3:
                newCenter = Vector3(pos.x - offset, pos.y + offset, pos.z + offset )
            elif branch == 4:
                newCenter = Vector3(pos.x + offset, pos.y - offset, pos.z - offset )
            elif branch == 5:
                newCenter = Vector3(pos.x + offset, pos.y - offset, pos.z + offset )
            elif branch == 6:
                newCenter = Vector3(pos.x + offset, pos.y + offset, pos.z - offset )
            elif branch == 7:
                newCenter = Vector3(pos.x + offset, pos.y + offset, pos.z + offset )

            # Now we know the centre point of the new node
            # we already know the size as supplied by the parent node
            # So create a new node at this position in the tree
            # print "Adding Node of size: " + str(size / 2) + " at " + str(newCenter)
            node = OctNode(newCenter, size, parent.depth + 1, [objData])
            octree.data[objData] = node

            return node

        # else: are we not at our position, but not at a leaf node either
        elif (
            not isLeafNode
            and
            (
                not root.position.equals(position)
            )
        ):

            # we're in an octNode still, we need to traverse further
            branch = self.__findBranch(root, position)
            # Find the new scale we working with
            newSize = root.size / 2
            # Perform the same operation on the appropriate branch recursively
            root.branches[branch] = self.__insertNode(octree, root.branches[branch], newSize, root, position, objData, depth+1)

        # else, is this node a leaf node with objects already in it?
        elif isLeafNode:
            # We've reached a leaf node. This has no branches yet, but does hold
            # some objects, at the moment, this has to be less objects than MAX_OBJECTS_PER_CUBE
            # otherwise this would not be a leafNode (elementary my dear watson).
            # if we add the node to this branch will we be over the limit?
            if (
                (self.limit_nodes and len(root.data) < self.limit)
                or
                (not self.limit_nodes and root.depth >= self.limit)
            ):
                # No? then Add to the Node's list of objects and we're done
                root.data.append(objData)
                octree.data[objData] = root
                #return root
            else:
                # Adding this object to this leaf takes us over the limit
                # So we have to subdivide the leaf and redistribute the objects
                # on the new children.
                # Add the new object to pre-existing list
                root.data.append(objData)
                # copy the list
                objList = root.data
                # Clear this node's data
                root.data = None
                # It is not a leaf node anymore
                root.isLeafNode = False
                # Calculate the size of the new children
                newSize = root.size / 2
                # distribute the objects on the new tree
                # print "Subdividing Node sized at: " + str(root.size) + " at " + str(root.position)
                branches = root.branches
                for ob in objList:
                    # Use the position attribute of the object if possible
                    _vector3.set(ob.matrixWorld.elements[12],
                                 ob.matrixWorld.elements[13],
                                 ob.matrixWorld.elements[14])

                    branch = self.__findBranch(root, _vector3)
                    root.branches[branch] = self.__insertNode(octree, branches[branch], newSize, root, _vector3, ob, depth+1)
        return root

    def findPosition(self, position):
        """
        Basic lookup that finds the leaf node containing the specified position
        Returns the child objects of the leaf, or None if the leaf is empty or none
        """
        if position.less_than(self.root.lower):
            return None
        if position.greater_than(self.root.upper):
            return None
        return self.__findPosition(self.root, position)

    @staticmethod
    def __findPosition(node, position, count=0, branch=0):
        """Private version of findPosition """
        if node.isLeafNode:
            #print("The position is", position, " data is", node.data)
            return node.data
        branch = Octree.__findBranch(node, position)
        child = node.branches[branch]
        if child is None:
            return None
        return Octree.__findPosition(child, position, count + 1, branch)

    @staticmethod
    def __findBranch(root, position):
        """
        helper function
        returns an index corresponding to a branch
        pointing in the direction we want to go
        """
        index = 0
        r = root.position.np
        p = position.np

        if p[0] >= r[0]:
            index |= 4
        if p[1] >= r[1]:
            index |= 2
        if p[2] >= r[2]:
            index |= 1
        return index

    def iterateDepthFirst(self):
        """Iterate through the octree depth-first"""
        gen = self.__iterateDepthFirst(self.root)
        for n in gen:
            yield n

    @staticmethod
    def __iterateDepthFirst(root):
        """Private (static) version of iterateDepthFirst"""

        for branch in root.branches:
            if branch is None:
                continue
            for n in Octree.__iterateDepthFirst(branch):
                yield n
            if branch.isLeafNode:
                yield branch

    def get_visible_data(self, frustum: Frustum, data):
        self.__get_visible_data(self.root, frustum, data)

    @staticmethod
    def __get_visible_data(node: OctNode, frustum: Frustum, datas: list):
        visibility = frustum.intersectsOctree(node)
        if visibility < 0:
            # completely outside of the frustrum
            # drop all objets here
            return

        elif visibility > 0:
            # completely inside the frustrum
            # send back all the objects
            Octree.__get_data(node, datas)
            return

        else:
            # partialy in the frustrum
            if node.isLeafNode:
                # for leaf, test each object individually
                for child in node.data:
                    if child.visible and frustum.intersectsObject(child):
                        datas.append(child)

            else:
                # for branch, continue testing down
                for branch in node.branches:
                    if branch is not None:
                        Octree.__get_visible_data(branch, frustum, datas)

    @staticmethod
    def __get_data(node: OctNode, datas: list):
        if node.isLeafNode:
            datas.extend(node.data)
        else:
            for branch in node.branches:
                if branch is not None:
                    Octree.__get_data(branch, datas)
