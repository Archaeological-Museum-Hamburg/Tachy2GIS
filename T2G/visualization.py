import vtk
from qgis.core import QgsFeature, QgsGeometry

from random import random
from .AnchorUpdater import VtkAnchorUpdater

COLOUR_SPACE = ['blanched_almond',
                'blue_medium',
                'flesh_ochre',
                'turquoise_dark',
                'cadmium_lemon',
                'sky_blue_light',
                'permanent_red_violet',
                'slate_grey_dark',
                'deep_pink',
                'olive_drab',
                'cinnabar_green',
                'manganese_blue',
                'saddle_brown',
                ]


class ColourProvider:
    index = 0
    colours = COLOUR_SPACE

    def next(self):
        self.index +=1
        if self.index > len(self.colours):
            return vtk.vtkColour3D(random(), random(), random())
        else:
            return COLOUR_SPACE[self.index]

class VtkGeometry:
    POLYGON = 1006
    MULTIPOLYGONZM = 3006


class VtkLayer:
    def __init__(self, qgs_layer):
        self.source_layer = qgs_layer
        self.id = self.source_layer.id()
        self.extractor = VtkAnchorUpdater(layer=self.source_layer)
        self.anchors = self.extractor.anchors
        self.geometries = self.extractor.geometries

    def update(self, dialog):
        self.extractor.signalAnchorCount.connect(dialog.setAnchorCount)
        self.extractor.signalAnchorProgress.connect(dialog.anchorProgress)
        self.extractor.signalGeometriesProgress.connect(dialog.geometriesProgress)
        # dialog.show()
        self.extractor.startExtraction()

    def make_wkt(self, vertices):
        raise NotImplementedError("Vtk layers have to implement this for each type of geometry")

    def insert_geometry(self, vertices):
        raise NotImplementedError("Vtk layers have to implement this for each type of geometry")

    def add_feature(self, vertices, iface):
        feat = QgsFeature()
        geom = QgsGeometry.fromWkt(self.make_wkt(vertices))
        feat.setGeometry(geom)
        feat.setFields(self.source_layer.fields())

        if iface.openFeatureForm(self.source_layer, feat, False):
            print('Feature added')
            self.insert_geometry(vertices)


class VtkPolyLayer(VtkLayer):
    def make_wkt(self, vertices):
        # wkt requires the first vertex to coincide with the last:
        if len(vertices) < 3 and vertices[-1] != vertices[0]:
            vertices.append(vertices[0])
        vertexts = [vertex.get_coordinates() for vertex in vertices]
        wkt = 'POLYGONZ(({0}))'.format(', '.join(vertexts))
        return wkt

    def insert_geometry(self, vertices):
        point_index = self.extractor.anchors.GetNumberOfPoints() + 1
        new_poly = vtk.vtkPolygon()
        for vertex in vertices:
            new_poly.GetPointIds().InsertNextId(point_index)
            point_index += 1
            self.extractor.anchors.InsertNextPoint(*vertex.get_coordinates())
        self.extractor.polies.InsertNextCell(new_poly)



