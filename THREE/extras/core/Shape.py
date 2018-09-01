"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 * Defines a 2d shape plane using paths.
 **/

# // STEP 1 Create a path.
# // STEP 2 Turn path into shape.
# // STEP 3 ExtrudeGeometry takes in Shape/Shapes
# // STEP 3a - Extract points from each shape, turn to vertices
# // STEP 3b - Triangulate each shape, add faces.
"""
from THREE.extras.core.Path import *
import THREE.extras.ShapeUtils as ShapeUtils
import THREE._Math as _Math


class Shape(Path):
    def __init__(self, pts=None):
        super().__init__(pts )
        self.uuid = _Math.generateUUID()

        self.type = 'Shape'
        self.holes = []

    def getPointsHoles(self, divisions ):
        holesPts = [None for i in range(len(self.holes))]

        for i in range(len(self.holes)):
            holesPts[ i ] = self.holes[ i ].getPoints( divisions )

        return holesPts

    # // Get points of shape and holes (keypoints based on segments parameter)

    def extractAllPoints(self, divisions ):
        return {
            'shape': self.getPoints( divisions ),
            'holes': self.getPointsHoles( divisions )
        }

    def extractPoints(self, divisions ):
        return self.extractAllPoints( divisions )

    def copy(self, source):
        super().copy(source)

        self.holes = []

        for hole in source.holes:
            self.holes.append( hole.clone() )

        return self

    def toJSON(self):
        data = super().toJSON()

        data['uuid'] = self.uuid
        data['holes'] = []

        for hole in self.holes:
            data['holes'].append( hole.toJSON() )

        return data

    def fromJSON(self, json):
        super().fromJSON(json)

        self.uuid = json['uuid']
        self.holes = []

        for hole in json['holes']:
            self.holes.append( Path().fromJSON( hole ) )

        return self

