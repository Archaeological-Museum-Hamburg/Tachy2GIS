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
import gc
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import QAction, QHeaderView, QDialog, QFileDialog, QSizePolicy, QVBoxLayout, QLineEdit,\
    QPushButton, QProgressDialog, QProgressBar, qApp
from PyQt5.QtCore import QSettings, QItemSelectionModel, QTranslator, QCoreApplication, QThread, qVersion, Qt, QEvent, QObject
from PyQt5.QtGui import QIcon
from qgis.utils import iface
from qgis.core import Qgis, QgsMapLayerProxyModel, QgsProject, QgsMapLayerType, QgsWkbTypes, QgsLayerTreeGroup,\
    QgsLayerTreeLayer, QgsGeometry, QgsVectorDataProvider, QgsFeature, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils , \
    QgsVectorLayer
from qgis.gui import QgsMapToolPan

import vtk
from PyQt5 import QtCore, QtWidgets

from .T2G.TachyReader import TachyReader, AvailabilityWatchdog
from .FieldDialog import FieldDialog
from .Tachy2GIS_dialog import Tachy2GisDialog
from .T2G.autoZoomer import ExtentProvider, AutoZoomer
from .T2G.geo_com import connect_beep
from .T2G.GSI_Parser import make_vertex
from .T2G.visualization import VtkWidget, VtkMouseInteractorStyle, VtkLineLayer, VtkLayer

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
    NO_PORT = 'Select tachymeter USB port'

    """QGIS Plugin Implementation."""
    # Custom methods go here:

    ## Constructor
    #  @param iface An interface instance that will be passed to this class
    #  which provides the hook by which you can manipulate the QGIS
    #  application at run time.
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
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
        self.dlg = Tachy2GisDialog()
        self.vtk_mouse_interactor_style = VtkMouseInteractorStyle()
        self.render_container_layout = QVBoxLayout()
        self.markerWidget = vtk.vtkOrientationMarkerWidget()
        self.vtk_widget = VtkWidget(self.dlg.vtk_frame)
        self.vtk_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.render_container_layout.addWidget(self.vtk_widget)
        self.dlg.vtk_frame.setLayout(self.render_container_layout)
        # The interactorStyle is instantiated explicitly so it can be connected to
        # events
        self.vtk_widget.SetInteractorStyle(self.vtk_mouse_interactor_style)
        self.vtk_mouse_interactor_style.SetCurrentRenderer(self.vtk_widget.renderer)
        # Setup axes
        self.markerWidget.SetOrientationMarker(self.vtk_widget.axes)
        self.markerWidget.SetInteractor(self.vtk_widget.renderer.GetRenderWindow().GetInteractor())
        self.markerWidget.SetViewport(0.0, 0.0, 0.1, 0.3)
        self.markerWidget.EnabledOn()
        self.markerWidget.InteractiveOff()

        self.tachyReader = TachyReader(QSerialPort.Baud9600)
        self.availability_watchdog = AvailabilityWatchdog()
        # todo: Order
        self.dlg.zoomModeComboBox.addItems(['Track last point',
                                            'Layer',
                                            'Last feature',
                                            'Last 2 features',
                                            'Last 4 features',
                                            'Last 8 features',
                                            'Off'
                                            ])
        # self.pollingThread = QThread()
        # self.tachyReader.moveToThread(self.pollingThread)
        # self.pollingThread.start()
        self.pluginIsActive = False

    def vertex_received(self, line):
        new_vtx = make_vertex(line)
        self.vtk_mouse_interactor_style.vertices.append(new_vtx)
        self.dlg.coords.setText(f"{new_vtx}")
        self.vtk_mouse_interactor_style.draw()
        self.autozoom(0)

    def tachyConnected(self, emit, comName):
        if self.availability_watchdog.pollingTimer.isActive():
            self.availability_watchdog.shutDown()
        self.dlg.tachy_connect_button.setText(emit)
        self.dlg.tachy_connect_button.setToolTip(f"Verbunden mit {comName}")

    def tachyDisconnected(self, emit):
        self.tachyReader.pollingTimer.stop()
        if not self.availability_watchdog.pollingTimer.isActive():
            self.availability_watchdog.start()
        self.dlg.tachy_connect_button.setText(emit)
        self.dlg.tachy_connect_button.setToolTip("Keine Verbindung")

    def tachyAvailable(self, emit):
        self.dlg.tachy_connect_button.setText(emit)
        self.dlg.tachy_connect_button.setToolTip("Tachy verbinden")

    def dump(self):
        vertices = self.vtk_mouse_interactor_style.vertices
        if len(vertices) == 0:
            iface.messageBar().pushMessage("Fehler: ", "Keine Punkte vorhanden!", Qgis.Warning, 5)
            return

        targetLayer = self.dlg.targetLayerComboBox.currentLayer()
        vtk_layer = self.vtk_widget.layers[targetLayer.id()]
        if vtk_layer.add_feature(vertices) == -1:
            return
        # clear picked vertices and remove them from renderer
        self.vtk_mouse_interactor_style.vertices = []
        self.vtk_mouse_interactor_style.draw()
        # remove vtk layer and update renderer
        self.rerenderVtkLayer([targetLayer.id()])
        # todo: autozoom after dump?
        self.autozoom(self.dlg.zoomModeComboBox.currentIndex())

    # Used after dump and layerRemoved/added signal which return the layer ids as list
    # featuresDeleted returns feature ids (int) instead of layer id so activeLayer().id() is used
    def rerenderVtkLayer(self, layerIds=(0,)):
        # todo: featureAdded triggering for every feature added, calling update_renderer multiple times on save
        # featureAdded
        if isinstance(layerIds, int):
            layerIds = [layerIds]
        # featuresDeleted
        if isinstance(layerIds[0], int):
            if type(self.vtk_widget.layers[iface.activeLayer().id()].vtkActor) == tuple:
                for actor in self.vtk_widget.layers[iface.activeLayer().id()].vtkActor:
                    self.vtk_widget.renderer.RemoveActor(actor)
            else:
                self.vtk_widget.renderer.RemoveActor(self.vtk_widget.layers[iface.activeLayer().id()].vtkActor)
            self.vtk_widget.layers.pop(iface.activeLayer().id())
            self.update_renderer()
            return
        # legendLayersAdded/ layerRemoved
        for layerId in layerIds:
            if layerId in self.vtk_widget.layers:
                if type(self.vtk_widget.layers[layerId].vtkActor) == tuple:
                    for actor in self.vtk_widget.layers[layerId].vtkActor:
                        self.vtk_widget.renderer.RemoveActor(actor)
                else:
                    self.vtk_widget.renderer.RemoveActor(self.vtk_widget.layers[layerId].vtkActor)
                self.vtk_widget.layers.pop(layerId)
        self.update_renderer()

    # Disconnect Signals and stop QThreads
    def onCloseCleanup(self):
        self.vtk_widget.renderer.GetRenderWindow().Finalize()  # Renderer does not crash anymore after plugin reload
        self.dlg.closingPlugin.disconnect(self.onCloseCleanup)
        # disconnect setupControls
        self.dlg.tachy_connect_button.clicked.disconnect()
        self.dlg.logFileEdit.selectionChanged.disconnect()
        self.dlg.dumpButton.clicked.disconnect()
        self.dlg.deleteVertexButton.clicked.disconnect()
        self.vtk_mouse_interactor_style.trackingCall.trackPoint.disconnect(self.autozoom)
        self.dlg.setRefHeight.returnPressed.disconnect()
        self.dlg.zoomResetButton.clicked.disconnect()
        self.availability_watchdog.serial_available.disconnect()
        self.dlg.loadPointCloud.clicked.disconnect()
        self.dlg.sourceLayerComboBox.layerChanged.disconnect()
        self.dlg.targetLayerComboBox.layerChanged.disconnect()
        self.tachyReader.lineReceived.disconnect()
        self.dlg.zoomModeComboBox.activated.disconnect(self.autozoom)
        QgsProject.instance().layerTreeRoot().visibilityChanged.disconnect(self.update_renderer)
        QgsProject.instance().legendLayersAdded.disconnect(self.rerenderVtkLayer)
        QgsProject.instance().legendLayersAdded.disconnect(self.connectAddedMapLayers)
        QgsProject.instance().layersRemoved.disconnect(self.rerenderVtkLayer)
        self.disconnectMapLayers()
        # self.dlg.request_mirror.clicked.disconnect()
        # self.dlg.deleteAllButton.clicked.disconnect()
        # self.vertexList.layoutChanged.disconnect()

        self.availability_watchdog.shutDown()
        self.tachyReader.shutDown()
        self.pluginIsActive = False
        gc.collect()
        print('Signals disconnected!')

    def setActiveLayer(self):
        if Qt is None:
            return
        activeLayer = self.dlg.targetLayerComboBox.currentLayer()
        if activeLayer is None:
            return
        self.iface.setActiveLayer(activeLayer)

    # TODO: Remove?
    # def toggleEdit(self):
    #     iface.actionToggleEditing().trigger()

    def connectSerial(self):
        port = self.dlg.portComboBox.currentText()
        if not port == Tachy2Gis.NO_PORT:
            self.tachyReader.setPort(port)
            connect_beep(port)

    # TODO: Log default path QgsProject.instance().homePath()?
    def setLog(self):
        logFileName = QFileDialog.getOpenFileName(None,
                                                  'Log-Datei speichern...',
                                                  QgsProject.instance().homePath(),
                                                  'Text (*.txt)',
                                                  '*.txt')[0]
        if logFileName == '':
            self.dlg.logFileEdit.clear()
            self.tachyReader.hasLogFile = False
            return
        self.dlg.logFileEdit.setText(logFileName)
        self.tachyReader.setLogfile(logFileName)

    def dumpEnabled(self):
        verticesAvailable = (len(self.vtk_mouse_interactor_style.vertices) > 0)
        # Selecting a target layer while there are no vertices in the vertex list may cause segfaults. To avoid this,
        # the 'Dump' button is disabled as long there are none:
        self.dlg.dumpButton.setEnabled(verticesAvailable)

    def zoom_full_extent(self):
        canvas = iface.mapCanvas()
        canvas.zoomToFullExtent()
        canvas.refresh()

    def autozoom(self, index):
        if self.dlg.sourceLayerComboBox.currentLayer() == self.dlg.targetLayerComboBox.currentLayer():
            current_layer = self.dlg.sourceLayerComboBox.currentLayer()
        else:
            current_layer = self.dlg.targetLayerComboBox.currentLayer()
        if current_layer is None:
            return
        if "⛅" in current_layer.name() and index == 1:
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(*self.vtk_widget.layers[current_layer.id()].vtkActor.GetBounds())
            self.vtk_widget.renderer.GetRenderWindow().Render()
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.dlg.zoomModeComboBox.setCurrentIndex(1)
            return
        feats = [f for f in current_layer.getFeatures()]
        if index == 0:  # Track last point
            if self.dlg.zoomModeComboBox.currentIndex() == 0:
                if self.vtk_mouse_interactor_style.vertices:
                    self.vtk_widget.renderer.ResetCamera(self.vtk_mouse_interactor_style.vertices[-1][0],
                                                         self.vtk_mouse_interactor_style.vertices[-1][0],
                                                         self.vtk_mouse_interactor_style.vertices[-1][1],
                                                         self.vtk_mouse_interactor_style.vertices[-1][1],
                                                         self.vtk_mouse_interactor_style.vertices[-1][2],
                                                         self.vtk_mouse_interactor_style.vertices[-1][2])
                    self.vtk_widget.renderer.GetActiveCamera().Zoom(3)
                    self.vtk_widget.renderer.ResetCameraClippingRange()
                    self.vtk_widget.renderer.GetRenderWindow().Render()
        elif index == 1:  # Layer
            if not feats:
                return
            zVtx = []  # get zMin/zMax
            for feat in feats:
                for vtx in feat.geometry().vertices():
                    if not vtx.z() == vtx.z():  # 0 if nan
                        zVtx.append(0)
                        continue
                    zVtx.append(vtx.z())
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(current_layer.extent().xMinimum(),
                                                 current_layer.extent().xMaximum(),
                                                 current_layer.extent().yMinimum(),
                                                 current_layer.extent().yMaximum(),
                                                 min(zVtx), max(zVtx))
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.vtk_widget.renderer.GetRenderWindow().Render()

        elif index == 2:  # Last Feature
            if not feats:
                self.dlg.zoomModeComboBox.setCurrentIndex(1)
                self.autozoom(1)
                return
            featIds = [f.id() for f in feats]
            if min(featIds) < 0:  # layers in edit buffer have ids below 0
                index = featIds.index(min(featIds))
            else:
                index = -1
            zVtx = []
            for vtx in feats[index].geometry().vertices():
                if not vtx.z() == vtx.z():
                    zVtx.append(0)
                    continue
                zVtx.append(vtx.z())
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(feats[index].geometry().boundingBox().xMinimum(),
                                                 feats[index].geometry().boundingBox().xMaximum(),
                                                 feats[index].geometry().boundingBox().yMinimum(),
                                                 feats[index].geometry().boundingBox().yMaximum(),
                                                 min(zVtx), max(zVtx))
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.vtk_widget.renderer.GetRenderWindow().Render()

        elif index == 3:  # Last 2 Features
            if not feats or len(feats) < 2:
                self.dlg.zoomModeComboBox.setCurrentIndex(1)
                self.autozoom(1)
                return
            featIds = [f.id() for f in feats]
            featIndices = []
            for i in range(2):
                if min(featIds) < 0:
                    featIndices.append(featIds.index(min(featIds)))
                    featIds[featIds.index(min(featIds))] = 0
                else:
                    featIndices.append(featIds.index(featIds[-1]))
                    featIds.pop(-1)
            xMin, xMax, yMin, yMax, zVtx = [], [], [], [], []
            for idx in featIndices:
                xMin.append(feats[idx].geometry().boundingBox().xMinimum())
                yMin.append(feats[idx].geometry().boundingBox().yMinimum())
                xMax.append(feats[idx].geometry().boundingBox().xMaximum())
                yMax.append(feats[idx].geometry().boundingBox().yMaximum())
                for vtx in feats[idx].geometry().vertices():
                    if not vtx.z() == vtx.z():
                        zVtx.append(0)
                        continue
                    zVtx.append(vtx.z())
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(min(xMin), max(xMax),
                                                 min(yMin), max(yMax),
                                                 min(zVtx), max(zVtx))
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.vtk_widget.renderer.GetRenderWindow().Render()

        elif index == 4:  # Last 4 Features
            if not feats or len(feats) < 4:
                self.dlg.zoomModeComboBox.setCurrentIndex(1)
                self.autozoom(1)
                return
            featIds = [f.id() for f in feats]
            featIndices = []
            for i in range(4):
                if min(featIds) < 0:
                    featIndices.append(featIds.index(min(featIds)))
                    featIds[featIds.index(min(featIds))] = 0
                else:
                    featIndices.append(featIds.index(featIds[-1]))
                    featIds.pop(-1)
            xMin, xMax, yMin, yMax, zVtx = [], [], [], [], []
            for idx in featIndices:
                xMin.append(feats[idx].geometry().boundingBox().xMinimum())
                yMin.append(feats[idx].geometry().boundingBox().yMinimum())
                xMax.append(feats[idx].geometry().boundingBox().xMaximum())
                yMax.append(feats[idx].geometry().boundingBox().yMaximum())
                for vtx in feats[idx].geometry().vertices():
                    if not vtx.z() == vtx.z():
                        zVtx.append(0)
                        continue
                    zVtx.append(vtx.z())
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(min(xMin), max(xMax),
                                                 min(yMin), max(yMax),
                                                 min(zVtx), max(zVtx))
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.vtk_widget.renderer.GetRenderWindow().Render()

        elif index == 5:  # Last 8 Features
            if not feats or len(feats) < 8:
                self.dlg.zoomModeComboBox.setCurrentIndex(1)
                self.autozoom(1)
                return
            featIds = [f.id() for f in feats]
            featIndices = []
            for i in range(8):
                if min(featIds) < 0:
                    featIndices.append(featIds.index(min(featIds)))
                    featIds[featIds.index(min(featIds))] = 0
                else:
                    featIndices.append(featIds.index(featIds[-1]))
                    featIds.pop(-1)
            xMin, xMax, yMin, yMax, zVtx = [], [], [], [], []
            for idx in featIndices:
                xMin.append(feats[idx].geometry().boundingBox().xMinimum())
                yMin.append(feats[idx].geometry().boundingBox().yMinimum())
                xMax.append(feats[idx].geometry().boundingBox().xMaximum())
                yMax.append(feats[idx].geometry().boundingBox().yMaximum())
                for vtx in feats[idx].geometry().vertices():
                    if not vtx.z() == vtx.z():
                        zVtx.append(0)
                        continue
                    zVtx.append(vtx.z())
            self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
            self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
            self.vtk_widget.renderer.ResetCamera(min(xMin), max(xMax),
                                                 min(yMin), max(yMax),
                                                 min(zVtx), max(zVtx))
            self.vtk_widget.renderer.ResetCameraClippingRange()
            self.vtk_widget.renderer.GetRenderWindow().Render()
        elif index == 6:  # Off
            return

    def set_tachy_button_text(self, txt):
        self.dlg.tachy_connect_button.text = txt

    # currently unused
    def resetVtkCamera(self):
        self.vtk_widget.renderer.ResetCamera()
        self.vtk_widget.renderer.GetRenderWindow().Render()

    # TODO: Other views?
    def resetVtkCameraTop(self):
        self.vtk_widget.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
        self.vtk_widget.renderer.GetActiveCamera().SetPosition(0, 0, 0)
        self.vtk_widget.renderer.GetActiveCamera().SetFocalPoint(0, 0, -1)
        self.vtk_widget.renderer.ResetCamera(iface.mapCanvas().extent().xMinimum(),
                                             iface.mapCanvas().extent().xMaximum(),
                                             iface.mapCanvas().extent().yMinimum(),
                                             iface.mapCanvas().extent().yMaximum(),
                                             self.vtk_widget.renderer.ComputeVisiblePropBounds()[-2],
                                             self.vtk_widget.renderer.ComputeVisiblePropBounds()[-1])
        self.vtk_widget.renderer.GetActiveCamera().Zoom(3)
        self.vtk_widget.renderer.ResetCameraClippingRange()
        self.vtk_widget.renderer.GetRenderWindow().Render()

    def setCoords(self, coord):
        self.dlg.coords.setText(*coord)

    def setRefHeight(self):
        refHeight = self.dlg.setRefHeight.text()
        # self.tachyReader.setReflectorHeight(refHeight)

    def getRefHeight(self):
        self.dlg.setRefHeight.setText(self.tachyReader.getRefHeight)

    # Testline XYZRGB: 32565837.246360727 5933518.657366993 2.063523623769514 255 255 255
    def loadPointCloud(self, cloudFileName=None, cloudId=None):
        if not cloudFileName:
            cloudFileName = QFileDialog.getOpenFileName(None,
                                                        'PointCloud laden...',
                                                        QgsProject.instance().homePath(),
                                                        'XYZRGB (*.xyz);;Text (*.txt)',
                                                        '*.xyz;;*.txt')[0]
            if cloudFileName == '':
                return
        cellIndex = 0
        points = vtk.vtkPoints()
        points.SetDataTypeToDouble()
        cells = vtk.vtkCellArray()
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        progress = QProgressDialog(self.tr("Lade PointCloud..."), self.tr("Abbrechen"), 0, 0)
        progress.setWindowTitle(self.tr("PointCloud laden..."))
        progress.setCancelButton(None)
        progress.show()
        with open(cloudFileName, 'r', encoding="utf-8-sig") as file:
            for line in file:
                qApp.processEvents()
                split = line.split()
                pid = points.InsertNextPoint((float(split[0]), float(split[1]), float(split[2])))
                cells.InsertNextCell(1, [pid])
                colors.InsertTuple3(cellIndex, int(split[3]), int(split[4]), int(split[5]))
                cellIndex += 1
        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.SetVerts(cells)
        polyData.GetPointData().SetScalars(colors)
        pointMapper = vtk.vtkPolyDataMapper()
        pointMapper.SetInputData(polyData)
        pointMapper.Update()
        pointActor = vtk.vtkActor()
        pointActor.SetMapper(pointMapper)
        pointActor.PickableOff()

        # todo: QgsPointCloudLayer will be added with QGIS 3.18
        # create memory layer to allow handling of point cloud
        if not cloudId:
            pcLayer = QgsVectorLayer("PointZ", "⛅ " + os.path.basename(cloudFileName), "memory")
            # todo: add point to zoom in?
            QgsExpressionContextUtils.setLayerVariable(pcLayer, 'cloud_path', cloudFileName)
            VtkPcLayer = VtkLayer(pcLayer)
            VtkPcLayer.vtkActor = pointActor
            self.vtk_widget.layers[pcLayer.id()] = VtkPcLayer
            QgsProject.instance().addMapLayer(pcLayer)
        else:
            VtkPcLayer = VtkLayer(QgsProject.instance().mapLayersByName("⛅ " + os.path.basename(cloudFileName))[0])
            VtkPcLayer.vtkActor = pointActor
            self.vtk_widget.layers[cloudId] = VtkPcLayer
        self.vtk_widget.renderer.AddActor(pointActor)
        self.vtk_widget.renderer.GetRenderWindow().Render()
        del progress

