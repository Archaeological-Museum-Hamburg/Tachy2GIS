# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Tachy2Gis
                                 A QGIS plugin
 This plugin allows to create geometries directly with a connected tachymeter
                              -------------------
        begin                : 2017-11-26
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Christian Trapp
        email                : mail@christiantrapp.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
from . import resources
"""
import pydevd
try:
    pydevd.settrace('localhost',
                    port=6565,
                    stdoutToServer=True,
                    stderrToServer=True,
                    suspend=False)
except ConnectionRefusedError:
    pass
"""
import os
import gc  # TODO: Garbage collect?
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QAction, QHeaderView, QDialog, QFileDialog, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import QSettings, QItemSelectionModel, QTranslator, QCoreApplication, QThread, qVersion, Qt
from PyQt5.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsMapToolPan

import vtk
import vtkmodules
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util.colors import tomato

from .T2G.VertexList import T2G_VertexList, T2G_Vertex
from .T2G.TachyReader import TachyReader, AvailabilityWatchdog
from .FieldDialog import FieldDialog
from .T2G.VertexPickerTool import T2G_VertexePickerTool
from .Tachy2GIS_dialog import Tachy2GisDialog
from .T2G.autoZoomer import ExtentProvider, AutoZoomer
from .T2G.geo_com import connect_beep


def make_axes_actor(scale, xyzLabels):
    axes = vtk.vtkAxesActor()
    axes.SetScale(scale[0], scale[1], scale[2])
    axes.SetShaftTypeToCylinder()
    axes.SetXAxisLabelText(xyzLabels[0])
    axes.SetYAxisLabelText(xyzLabels[1])
    axes.SetZAxisLabelText(xyzLabels[2])
    axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
    axes.SetConeRadius(1.025 * axes.GetConeRadius())
    axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
    tprop = axes.GetXAxisCaptionActor2D().GetCaptionTextProperty()
    tprop.ItalicOn()
    tprop.ShadowOn()
    tprop.SetFontFamilyToTimes()
    # Use the same text properties on the other two axes.
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tprop)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShallowCopy(tprop)
    return axes


