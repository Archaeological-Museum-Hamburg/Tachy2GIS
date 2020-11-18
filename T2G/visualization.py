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
        self.wkbType = self.source_layer.wkbType()
        self.extractor = VtkAnchorUpdater(layer=self.source_layer)
        self.anchors = self.extractor.anchors
        self.geometries = self.extractor.geometries

    def update(self, dialog):
        self.extractor.signalAnchorCount.connect(dialog.setAnchorCount)
        self.extractor.signalAnchorProgress.connect(dialog.anchorProgress)
        self.extractor.signalGeometriesProgress.connect(dialog.geometriesProgress)
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


# TODO: Snapping visualization
#       show coordinates in widget 'coords' OnMouseMove
class VtkMouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        # self.AddObserver("MouseMoveEvent", self.mouse_move_event)  # TODO: camera not rotatable OnMouseMove (blocks left klick)
        # self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
        self.default_color = (0.0, 1.0, 1.0)
        self.select_color = (1.0, 0.2, 0.2)
        self.lastPickedActor = None
        self.lastPickedProperty = vtk.vtkProperty()

    # Creates a vtkPoints with RenderAsSpheresOn on a selected point and returns point coordinates as a tuple
    def OnRightButtonDown(self):
        if self.lastPickedActor:
            self.lastPickedActor.GetProperty().SetColor(self.default_color)
            # print(self.lastPickedActor.GetMapper().GetInput().GetPoint(0))

        clickPos = self.GetInteractor().GetEventPosition()
        print("Click pos: ", clickPos)
        # vtkPointPicker
        picker = vtk.vtkPointPicker()
        # TODO: Set tolerance in GUI?
        picker.SetTolerance(1000)
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetCurrentRenderer())  # vtkPointPicker
        picked = picker.GetPickPosition()  # vtkPointPicker
        print("vtkPointPicker picked: ", picked)

        picked_point = vtk.vtkPoints()
        picked_point.InsertNextPoint(*picked)
        vertices = vtk.vtkCellArray()
        vertices.InsertNextCell(1, [0])

        point_data = vtk.vtkPolyData()
        point_data.SetPoints(picked_point)
        point_data.SetVerts(vertices)

        pointMapper = vtk.vtkPolyDataMapper()
        pointMapper.SetInputData(point_data)
        pointActor = vtk.vtkActor()
        pointActor.SetMapper(pointMapper)
        # TODO: Set properties?
        pointActor.GetProperty().SetColor(self.select_color)
        pointActor.GetProperty().SetPointSize(10)
        pointActor.GetProperty().RenderPointsAsSpheresOn()
        pointActor.PickableOff()

        # draw lines between points
        if self.lastPickedActor:
            picked_point.InsertNextPoint(self.lastPickedActor.GetMapper().GetInput().GetPoint(0))

            polyLine = vtk.vtkPolyLine()
            polyLine.GetPointIds().SetNumberOfIds(2)
            for i in range(0, 2):
                polyLine.GetPointIds().SetId(i, i)
            cells = vtk.vtkCellArray()
            cells.InsertNextCell(polyLine)

            polyData = vtk.vtkPolyData()
            polyData.SetPoints(picked_point)
            polyData.SetLines(cells)

            lineMapper = vtk.vtkPolyDataMapper()
            lineMapper.SetInputData(polyData)
            lineActor = vtk.vtkActor()
            lineActor.SetMapper(lineMapper)
            lineActor.PickableOff()
            lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            lineActor.GetProperty().SetLineWidth(3)
            self.GetCurrentRenderer().AddActor(lineActor)

        # TODO: remove points on dump? reopening t2g removes points
        #       points can't be removed from selection
        #       GetCurrentRenderer only works if RenderWindow was interacted with (e.g. zoomed, rotated)
        self.GetCurrentRenderer().AddActor(pointActor)
        self.GetCurrentRenderer().GetRenderWindow().Render()
        self.lastPickedActor = pointActor

        return picked

        # vtkCellPicker test
        # picker = vtk.vtkCellPicker()
        # picker.SetTolerance(10000)
        # picker.Pick(clickPos[0], clickPos[1], 0, self.GetCurrentRenderer())
        # picked = picker.GetCellId()
        # print("vtkCellPicker picked: ", picked)

        # vtkPropPicker test
        # picker = vtk.vtkPropPicker()
        # picker.PickProp(clickPos[0], clickPos[1], self.GetCurrentRenderer())
        # picked = picker.GetViewProp()
        # print("Picked: ", picked)

    def OnRightButtonUp(self):
        pass

    def right_button_press_event(self, obj, event):
        print("Right Button pressed")
        self.OnRightButtonDown()
        return

    def right_button_release_event(self, obj, event):
        print("Right Button released")
        self.OnRightButtonUp()
        return

    def OnMouseMove(self):
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPointPicker()
        picker.SetTolerance(0)
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetCurrentRenderer())
        picked = picker.GetPickPosition()

    def mouse_move_event(self, obj, event):
        self.OnMouseMove()
        return
