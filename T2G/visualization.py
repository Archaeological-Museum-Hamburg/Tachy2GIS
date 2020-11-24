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


class VtkLayer:
    def __init__(self, qgs_layer):
        self.source_layer = qgs_layer
        self.id = self.source_layer.id()
        self.wkbType = self.source_layer.wkbType()
        self.extractor = VtkAnchorUpdater(layer=self.source_layer, wkbType=self.wkbType)
        self.anchors = self.extractor.anchors
        self.geometries = self.extractor.geometries
        self.poly_data = self.extractor.poly_data

    def update(self, dialog):
        self.extractor.signalAnchorCount.connect(dialog.setAnchorCount)
        self.extractor.signalAnchorProgress.connect(dialog.anchorProgress)
        self.extractor.signalGeometriesProgress.connect(dialog.geometriesProgress)
        self.poly_data = self.extractor.startExtraction(self.wkbType)

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
        # poly_data = self.anchor_updater.layer_cache[self.source_layer.id]['poly_data']
        #poly_data = self.extractor.layer_cache[self.source_layer.id()]['poly_data']
        # TODO: Get poly_data from VtkLayer
        poly_data = self.extractor.startExtraction(self.wkbType)
        # print(self.poly_data)

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
        self.layers = {}

    def switch_layer(self, qgis_layer):
        layer_id = qgis_layer.id()
        print(layer_id)
        if layer_id not in self.layers.keys():
            print(self.layers)
            created = VtkPolyLayer(qgs_layer=qgis_layer)
            print('made a new one!')
            self.layers[layer_id] = created
            actor, edge_actor = created.get_actors(self.colour_provider.next())
            self.renderer.AddActor(actor)
            self.renderer.AddActor(edge_actor)
        self.refresh_content()


    # TODO: PointClouds, vtk.vtkLineSource/vtkPolyLine, vtk.vtkPoints visualization
    def refresh_content(self):
        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.

        # actor.GetProperty().SetEdgeColor(vtk.vtkNamedColors().GetColor3d("Red"))
        # actor.GetProperty().EdgeVisibilityOff()

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.

        ren = self.renderer
        renWin = self.GetRenderWindow()
        renWin.PointSmoothingOn()  # Point Cloud test
        iren = renWin.GetInteractor()
        iren.SetRenderWindow(renWin)

        # Add the actors to the renderer, set the background and size
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
#       use only one vtkPoints object
class VtkMouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        # self.AddObserver("MouseMoveEvent", self.mouse_move_event)  # TODO: camera not rotatable OnMouseMove (blocks left klick)
        # self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
        self.default_color = (0.0, 1.0, 1.0)
        self.select_color = (1.0, 0.2, 0.2)
        self.lastPickedActor = None
        self.lastPickedProperty = vtk.vtkProperty()
        self.vertices = []
        self.select_index = -1

        self.vtk_points = vtk.vtkPoints()
        self.vtk_points.SetDataTypeToDouble()
        self.vertex_cell_array = vtk.vtkCellArray()
        self.poly_data = vtk.vtkPolyData()

        self.vertices_actor = vtk.vtkActor()
        self.selected_vertex_actor = vtk.vtkActor()
        self.poly_line_actor = vtk.vtkActor()
        self.actors = [self.vertices_actor,
                       self.selected_vertex_actor,
                       self.poly_line_actor]

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
        self.vertices.append(picked)
        # move this to draw logic
        point_id = [0]
        point_id[0] = self.vtk_points.InsertNextPoint(*picked)
        self.vertex_cell_array.InsertNextCell(1, point_id)
        print(self.vtk_points)
        self.poly_data.SetPoints(self.vtk_points)
        self.poly_data.SetVerts(self.vertex_cell_array) # Required for mapper


        """
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
        self.lastPickedActor = pointActor
        """
        self.draw()
        return picked

    def draw(self):
        for actor in self.actors:
            self.GetCurrentRenderer().RemoveActor(actor)
        # put all self.vertices into vertex_actor
        # buid poly_line from vertices
        # add selected point actor (and make it slightly bigger)
        # add all of them to the renderer
        pointMapper = vtk.vtkPolyDataMapper()
        pointMapper.SetInputData(self.poly_data)
        print(self.poly_data)
        pointActor = vtk.vtkActor()
        pointActor.SetMapper(pointMapper)
        # TODO: Set properties?
        pointActor.GetProperty().SetColor(self.select_color)
        pointActor.GetProperty().SetPointSize(10)
        pointActor.GetProperty().RenderPointsAsSpheresOn()
        pointActor.PickableOff()
        if self.GetCurrentRenderer():
            self.GetCurrentRenderer().AddActor(pointActor)
            self.GetCurrentRenderer().GetRenderWindow().Render()

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
