import vtk
from qgis.core import QgsFeature, QgsGeometry, QgsWkbTypes
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
        self.geoType = self.source_layer.geometryType()
        self.extractor = VtkAnchorUpdater(layer=self.source_layer, geoType=self.geoType)
        self.anchors = self.extractor.anchors
        self.geometries = self.extractor.geometries
        self.poly_data = self.extractor.poly_data

    def update(self, dialog):
        self.extractor.signalAnchorCount.connect(dialog.setAnchorCount)
        self.extractor.signalAnchorProgress.connect(dialog.anchorProgress)
        self.extractor.signalGeometriesProgress.connect(dialog.geometriesProgress)
        self.poly_data = self.extractor.startExtraction()

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
    vtkActor = None

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
        # poly_data = self.extractor.layer_cache[self.source_layer.id()]['poly_data']
        poly_data = self.extractor.startExtraction()
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

        self.vtkActor = actor, edgeActor
        return actor, edgeActor

        # if self.geoType == QgsWkbTypes.LineGeometry:
        #     lineMapper = vtk.vtkPolyDataMapper()
        #     lineMapper.SetInputData(poly_data)
        #     lineActor = vtk.vtkActor()
        #     lineActor.SetMapper(lineMapper)
        #     lineActor.GetProperty().SetColor(colour)
        #     lineActor.GetProperty().SetLineWidth(3)
        #
        #     self.vtkActor = lineActor
        #     return lineActor
        #
        # if self.geoType == QgsWkbTypes.PointGeometry:
        #     pointMapper = vtk.vtkPolyDataMapper()
        #     pointMapper.SetInputData(poly_data)
        #     pointActor = vtk.vtkActor()
        #     pointActor.SetMapper(pointMapper)
        #     pointActor.GetProperty().SetPointSize(5)
        #     pointActor.GetProperty().RenderPointsAsSpheresOn()
        #     pointActor.GetProperty().SetColor(colour)
        #
        #     self.vtkActor = pointActor
        #     return pointActor


class VtkLineLayer(VtkLayer):
    vtkActor = None

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
        poly_data = self.extractor.startExtraction()
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInputData(poly_data)
        lineActor = vtk.vtkActor()
        lineActor.SetMapper(lineMapper)
        lineActor.GetProperty().SetColor(colour)
        lineActor.GetProperty().SetLineWidth(3)

        self.vtkActor = lineActor
        return lineActor


class VtkPointLayer(VtkLayer):
    vtkActor = None

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
        poly_data = self.extractor.startExtraction()
        pointMapper = vtk.vtkPolyDataMapper()
        pointMapper.SetInputData(poly_data)
        pointActor = vtk.vtkActor()
        pointActor.SetMapper(pointMapper)
        pointActor.GetProperty().SetPointSize(5)
        pointActor.GetProperty().RenderPointsAsSpheresOn()
        pointActor.GetProperty().SetColor(colour)

        self.vtkActor = pointActor
        return pointActor


class VtkWidget(QVTKRenderWindowInteractor):
    def __init__(self, widget):
        self.renderer = vtk.vtkRenderer()
        self.axes = vtk.vtkAxesActor()
        self.axes.PickableOff()
        self.colour_provider = ColourProvider()
        super().__init__(widget)
        self.GetRenderWindow().AddRenderer(self.renderer)
        self.layers = {}

    def switch_layer(self, qgis_layer):
        layer_id = qgis_layer.id()
        if qgis_layer.type() != 1:  # Raster layers have no geometryType() method
            geoType = qgis_layer.geometryType()
        else:
            geoType = None
        print(layer_id)
        if layer_id not in self.layers.keys():
            if geoType == QgsWkbTypes.PolygonGeometry:
                print(self.layers)
                created = VtkPolyLayer(qgs_layer=qgis_layer)
                print('made a new one!')
                self.layers[layer_id] = created
                actor, edge_actor = created.get_actors(self.colour_provider.next())
                self.renderer.AddActor(actor)
                self.renderer.AddActor(edge_actor)
            if geoType == QgsWkbTypes.LineGeometry:
                print(self.layers)
                created = VtkLineLayer(qgs_layer=qgis_layer)
                print('made a new one!')
                self.layers[layer_id] = created
                lineActor = created.get_actors(self.colour_provider.next())
                self.renderer.AddActor(lineActor)
            if geoType == QgsWkbTypes.PointGeometry:
                print(self.layers)
                created = VtkPointLayer(qgs_layer=qgis_layer)
                print('made a new one!')
                self.layers[layer_id] = created
                pointActor = created.get_actors(self.colour_provider.next())
                self.renderer.AddActor(pointActor)
        self.refresh_content()

    def refresh_content(self):
        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.

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


class VtkMouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        # self.AddObserver("MouseMoveEvent", self.mouse_move_event)
        # self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
        self.default_color = (0.0, 1.0, 1.0)
        self.select_color = (1.0, 0.2, 0.2)
        self.vertices = []
        self.select_index = -1

        self.initialize_geometry_info()

        self.vertices_actor = vtk.vtkActor()
        self.selected_vertex_actor = vtk.vtkActor()
        self.poly_line_actor = vtk.vtkActor()
        self.actors = [self.vertices_actor,
                       self.selected_vertex_actor,
                       self.poly_line_actor]

    def initialize_geometry_info(self):
        self.vtk_points = vtk.vtkPoints()
        self.vtk_points.SetDataTypeToDouble()
        self.vertex_cell_array = vtk.vtkCellArray()
        self.poly_data = vtk.vtkPolyData()

    # Creates a vtkPoints with RenderAsSpheresOn on a selected point and appends point coordinates to self.vertices
    # TODO: GetCurrentRenderer only works if RenderWindow was interacted with (e.g. zoomed, rotated)
    def OnRightButtonDown(self):
        clickPos = self.GetInteractor().GetEventPosition()
        print("Click pos: ", clickPos)
        picker = vtk.vtkPointPicker()
        picker.SetTolerance(100)
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetCurrentRenderer())
        picked = picker.GetPickPosition()
        picked_actor = picker.GetActor()
        print("vtkPointPicker picked: ", picked)
        if picked in self.vertices:
            print("Vertex already in list!")
            return
        # return if selection is not an actor
        if picked_actor is None:
            return
        print(len(self.vertices))
        self.vertices.append(picked)
        print(len(self.vertices))
        self.draw()

    def draw(self):
        for actor in self.actors:
            if actor is None:
                continue
            self.GetCurrentRenderer().RemoveActor(actor)
            actor.SetMapper(None)
        # put all self.vertices into vertex_actor
        # build poly_line from vertices
        # add selected point actor (and make it slightly bigger)
        # add all of them to the renderer
        self.initialize_geometry_info()
        for vertex in self.vertices:
            pid = self.vtk_points.InsertNextPoint(vertex)
            self.vertex_cell_array.InsertNextCell(1, [pid])
        self.vtk_points.Modified()
        self.poly_data.SetPoints(self.vtk_points)
        self.poly_data.SetVerts(self.vertex_cell_array)
        pointMapper = vtk.vtkPolyDataMapper()
        pointMapper.SetInputData(self.poly_data)
        self.vertices_actor.SetMapper(pointMapper)
        self.vertices_actor.GetProperty().SetColor(self.default_color)
        self.vertices_actor.GetProperty().SetPointSize(10)
        self.vertices_actor.GetProperty().RenderPointsAsSpheresOn()
        self.vertices_actor.PickableOff()

        # Create polylines from self.vtk_points if there is more than one vertex
        if len(self.vertices):
            polyLine = vtk.vtkPolyLine()
            polyLine.GetPointIds().SetNumberOfIds(len(self.vertices))
            for i in range(len(self.vertices)):
                polyLine.GetPointIds().SetId(i, i)
            cells = vtk.vtkCellArray()
            cells.InsertNextCell(polyLine)

            polyData = vtk.vtkPolyData()
            polyData.SetPoints(self.vtk_points)
            polyData.SetLines(cells)

            lineMapper = vtk.vtkPolyDataMapper()
            lineMapper.SetInputData(polyData)
            self.poly_line_actor.SetMapper(lineMapper)
            self.poly_line_actor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.poly_line_actor.GetProperty().SetLineWidth(3)
            self.poly_line_actor.PickableOff()

        # Create bigger, self.select_color selection point
        if self.vertices:
            selected = vtk.vtkPoints()
            selected.SetDataTypeToDouble()
            selected.InsertNextPoint(self.vertices[self.select_index])
            selected_cells = vtk.vtkCellArray()
            selected_cells.InsertNextCell(1, [0])
            selected_poly_data = vtk.vtkPolyData()
            selected_poly_data.SetPoints(selected)
            selected_poly_data.SetVerts(selected_cells)
            selected_mapper = vtk.vtkPolyDataMapper()
            selected_mapper.SetInputData(selected_poly_data)
            self.selected_vertex_actor.SetMapper(selected_mapper)
            self.selected_vertex_actor.GetProperty().SetColor(self.select_color)
            self.selected_vertex_actor.GetProperty().SetPointSize(15)
            self.selected_vertex_actor.GetProperty().RenderPointsAsSpheresOn()
            self.selected_vertex_actor.PickableOff()

        if self.GetCurrentRenderer():
            self.GetCurrentRenderer().AddActor(self.selected_vertex_actor)
            self.GetCurrentRenderer().AddActor(self.vertices_actor)
            self.GetCurrentRenderer().AddActor(self.poly_line_actor)
            self.GetCurrentRenderer().GetRenderWindow().Render()

    def set_selection(self, index):
        # With the changes in draw, this can be used as a receiver for a selection_changed
        # event of a vertex list widget
        self.select_index = index
        self.draw()

    # Remove vertex from self.vertices and self.vtk_points
    def remove_selected(self):
        if self.vertices:
            # No idea how this happens, but it looks like the vertex list gets reversed in some other
            # step. Without reversing it before removing a vertex, the index '-1' deletes the first element.
            # '.pop' behaves the same way.
            # working with the select_index allows to work with a wdget that allows selection of vertices.

            # self.vertices.reverse()
            del self.vertices[self.select_index]
            # self.vertices.reverse()
            # self.select_index = -1
            self.draw()

    def removeAllVertices(self):
        self.vertices = []
        self.draw()

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
