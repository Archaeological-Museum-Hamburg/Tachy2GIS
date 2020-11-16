import vtk
from qgis.core import QgsFeature, QgsGeometry
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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
        self.index += 1
        if self.index > len(self.colours) - 1:
            return vtk.vtkColor3d(random(), random(), random())
        else:
            return vtk.vtkNamedColors().GetColor3d(COLOUR_SPACE[self.index])


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

    def get_actors(self, colour):
        #poly_data = self.anchor_updater.layer_cache[self.source_layer.id]['poly_data']
        poly_data = self.extractor.layer_cache[self.source_layer.id()]['poly_data']

        poly_mapper = vtk.vtkPolyDataMapper()
        tri_filter = vtk.vtkTriangleFilter()
        tri_filter.SetInputData(poly_data)
        tri_filter.Update()

        # use vtkFeatureEdges for Boundary rendering
        featureEdges = vtk.vtkFeatureEdges()
        featureEdges.SetColoring(0)
        featureEdges.BoundaryEdgesOn()
        featureEdges.FeatureEdgesOff()
        featureEdges.ManifoldEdgesOff()
        featureEdges.NonManifoldEdgesOff()
        featureEdges.SetInputData(poly_data)
        featureEdges.Update()

        edgeMapper = vtk.vtkPolyDataMapper()
        edgeMapper.SetInputConnection(featureEdges.GetOutputPort())
        edgeActor = vtk.vtkActor()
        edgeActor.GetProperty().SetLineWidth(3)  # TODO: Width option in GUI?
        edgeActor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Black"))
        edgeActor.SetMapper(edgeMapper)

        poly_mapper.SetInputData(tri_filter.GetOutput())

        # The actor is a grouping mechanism: besides the geometry (mapper), it
        # also has a property, transformation matrix, and/or texture map.
        # Here we set its color and rotate it -22.5 degrees.
        actor = vtk.vtkActor()
        actor.SetMapper(poly_mapper)
        actor.GetProperty().SetColor(colour)

        return actor, edgeActor


class VtkWidget(QVTKRenderWindowInteractor):
    def __init__(self, widget):
        self.renderer = vtk.vtkRenderer()
        self.colour_provider = ColourProvider()
        super().__init__(widget)
        self.GetRenderWindow().AddRenderer(self.renderer)

    # TODO: PointClouds, vtk.vtkLineSource/vtkPolyLine, vtk.vtkPoints visualization
    def refresh_content(self, layer):
        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.

        # actor.GetProperty().SetEdgeColor(vtk.vtkNamedColors().GetColor3d("Red"))
        # actor.GetProperty().EdgeVisibilityOff()

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.
        vtk_layer = VtkPolyLayer(layer)

        ren = self.renderer
        renWin = self.GetRenderWindow()
        renWin.PointSmoothingOn()  # Point Cloud test
        iren = renWin.GetInteractor()
        iren.SetRenderWindow(renWin)

        # Add the actors to the renderer, set the background and size
        actor, edgeActor = vtk_layer.get_actors(self.colour_provider.next())
        ren.AddActor(actor)
        ren.AddActor(edgeActor)
        ren.SetBackground(vtk.vtkNamedColors().GetColor3d("light_grey"))

        # This allows the interactor to initalize itself. It has to be
        # called before an event loop.
        iren.Initialize()

        # We'll zoom in a little by accessing the camera and invoking a "Zoom"
        # method on it.
        ren.ResetCamera()
        # ren.GetActiveCamera().Zoom(1.5)
        renWin.Render()