# TODO: Set colors for active or inactive layers?
    def setPickable(self):
        currentLayer = self.dlg.sourceLayerComboBox.currentLayer()
        if currentLayer is None:
            currentLayer = self.dlg.sourceLayerComboBox.additionalItems()
        for ids, layer in self.vtk_widget.layers.items():
            if type(currentLayer) == list:
                if " ⛅   "+ids in currentLayer:
                    layer.PickableOn()
                continue
            if currentLayer.type() == QgsMapLayerType.RasterLayer:
                continue
            if currentLayer.geometryType() == QgsWkbTypes.NullGeometry:  # excel sheet
                continue
            if isinstance(layer, vtk.vtkActor):
                layer.PickableOff()
                layer.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Orange"))
                continue
            if not ids == currentLayer.id():
                if type(layer.vtkActor) == tuple:
                    for actor in layer.vtkActor:
                        actor.PickableOff()
                    layer.vtkActor[0].GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Orange"))
                else:
                    if isinstance(layer, VtkLineLayer):
                        layer.vtkActor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Black"))
                    else:
                        layer.vtkActor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Orange"))
                    layer.vtkActor.PickableOff()
            else:
                if type(layer.vtkActor) == tuple:
                    for actor in layer.vtkActor:
                        actor.PickableOn()
                    layer.vtkActor[0].GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Yellow"))
                else:
                    layer.vtkActor.PickableOn()
                    layer.vtkActor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("Yellow"))
        self.vtk_widget.refresh_content()

    # Interface code goes here:
    def setupControls(self):
        """This method connects all controls in the UI to their callbacks.
        It is called in add_action"""
        self.dlg.closingPlugin.connect(self.onCloseCleanup)
        self.dlg.tachy_connect_button.clicked.connect(self.tachyReader.hook_up)
        # self.dlg.request_mirror.clicked.connect(self.tachyReader.request_mirror_z)
        self.tachyReader.mirror_z_received.connect(self.getRefHeight)
        self.dlg.setRefHeight.returnPressed.connect(self.setRefHeight)
        self.vtk_mouse_interactor_style.trackingCall.trackPoint.connect(self.autozoom)

        self.dlg.logFileEdit.selectionChanged.connect(self.setLog)  # TODO: Only works by double clicking/dragging

        # self.dlg.deleteAllButton.clicked.connect(self.clearCanvas)
        # self.dlg.finished.connect(self.mapTool.clear)
        self.dlg.dumpButton.clicked.connect(self.dump)
        self.dlg.deleteVertexButton.clicked.connect(self.vtk_mouse_interactor_style.remove_selected)
        self.dlg.loadPointCloud.clicked.connect(self.loadPointCloud)

        # self.dlg.vertexTableView.setModel(self.vertexList)
        # self.dlg.vertexTableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.dlg.vertexTableView.setSelectionModel(QItemSelectionModel(self.vertexList))
        # self.dlg.vertexTableView.selectionModel().selectionChanged.connect(self.mapTool.selectVertex)

        self.dlg.sourceLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer | QgsMapLayerProxyModel.WritableLayer)
        self.dlg.sourceLayerComboBox.setExcludedProviders(["delimitedtext"])
        self.dlg.sourceLayerComboBox.setLayer(self.iface.activeLayer())
        self.dlg.sourceLayerComboBox.layerChanged.connect(self.setPickable)

        self.dlg.targetLayerComboBox.layerChanged.connect(self.setActiveLayer)
        self.dlg.targetLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.targetLayerComboBox.setLayer(self.iface.activeLayer())
        self.dlg.targetLayerComboBox.setExcludedProviders(["delimitedtext"])
        self.dlg.zoomResetButton.clicked.connect(self.resetVtkCameraTop)

        self.dlg.zoomModeComboBox.activated.connect(self.autozoom)
        self.dlg.zoomModeComboBox.setCurrentIndex(0)

        self.tachyReader.lineReceived.connect(self.vertex_received)
        self.tachyReader.serial_connected.connect(self.tachyConnected)
        self.tachyReader.serial_disconnected.connect(self.tachyDisconnected)
        self.availability_watchdog.serial_available.connect(self.tachyAvailable)

        # self.vtk_widget.resizeEvent().connect(self.renderer.resize)
        # Connect signals for existing layers
        self.connectMapLayers()
        QgsProject.instance().layerTreeRoot().visibilityChanged.connect(self.update_renderer)
        QgsProject.instance().legendLayersAdded.connect(self.rerenderVtkLayer)
        QgsProject.instance().legendLayersAdded.connect(self.connectAddedMapLayers)
        QgsProject.instance().layersRemoved.connect(self.rerenderVtkLayer)

        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

    def disconnectMapLayers(self):
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if layer.layer().type() == QgsMapLayerType.RasterLayer:
                continue
            if layer.layer().geometryType() == QgsWkbTypes.NullGeometry:
                continue
            layer.layer().featuresDeleted.disconnect(self.rerenderVtkLayer)
            layer.layer().featureAdded.disconnect(self.rerenderVtkLayer)
            layer.layer().afterRollBack.disconnect(self.rerenderVtkLayer)

    # connect existing QgsMapLayers
    def connectMapLayers(self):
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if layer.layer().type() == QgsMapLayerType.RasterLayer:
                continue
            if layer.layer().geometryType() == QgsWkbTypes.NullGeometry:
                continue
            layer.layer().featuresDeleted.connect(self.rerenderVtkLayer)
            layer.layer().featureAdded.connect(self.rerenderVtkLayer)
            layer.layer().afterRollBack.connect(self.rerenderVtkLayer)

    def connectAddedMapLayers(self, QgsMapLayers):
        for layer in QgsMapLayers:
            if layer.type() == QgsMapLayerType.RasterLayer:
                continue
            if layer.geometryType() == QgsWkbTypes.NullGeometry:
                continue
            layer.featuresDeleted.connect(self.rerenderVtkLayer)
            layer.featureAdded.connect(self.rerenderVtkLayer)
            layer.afterRollBack.connect(self.rerenderVtkLayer)

    def update_renderer(self):
        self.vtkLayerCleanUp()
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if layer.layer().type() == QgsMapLayerType.RasterLayer:
                continue
            if layer.layer().geometryType == QgsWkbTypes.NullGeometry:
                continue
            if layer.isVisible():
                if layer.layer().id() not in self.vtk_widget.layers:
                    if "⛅" in layer.layer().name():
                        self.loadPointCloud(QgsExpressionContextUtils.layerScope(layer.layer()).variable('cloud_path'), layer.layer().id())
                    else:
                        self.vtk_widget.switch_layer(layer.layer())
            else:  # remove actor from renderer and vtk_widget.layers{}
                if layer.layer().id() in self.vtk_widget.layers:
                    if type(self.vtk_widget.layers[layer.layer().id()].vtkActor) == tuple:
                        for actor in self.vtk_widget.layers[layer.layer().id()].vtkActor:
                            self.vtk_widget.renderer.RemoveActor(actor)
                        self.vtk_widget.layers.pop(layer.layer().id())
                    else:
                        self.vtk_widget.renderer.RemoveActor(self.vtk_widget.layers[layer.layer().id()].vtkActor)
                        self.vtk_widget.layers.pop(layer.layer().id())
        # print("vtk_widget layers:\n", self.vtk_widget.layers)
        self.vtk_widget.refresh_content()
        self.setPickable()

    # remove layers if they are not in the layer legend
    # todo: qgsLayerIds None type has no .id() when loading project while t2g is open
    def vtkLayerCleanUp(self):
        qgsLayerIds = [layer.layer().id() for layer in QgsProject.instance().layerTreeRoot().findLayers()]
        vtkDict = self.vtk_widget.layers.copy()
        for vtkLayerId, actor in vtkDict.items():
            if vtkLayerId not in qgsLayerIds:
                if type(self.vtk_widget.layers[vtkLayerId].vtkActor) == tuple:
                    for a in actor.vtkActor:
                        self.vtk_widget.renderer.RemoveActor(a)
                    self.vtk_widget.layers.pop(vtkLayerId)
                else:
                    self.vtk_widget.renderer.RemoveActor(self.vtk_widget.layers[vtkLayerId].vtkActor)
                    self.vtk_widget.layers.pop(vtkLayerId)

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

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # # Create the dialog (after translation) and keep reference
            if self.dlg is None:
                self.dlg = Tachy2GisDialog()
                self.render_container_layout = QVBoxLayout()
                self.vtk_widget = VtkWidget(self.dlg.vtk_frame)
                self.vtk_widget.refresh_content()
                self.setupControls()

            self.setupControls()
            # not implemented yet
            self.dlg.setRefHeight.hide()

            self.availability_watchdog.start()
            # self.tachyReader.beginListening()
            self.setActiveLayer()
            self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dlg)
            # Start with top view with QGIS map canvas extents
            self.resetVtkCameraTop()  # todo: resets with 1/-1 bounds because renderer was not yet interacted with
            self.update_renderer()
            self.dlg.show()