class Tachy2Gis:
    """QGIS Plugin Implementation."""
    # Custom methods go here:

    NO_PORT = 'Select tachymeter USB port'

    def vertexReceived(self, line):
        newVtx = T2G_Vertex.fromGSI(line)
        self.mapTool.addVertex(vtx=newVtx)

    ## Clears the map canvas and in turn the vertexList
    def clearCanvas(self):
        self.mapTool.clear()

    ## Opens the field dialog in preparation of dumping new vertices to the target layer
    def dump(self):
        # the input table of the dialog is updated
        self.fieldDialog.populateFieldTable()
        result = self.fieldDialog.exec_()
        if result == QDialog.Accepted:
            targetLayer = self.fieldDialog.layer
            self.vertexList.dumpToFile(targetLayer, self.fieldDialog.fieldData)
            # if the target layer holds point geometries, only the currently selected vertex is dumped and
            # removed from the list
            if self.fieldDialog.targetLayerComboBox.currentLayer().geometryType() == 0:
                self.mapTool.deleteVertex()
            else:
                # otherwise the list is cleared
                self.mapTool.clear()
            targetLayer.dataProvider().forceReload()
            targetLayer.triggerRepaint()
            self.vertexList.updateAnchors(self.dlg.sourceLayerComboBox.currentLayer())
        else:
            return

    ## Restores the map tool to the one that was active before T2G was started
    #  The pan tool is the default tool used by QGIS
    def restoreTool(self):
        if self.previousTool is None:
            self.previousTool = QgsMapToolPan(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.previousTool)

    # Disconnect Signals and stop QThreads
    def onCloseCleanup(self):
        self.dlg.tachy_connect_button.clicked.disconnect(self.tachyReader.hook_up)
        # self.dlg.request_mirror.clicked.disconnect(self.tachyReader.request_mirror_z)
        self.dlg.logFileEdit.selectionChanged.disconnect(self.setLog)
        # self.dlg.deleteAllButton.clicked.disconnect(self.clearCanvas)
        self.dlg.finished.disconnect(self.mapTool.clear)
        self.dlg.dumpButton.clicked.disconnect(self.dump)
        self.dlg.deleteVertexButton.clicked.disconnect(self.mapTool.deleteVertex)
        self.dlg.finished.disconnect(self.restoreTool)
        self.dlg.accepted.disconnect(self.restoreTool)
        self.dlg.rejected.disconnect(self.restoreTool)
        self.dlg.rejected.disconnect(self.onCloseCleanup)
        self.dlg.sourceLayerComboBox.layerChanged.disconnect(self.setActiveLayer)
        self.dlg.sourceLayerComboBox.layerChanged.disconnect(self.mapTool.clear)
        self.fieldDialog.targetLayerComboBox.layerChanged.disconnect(self.targetChanged)
        # self.vertexList.layoutChanged.disconnect(self.dumpEnabled)
        self.fieldDialog.buttonBox.accepted.disconnect(self.extent_provider.add_feature)
        self.dlg.zoomResetButton.clicked.disconnect(self.extent_provider.reset)
        self.dlg.zoomResetButton.clicked.disconnect(self.resetVtkCamera)
        # self.dlg.rejected.disconnect(self.onCloseCleanup)  # error?
        self.availability_watchdog.serial_available.disconnect(self.dlg.tachy_connect_button.setText)
        self.availability_watchdog.shutDown()
        self.tachyReader.shutDown()
        gc.collect()
        print("Signals disconnected!")

    def setActiveLayer(self):
        if Qt is None:
            return
        activeLayer = self.dlg.sourceLayerComboBox.currentLayer()
        if activeLayer is None:
            return
        self.iface.setActiveLayer(activeLayer)
        self.vertexList.updateAnchors(activeLayer)
        
    def targetChanged(self):
        targetLayer = self.fieldDialog.targetLayerComboBox.currentLayer()
        self.mapTool.setGeometryType(targetLayer)

    def toggleEdit(self):
        iface.actionToggleEditing().trigger()

    def connectSerial(self):
        port = self.dlg.portComboBox.currentText()
        if not port == Tachy2Gis.NO_PORT:
            self.tachyReader.setPort(port)
            connect_beep(port)

    def setLog(self):
        logFileName = QFileDialog.getOpenFileName()[0]
        self.dlg.logFileEdit.setText(logFileName)
        self.tachyReader.setLogfile(logFileName)

    def dumpEnabled(self):
        verticesAvailable = (len(self.vertexList) > 0)
        # Selecting a target layer while there are no vertices in the vertex list may cause segfaults. To avoid this,
        # the 'Dump' button is disabled as long there are none:
        self.dlg.dumpButton.setEnabled(verticesAvailable)

    def zoom_full_extent(self):
        canvas = iface.mapCanvas()
        canvas.zoomToFullExtent()
        canvas.refresh()

    def set_tachy_button_text(self, txt):
        self.dlg.tachy_connect_button.text = txt

    def resetVtkCamera(self):
        self.renderer.ResetCamera()
        self.renderer.GetRenderWindow().Render()

    def setCoords(self, coord):
        self.dlg.coords.setText(*coord)

    # Interface code goes here:
    def setupControls(self):
        """This method connects all controls in the UI to their callbacks.
        It is called in add_action"""
        self.dlg.tachy_connect_button.clicked.connect(self.tachyReader.hook_up)
        # self.dlg.request_mirror.clicked.connect(self.tachyReader.request_mirror_z)

        self.dlg.logFileEdit.selectionChanged.connect(self.setLog)  # TODO: Only works by double clicking

        # self.dlg.deleteAllButton.clicked.connect(self.clearCanvas)
        self.dlg.finished.connect(self.mapTool.clear)
        self.dlg.dumpButton.clicked.connect(self.dump)
        self.dlg.deleteVertexButton.clicked.connect(self.mapTool.deleteVertex)

        # self.dlg.vertexTableView.setModel(self.vertexList)
        # self.dlg.vertexTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.dlg.vertexTableView.setSelectionModel(QItemSelectionModel(self.vertexList))
        # self.dlg.vertexTableView.selectionModel().selectionChanged.connect(self.mapTool.selectVertex)

        self.dlg.finished.connect(self.restoreTool)
        self.dlg.accepted.connect(self.restoreTool)
        self.dlg.rejected.connect(self.restoreTool)
        self.dlg.rejected.connect(self.onCloseCleanup)

        self.dlg.sourceLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer | QgsMapLayerProxyModel.WritableLayer)
        self.dlg.sourceLayerComboBox.setLayer(self.iface.activeLayer())
        self.dlg.sourceLayerComboBox.layerChanged.connect(self.setActiveLayer)
        self.dlg.sourceLayerComboBox.layerChanged.connect(self.mapTool.clear)

        self.fieldDialog.targetLayerComboBox.layerChanged.connect(self.targetChanged)
        # self.vertexList.layoutChanged.connect(self.dumpEnabled)
        self.fieldDialog.buttonBox.accepted.connect(self.extent_provider.add_feature)
        self.dlg.zoomResetButton.clicked.connect(self.extent_provider.reset)
        self.dlg.zoomResetButton.clicked.connect(self.resetVtkCamera)

        self.dlg.zoomModeComboBox.addItems(['Layer',
                                            'Last feature',
                                            'Last 2 features',
                                            'Last 4 features',
                                            'Last 8 features',
                                            ])
        self.dlg.zoomModeComboBox.currentIndexChanged.connect(self.extent_provider.set_mode)
        # self.dlg.zoomActiveCheckBox.stateChanged.connect(self.auto_zoomer.set_active)
        self.extent_provider.ready.connect(self.auto_zoomer.apply)
        self.availability_watchdog.serial_available.connect(self.dlg.tachy_connect_button.setText)

        self.vtk_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.render_container_layout.addWidget(self.vtk_widget)
        self.dlg.vtk_frame.setLayout(self.render_container_layout)
        self.vtk_widget.SetInteractorStyle(VtkMouseInteractorStyle())
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        # self.vtk_widget.resizeEvent().connect(self.renderer.resize)
        self.vertexList.signal_anchors_updated.connect(self.update_renderer)

    # TODO: PointClouds, vtk.vtkLineSource/vtkPolyLine, vtk.vtkPoints visualization
    def update_renderer(self):
        poly_data = self.vertexList.anchorUpdater.poly_data
        # The mapper is responsible for pushing the geometry into the graphics
        # library. It may also do color mapping, if scalars or other
        # attributes are defined.
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
        actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Orange"))

        # actor.GetProperty().SetEdgeColor(vtk.vtkNamedColors().GetColor3d("Red"))
        # actor.GetProperty().EdgeVisibilityOff()

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.
        ren = self.renderer
        renWin = self.vtk_widget.GetRenderWindow()
        renWin.PointSmoothingOn()  # Point Cloud test
        iren = renWin.GetInteractor()
        iren.SetRenderWindow(renWin)

        # Add the actors to the renderer, set the background and size
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

    ## Constructor
    #  @param iface An interface instance that will be passed to this class
    #  which provides the hook by which you can manipulate the QGIS
    #  application at run time.
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.dlg = Tachy2GisDialog()
        self.renderer = vtk.vtkRenderer()
        self.render_container_layout = QVBoxLayout()
        self.vtk_widget = QVTKRenderWindowInteractor(self.dlg.vtk_frame)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Tachy2Gis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr('&Tachy2GIS')
        # remove empty toolbar
        # self.toolbar = self.iface.addToolBar('Tachy2Gis')
        # self.toolbar.setObjectName('Tachy2Gis')
        
        # From here: Own additions
        self.vertexList = T2G_VertexList()
        self.extent_provider = ExtentProvider(self.vertexList, self.iface.mapCanvas())
        self.auto_zoomer = AutoZoomer(self.iface.mapCanvas(), self.extent_provider)

        self.mapTool = T2G_VertexePickerTool(self)
        self.previousTool = None
        self.fieldDialog = FieldDialog(self.iface.activeLayer())
        self.tachyReader = TachyReader(QSerialPort.Baud9600)
        self.availability_watchdog = AvailabilityWatchdog()
        self.availability_watchdog.start()
        # self.pollingThread = QThread()
        # self.tachyReader.moveToThread(self.pollingThread)
        # self.pollingThread.start()
        self.tachyReader.lineReceived.connect(self.vertexReceived)
        # self.tachyReader.beginListening()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Tachy2Gis', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        # self.dlg = Tachy2GisDialog()
        # self.setupControls()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Tachy2Gis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr('Tachy2GIS'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr('&Tachy2GIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        # del self.toolbarminec

    def run(self):
        """Run method that performs all the real work"""
        # # Create the dialog (after translation) and keep reference
        self.dlg = Tachy2GisDialog()
        self.renderer = vtk.vtkRenderer()
        self.render_container_layout = QVBoxLayout()
        self.vtk_widget = QVTKRenderWindowInteractor(self.dlg.vtk_frame)
        self.setupControls()
        self.availability_watchdog.start()
        self.tachyReader.start()
        # Store the active map tool and switch to the T2G_VertexPickerTool
        self.previousTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.mapTool.alive = True
        self.setActiveLayer()
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass


# TODO: Replace glyphs with points for visualization
#       Change point color for latest selection
#       Snapping visualization
#       show coordinates in widget 'coords' OnMouseMove
#       draw lines between points
class VtkMouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.AddObserver("RightButtonPressEvent", self.right_button_press_event)
        # self.AddObserver("MouseMoveEvent", self.mouse_move_event)  # TODO: camera not rotatable OnMouseMove (blocks left klick)
        # self.AddObserver("RightButtonReleaseEvent", self.right_button_release_event)
        self.default_color = (0.0, 1.0, 1.0)
        self.select_color = (1.0, 0.2, 0.2)
        self.lastPickedActor = None
        self.lastPickedProperty = vtk.vtkProperty()

    # Creates a glyph on a selected point and returns point coordinates as a tuple
    def OnRightButtonDown(self):
        if self.lastPickedActor:
            self.lastPickedActor.GetProperty().SetColor(self.default_color)

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

        # TODO: remove points on dump? reopening t2g removes points
        #       spheres can't be removed from selection
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

