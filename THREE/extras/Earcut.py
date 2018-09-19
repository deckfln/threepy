"""
 * @author Mugen87 / https:#github.com/Mugen87
 * Port from https:#github.com/mapbox/earcut (v2.1.2)
"""


class Node:
    def __init__(self, i, x, y):
        # vertice index in coordinates array
        self.i = i

        # vertex coordinates
        self.x = x
        self.y = y

        # previous and next vertice nodes in a polygon ring
        self.prev = None
        self.next = None

        # z-order curve value
        self.z = None

        # previous and next nodes in z-order
        self.prevZ = None
        self.nextZ = None

        # indicates whether self is a steiner point
        self.steiner = False


def triangulate(data, holeIndices, dim=2):
    hasHoles = holeIndices and len(holeIndices)
    outerLen = holeIndices[ 0 ] * dim if hasHoles else len(data)
    outerNode = linkedList(data, 0, outerLen, dim, True)
    triangles = []

    if not outerNode:
        return triangles

    if hasHoles:
        outerNode = eliminateHoles(data, holeIndices, outerNode, dim)

    # if the shape is not too simple, we'll use z-order curve hash later; calculate polygon bbox
    minX = minY = invSize = None

    if len(data) > 80 * dim:
        minX = maxX = data[ 0 ]
        minY = maxY = data[ 1 ]

        for i in range(dim, outerLen, dim):
            x = data[ i ]
            y = data[ i + 1 ]
            if x < minX:
                minX = x
            if y < minY:
                minY = y
            if x > maxX:
                maxX = x
            if y > maxY:
                maxY = y

        # minX, minY and invSize are later used to transform coords into integers for z-order calculation

        invSize = max(maxX - minX, maxY - minY)
        invSize = 1 / invSize if invSize != 0 else 0

    earcutLinked(outerNode, triangles, dim, minX, minY, invSize)

    return triangles

    
def linkedList(data, start, end, dim, clockwise):
    """
    # create a circular doubly linked list from polygon points in the specified winding order
    """
    last = None
    if clockwise == (signedArea(data, start, end, dim) > 0):
        for i in range(start, end, dim):
            last = insertNode(i, data[ i ], data[ i + 1 ], last)

    else:
        for i in range(end - dim, start - 1, -dim):
            last = insertNode(i, data[ i ], data[ i + 1 ], last)

    if last and nequals(last, last.next):
        removeNode(last)
        last = last.next

    return last


def filterPoints(start, end=None):
    """
    # eliminate colinear or duplicate points
    """
    if not start:
        return start
    if not end: 
        end = start

    p = start

    while True:
        again = False

        if not p.steiner and (nequals(p, p.next) or area(p.prev, p, p.next) == 0):
            removeNode(p)
            p = end = p.prev
            if p == p.next:
                break
            again = True

        else:
            p = p.next

        if not again or p == end:
            break

    return end


def earcutLinked(ear, triangles, dim, minX, minY, invSize, pass1 = None):
    """
    # main ear slicing loop which triangulates a polygon (given as a linked list)
    """
    if not ear:
        return

    # interlink polygon nodes in z-order

    if not pass1 and invSize:
        indexCurve(ear, minX, minY, invSize)

    stop = ear

    # iterate through ears, slicing them one by one

    while ear.prev != ear.next:
        prev = ear.prev
        next = ear.next
        
        t =  isEarHashed(ear, minX, minY, invSize) if invSize else isEar(ear)
        if t:
            # cut off the triangle
            triangles.append(int(prev.i / dim))
            triangles.append(int(ear.i / dim))
            triangles.append(int(next.i / dim))

            removeNode(ear)

            # skipping the next vertice leads to less sliver triangles
            ear = next.next
            stop = next.next

            continue

        ear = next

        # if we looped through the whole remaining polygon and can't find any more ears

        if ear == stop:
            # try filtering points and slicing again
            if pass1 is None:
                earcutLinked(filterPoints(ear), triangles, dim, minX, minY, invSize, 1)

                # if self didn't work, try curing all small self-intersections locally

            elif pass1 == 1:
                ear = cureLocalIntersections(ear, triangles, dim)
                earcutLinked(ear, triangles, dim, minX, minY, invSize, 2)

            # as a last resort, try splitting the remaining polygon into two

            elif pass1 == 2:
                splitEarcut(ear, triangles, dim, minX, minY, invSize)

            break


