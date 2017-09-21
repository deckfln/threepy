"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


def painterSortStable( a, b ):

    if a.renderOrder != b.renderOrder:
        return a.renderOrder - b.renderOrder

    elif a.program and b.program and a.program != b.program:
        return a.program.id - b.program.id

    elif a.material.id != b.material.id:
        return a.material.id - b.material.id

    elif a.z != b.z:
        return a.z - b.z

    else:
        return a.id - b.id


def reversePainterSortStable( a, b ):
    if a.renderOrder != b.renderOrder:
        return a.renderOrder - b.renderOrder

    if a.z != b.z:
        return b.z - a.z

    else:
        return a.id - b.id


class _renderItem:
    def __init__(self, id, object, geometry, material, program, renderOrder, z, group):
        self.id = id
        self.object = object
        self.geometry = geometry
        self.material = material
        self.program = program
        self.renderOrder = renderOrder
        self.z = z
        self.group = group


class pyOpenGLRenderList:
    def __init__(self):
        self.renderItems = []
        self.renderItemsIndex = 0

        self.opaque = []
        self.transparent = []

    def init(self):
        self.renderItemsIndex = 0

        self.opaque.length = 0
        self.transparent.length = 0

    def push(self, object, geometry, material, z, group ):
        if self.renderItemsIndex in self.renderItems:
            renderItem = self.renderItems[ self.renderItemsIndex ]
            renderItem.id = object.id
            renderItem.object = object
            renderItem.geometry = geometry
            renderItem.material = material
            renderItem.program = material.program
            renderItem.renderOrder = object.renderOrder
            renderItem.z = z
            renderItem.group = group
        else:
            renderItem = _renderItem(object.id, object, geometry, material, material.program, object.renderOrder, z, group)
            self.renderItems[ self.renderItemsIndex ] = renderItem

        if material.transparent:
            self.transparent.append(renderItem)
        else:
            self.opaque.append( renderItem )

        self.renderItemsIndex += 1

    def sort(self):
        if len(self.opaque) > 1:
            self.opaque.sort(key=painterSortStable)
        if len(self.transparent) > 1:
            self.transparent.sort(key=reversePainterSortStable)


class pyOpenGLRenderLists:
    def __init__(self):
        self.lists = {}

    def get(self, scene, camera ):
        hash = "%d,%d" % (scene.id, camera.id)
        
        if hash not in self.lists:
            # // console.log( 'THREE.WebGLRenderLists:', hash )

            list = pyOpenGLRenderList()
            self.lists[ hash ] = list
        else:
            list = self.lists[ hash ]

        return list

    def dispose(self):
        self.lists = {}
