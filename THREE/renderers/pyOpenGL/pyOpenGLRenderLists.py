"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


def _painter(a):
    ro = (0 if a.renderOrder is None else a.renderOrder) * 10000
    pi = ( a.program.id if a.program else 0) * 1000
    mi = a.material.id * 100
    az = (0 if a.z is None else a.z) * 10
    ai = (0 if a.id is None else a.id)
    return ro + pi + mi + az + ai


def _painterSortStable( a, b ):
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


def _reversePainterSortStable( a, b ):
    if a.renderOrder != b.renderOrder:
        return a.renderOrder - b.renderOrder

    if a.z != b.z:
        return b.z - a.z

    else:
        return a.id - b.id


class RenderItem:
    def __init__(self, id, object, geometry, material, program, renderOrder, z, group):
        self.id = id
        self.object = object
        self.geometry = geometry
        self.material = material
        self.program = program
        self.renderOrder = renderOrder
        self.z = z
        self.group = group
        self.instance = False


class pyOpenGLRenderList:
    def __init__(self):
        self.renderItems = []
        self.renderItemsIndex = 0

        self.opaque = []
        self.opaq = {}
        self.transparent = []
        self.transp = {}

    def init(self):
        self.renderItemsIndex = 0

        self.opaque.clear()
        self.opaq.clear()
        self.transparent.clear()
        self.transp.clear()

    def push(self, object, geometry, material, z, group):
        if len(self.renderItems) > self.renderItemsIndex:
            renderItem = self.renderItems[self.renderItemsIndex]
            renderItem.id = object.id
            renderItem.object = object
            renderItem.geometry = geometry
            renderItem.material = material
            renderItem.program = material.program
            renderItem.renderOrder = object.renderOrder
            renderItem.z = z
            renderItem.group = group
        else:
            renderItem = RenderItem(object.id, object, geometry, material, material.program, object.renderOrder, z, group)
            self.renderItems.append(renderItem)

        dedup = "%d.%d" % (geometry.id, material.id)

        if material.transparent:
            self.transparent.append(renderItem)
            if dedup in self.transp:
                self.transp[dedup].append(renderItem)
            else:
                self.transp[dedup] = [renderItem]
        else:
            self.opaque.append(renderItem)
            if dedup in self.opaq:
                self.opaq[dedup].append(renderItem)
            else:
                self.opaq[dedup] = [renderItem]

        self.renderItemsIndex += 1

    def sort(self, opaque, transparent):
        if len(opaque) > 1:
            opaque.sort(key=_painter, reverse=True)
        if len(transparent) > 1:
            transparent.sort(key=_painter, reverse=True)


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