def isEar(ear):
    """
    # check whether a polygon node forms a valid ear with adjacent nodes
    """
    a = ear.prev
    b = ear
    c = ear.next

    if area(a, b, c) >= 0:
        return False     # reflex, can't be an ear

    # now make sure we don't have other points inside the potential ear
    p = ear.next.next

    while p != ear.prev:
        if pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and area(p.prev, p, p.next) >= 0:
            return False

        p = p.next

    return True


def isEarHashed(ear, minX, minY, invSize):
    a = ear.prev
    b = ear
    c = ear.next

    if area(a, b, c) >= 0:
        return False     # reflex, can't be an ear

    # triangle bbox; min & max are calculated like self for speed

    minTXa = a.x if a.x < c.x else c.x
    minTXb = b.x if b.x < c.x else c.x
    minTX = minTXa if a.x < b.x else minTXb
    
    minTYa = a.y if a.y < c.y else c.y
    minTYb = b.y if b.y < c.y else c.y
    minTY = minTYa if a.y < b.y else minTYb
    
    maxTXa = a.x if a.x > c.x else c.x
    maxTXb = b.x if b.x > c.x else c.x
    maxTX = maxTXa if a.x > b.x else maxTXb
    
    maxTYa = a.y if a.y > c.y else c.y
    maxTYb = b.y if b.y > c.y else c.y
    maxTY = maxTYa if a.y > b.y else maxTYb

    # z-order range for the current triangle bbox

    minZ = zOrder(minTX, minTY, minX, minY, invSize)
    maxZ = zOrder(maxTX, maxTY, minX, minY, invSize)

    # first look for points inside the triangle in increasing z-order

    p = ear.nextZ

    while p and p.z <= maxZ:
        if p != ear.prev and p != ear.next and \
            pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and \
            area(p.prev, p, p.next) >= 0:
                return False
        p = p.nextZ

    # then look for points in decreasing z-order

    p = ear.prevZ

    while p and p.z >= minZ:
        if p != ear.prev and p != ear.next and \
            pointInTriangle(a.x, a.y, b.x, b.y, c.x, c.y, p.x, p.y) and \
            area(p.prev, p, p.next) >= 0:
                return False

        p = p.prevZ

    return True


def cureLocalIntersections(start, triangles, dim):
    """
    # go through all polygon nodes and cure small local self-intersections
    """
    p = start

    while True:
        a = p.prev
        b = p.next.next

        if not nequals(a, b) and intersects(a, p, p.next, b) and locallyInside(a, b) and locallyInside(b, a):
            triangles.append(a.i / dim)
            triangles.append(p.i / dim)
            triangles.append(b.i / dim)

            # remove two nodes involved

            removeNode(p)
            removeNode(p.next)

            p = start = b

        p = p.next

        if p == start:
            break

    return p


def splitEarcut(start, triangles, dim, minX, minY, invSize):
    """
    # try splitting polygon into two and triangulate them independently
    """
    # look for a valid diagonal that divides the polygon into two

    a = start

    while True:
        b = a.next.next

        while b != a.prev:
            if a.i != b.i and isValidDiagonal(a, b):
                # split the polygon in two by the diagonal
                c = splitPolygon(a, b)

                # filter colinear points around the cuts
                a = filterPoints(a, a.next)
                c = filterPoints(c, c.next)

                # run earcut on each half
                earcutLinked(a, triangles, dim, minX, minY, invSize)
                earcutLinked(c, triangles, dim, minX, minY, invSize)
                return

            b = b.next

        a = a.next

        if a == start:
            break


def eliminateHoles(data, holeIndices, outerNode, dim):
    """
    # link every hole into the outer loop, producing a single-ring polygon without holes
    """
    queue = []

    l = len(holeIndices)
    for i in range(l):
        start = holeIndices[ i ] * dim
        end = holeIndices[ i + 1 ] * dim if i < l - 1 else len(data)
        list1 = linkedList(data, start, end, dim, False)
        if list1 == list1.next:
            list1.steiner = True
        queue.append(getLeftmost(list1))

    queue = sorted(queue, key=compareX)

    # process holes from left to right

    for q in queue:
        eliminateHole(q, outerNode)
        outerNode = filterPoints(outerNode, outerNode.next)

    return outerNode


