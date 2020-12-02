# -*- coding: utf-8 -*-
#******************************************************************************
#
#
#******************************************************************************
from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
from .VertexList import T2G_Vertex, T2G_VertexList


## T2G_VertexePickerTool
#
# This is the map tool that allows the plugin to draw shapes on the map canvas
# while they are recorded.
class T2G_VertexePickerTool(QgsMapTool):
    ## Rubberband color
    RB_COLOR = Qt.red
    ## Rubberband fill color, alpha set to 50%
    RB_FILLCOLOR = QColor(255, 0, 0, 127)
    def __init__(self, parent): #tableModel, vertexIndex, zIndex):
        
        QgsMapTool.__init__(self, parent.iface.mapCanvas())
        self.parent = parent
        self.canvas = parent.iface.mapCanvas()
        # self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.vertexList = parent.vertexList
        self.rubberBand = QgsRubberBand(self.canvas)
        self.geometryType = QgsWkbTypes.PolygonGeometry
        self.rubberBand.setColor(self.RB_COLOR)
        self.rubberBand.setFillColor(self.RB_FILLCOLOR)
        self.rubberBand.setWidth(1)
        self.markers = []
        self.reset()
        self.alive = False
        
    def setGeometryType(self, layer):
        if not self.alive:
            return
        if layer is None:
            return
        if layer.type() == QgsMapLayerType.RasterLayer:
            return
        self.geometryType = layer.geometryType()
        geometry = self.rubberBand.asGeometry()
        self.rubberBand.reset(self.geometryType)
        self.rubberBand.addGeometry(geometry, layer)
        
    
    ## Reset the rubber band and clean up markers
    def reset(self):
        self.rubberBand.reset(self.geometryType)
        self.markers = []
    
    
    ## Adds a new vertex to the attached table model, the rubber band and the vertex markers
    def addVertex(self, label = None, source = None, x = None, y = None, z = None, vtx=None):
        if vtx:
            vertex = vtx
        else:
            vertex = T2G_Vertex(label, source, x, y, z)
        adjusted = self.vertexList.append(vertex)
        self.rubberBand.addPoint(adjusted.getQgsPointXY(), True)
        # TODO: getMarker() does not exist anymore
        # index = len(self.markers)
        # self.markers.append(adjusted.getMarker(self.canvas))
        # self.parent.dlg.vertexTableView.selectRow(index)

        
    def deleteVertex(self):
        selectionModel = self.parent.dlg.vertexTableView.selectionModel()
        if selectionModel.selectedIndexes():
            index = selectionModel.selectedIndexes()[0].row()
            self.rubberBand.removePoint(index)
            self.markers[index].hide()
            del self.markers[index]
            self.vertexList.deleteVertex(index)
            lastRow = len(self.markers) - 1
            if lastRow >= 0:
                self.parent.dlg.vertexTableView.selectRow(lastRow)
        pass
    
    ## Removes all markers, resets the rubber band and clears the table model 
    def clear(self):
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.reset()
        self.vertexList.clear()
        
    ## Finds the nearest existing 3D vertex, and adds it to the vertex list
    def canvasReleaseEvent(self, event):
        if self.vertexList.hasAnchors():
            x = event.pos().x()
            y = event.pos().y()
            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.addVertex(None, T2G_Vertex.SOURCE_INTERNAL, point.x(), point.y(), None)            
        else:
            QMessageBox(QMessageBox.Critical,
                        "No Anchors Available",
                        "Current layer has no anchors to snap to.",
                        QMessageBox.Ok).exec_()
        
    def selectVertex(self):
        selection = self.parent.dlg.vertexTableView.selectionModel().selectedRows()
        if selection:
            index = selection[0].row()
            self.vertexList.select(index)
            markerColors = self.vertexList.getColors()
            for marker, color in zip(self.markers, markerColors):
                marker.setColor(color)
            self.canvas.refresh()
        pass
    
    """
    def activate(self, *args, **kwargs):
        super(T2G_VertexePickerTool, self).activate()
        
    def deativate(self):
        self.clear()
        super(T2G_VertexePickerTool, self).deactivate()
        self.emit(SIGNAL("deactivated()"))
    """
        
if __name__ == "__main__":
    def printColors(vertexList):
        colors = vertexList.getColors()
        for c in colors:
            print(c.red(), c.green(), c.blue())
    
    vl = T2G_VertexList()
    vl.append(T2G_Vertex())
    vl.append(T2G_Vertex(1, 2, 3))
    vl.select(1)
    printColors(vl)
    vl.clearSelection()
    printColors(vl)
    wktv = T2G_Vertex(wkt = '552364.36630000011064112 5921140.47400000039488077 49.57150000000000034 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368')
    print(vl[0].wktDimensions)
    print(wktv.wktDimensions)