def compareX(a):
    return a.x


def eliminateHole(hole, outerNode):
    """
    # find a bridge between vertices that connects hole with an outer ring and and link it
    """
    outerNode = findHoleBridge(hole, outerNode)

    if outerNode :
        b = splitPolygon(outerNode, hole)

        filterPoints(b, b.next)


def findHoleBridge(hole, outerNode):
    """
    # David Eberly's algorithm for finding a bridge between hole and outer polygon
    """
    p = outerNode
    hx = hole.x
    hy = hole.y
    qx = float("-Inf")

    # find a segment intersected by a ray from the hole's leftmost point to the left
    # segment's endpoint with lesser x will be potential connection point

    m = None
    while True:
        if p.next.y <= hy <= p.y and p.next.y != p.y:
            x = p.x + (hy - p.y) * (p.next.x - p.x) / (p.next.y - p.y)

            if qx < x <= hx:
                qx = x

                if x == hx:
                    if hy == p.y:
                        return p
                    if hy == p.next.y:
                        return p.next

                m = p if p.x < p.next.x else p.next

        p = p.next

        if p == outerNode:
            break

    if not m:
        return None

    if hx == qx:
        return m.prev     # hole touches outer segment; pick lower endpoint

    # look for points inside the triangle of hole point, segment intersection and endpoint
    # if there are no points found, we have a valid connection
    # otherwise choose the point of the minimum angle with the ray as connection point

    stop = m
    mx = m.x
    my = m.y
    tanMin = float("Inf")

    p = m.next

    while p != stop:
        if hx >= p.x >= mx and hx != p.x and \
            pointInTriangle(hx if hy < my else qx, hy, mx, my, qx if hy < my else hx, hy, p.x, p.y):
            tan = abs(hy - p.y) / (hx - p.x)     # tangential

            if (tan < tanMin or (tan == tanMin and p.x > m.x)) and locallyInside(p, hole):
                m = p
                tanMin = tan

        p = p.next

    return m


def indexCurve(start, minX, minY, invSize):
    """
    # interlink polygon nodes in z-order
    """
    p = start

    while True:
        if p.z is None:
            p.z = zOrder(p.x, p.y, minX, minY, invSize)
            
        p.prevZ = p.prev
        p.nextZ = p.next
        p = p.next

        if p == start:
            break

    p.prevZ.nextZ = None
    p.prevZ = None

    sortLinked(p)


def sortLinked(list1):
    """
    # Simon Tatham's linked list merge sort algorithm
    # http:#www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.html
    """
    inSize = 1

    while True:
        p = list1
        list1 = None
        tail = None
        numMerges = 0

        while p:
            numMerges += 1
            q = p
            pSize = 0

            for i in range(inSize):
                pSize += 1
                q = q.nextZ
                if not q:
                    break

            qSize = inSize

            while pSize > 0 or (qSize > 0 and q):
                if pSize != 0 and (qSize == 0 or not q or p.z <= q.z):
                    e = p
                    p = p.nextZ
                    pSize -= 1
                else:
                    e = q
                    q = q.nextZ
                    qSize -= 1

                if tail:
                    tail.nextZ = e
                else:
                    list1 = e

                e.prevZ = tail
                tail = e

            p = q

        tail.nextZ = None
        inSize *= 2

        if numMerges <= 1:
            break
    
    return list1


def zOrder(x, y, minX, minY, invSize):
    """
    # z-order of a point given coords and inverse of the longer side of data bbox
    """
    # coords are transformed into non-negative 15-bit integer range

    x = int(32767 * (x - minX) * invSize)
    y = int(32767 * (y - minY) * invSize)

    x = (x | (x << 8)) & 0x00FF00FF
    x = (x | (x << 4)) & 0x0F0F0F0F
    x = (x | (x << 2)) & 0x33333333
    x = (x | (x << 1)) & 0x55555555

    y = (y | (y << 8)) & 0x00FF00FF
    y = (y | (y << 4)) & 0x0F0F0F0F
    y = (y | (y << 2)) & 0x33333333
    y = (y | (y << 1)) & 0x55555555

    return x | (y << 1)


def getLeftmost(start):
    """
    # find the leftmost node of a polygon ring
    """
    p = start
    leftmost = start

    while True:
        if p.x < leftmost.x:
            leftmost = p
        p = p.next
        if p == start:
            break

    return leftmost


def pointInTriangle(ax, ay, bx, by, cx, cy, px, py):
    """
    # check if a point lies within a convex triangle
    """
    return (cx - px) * (ay - py) - (ax - px) * (cy - py) >= 0 and \
     (ax - px) * (by - py) - (bx - px) * (ay - py) >= 0 and \
     (bx - px) * (cy - py) - (cx - px) * (by - py) >= 0


def isValidDiagonal(a, b):
    """
    # check if a diagonal between two polygon nodes is valid (lies in polygon interior)
    """
    return a.next.i != b.i and a.prev.i != b.i and not intersectsPolygon(a, b) and \
        locallyInside(a, b) and locallyInside(b, a) and middleInside(a, b)


def area(p, q, r):
    """
    # signed area of a triangle
    """
    return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)


def nequals(p1: Node, p2: Node):
    """
    # check if two points are equal
    """
    return p1.x == p2.x and p1.y == p2.y


def intersects(p1, q1, p2, q2):
    """
    # check if two segments intersect
    """
    if (nequals(p1, q1) and nequals(p2, q2)) or \
            (nequals(p1, q2) and nequals(p2, q1)):
            return True

    return area(p1, q1, p2) > 0 != area(p1, q1, q2) > 0 and \
                 area(p2, q2, p1) > 0 != area(p2, q2, q1) > 0


def intersectsPolygon(a, b):
    """
    # check if a polygon diagonal intersects any polygon segments
    """
    p = a

    while True:
        if p.i != a.i and p.next.i != a.i and p.i != b.i and p.next.i != b.i and \
            intersects(p, p.next, a, b) :
            return True

        p = p.next

        if p == a:
            break

    return False


def locallyInside(a, b):
    """
    # check if a polygon diagonal is locally inside the polygon
    """
    if area(a.prev, a, a.next) < 0:
        return area(a, b, a.next) >= 0
        
    
    return area(a, b, a.prev) < 0 or area(a, a.next, b) < 0


def middleInside(a, b):
    """
    # check if the middle point of a polygon diagonal is inside the polygon
    """
    p = a
    inside = False
    px = (a.x + b.x) / 2
    py = (a.y + b.y) / 2

    while True:
        if ((p.y > py) != (p.next.y > py)) and p.next.y != p.y and \
                        (px < (p.next.x - p.x) * (py - p.y) / (p.next.y - p.y) + p.x):
            inside = not inside

        p = p.next

        if p == a:
            break

    return inside


def splitPolygon(a, b):
    """
    # link two polygon vertices with a bridge; if the vertices belong to the same ring, it splits polygon into two
    # if one belongs to the outer ring and another to a hole, it merges it into a single ring
    """
    a2 = Node(a.i, a.x, a.y)
    b2 = Node(b.i, b.x, b.y)
    an = a.next
    bp = b.prev

    a.next = b
    b.prev = a

    a2.next = an
    an.prev = a2

    b2.next = a2
    a2.prev = b2

    bp.next = b2
    b2.prev = bp

    return b2


def insertNode(i, x, y, last):
    """
    # create a node and optionally link it with previous one (in a circular doubly linked list)
    """
    p = Node(i, x, y)

    if not last :
        p.prev = p
        p.next = p
    else:
        p.next = last.next
        p.prev = last
        last.next.prev = p
        last.next = p

    return p


def removeNode(p):
    p.next.prev = p.prev
    p.prev.next = p.next

    if p.prevZ:
        p.prevZ.nextZ = p.nextZ
    if p.nextZ:
        p.nextZ.prevZ = p.prevZ


def signedArea(data, start, end, dim):
    sum = 0

    j = end - dim
    for i in range(start, end, dim):
        sum += (data[ j ] - data[ i ]) * (data[ i + 1 ] + data[ j + 1 ])
        j = i

    return sum
