# -*- coding: utf-8 -*-
#******************************************************************************
#
#
#******************************************************************************
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *



class T2Gvertex():
    def __init__(self, x = None, y = None, z = None):
        self.x = x
        self.y = y
        self.z = z
        
    def getQpoint(self):
        return QgsPoint(self.x, self.y)
    
class T2GvertexList():
    VERTEX_COLOR = QColor(0, 255, 0)
    SELECTED_COLOR = QColor(255, 0, 0)
    def __init__(self, vertices = []):
        self.vertices = vertices
        self.colors = []
        self.selected = None
    
    def __len__(self):
        return self.vertices.__len__()
    
    def append(self, vertex):
        self.vertices.append(vertex)
    
    def select(self, index):
        if index >= len(self):
            return
        self.selected = index
        
    def clearSelection(self):
        self.selected = None
    
    def getColors(self):
        colors = [self.VERTEX_COLOR for vertex in self.vertices]
        if self.selected:
            colors[self.selected] = self.SELECTED_COLOR
        return colors
    
    

class T2G_PolyPainter(QgsMapTool):
    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())
    
        self.canvas = iface.mapCanvas()
        #self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.iface = iface
        
    def canvasReleaseEvent(self, event):
  
        crsSrc = self.canvas.mapRenderer().destinationCrs()
        crsWGS = QgsCoordinateReferenceSystem(4326)
    
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        
if __name__ == "__main__":
    def printColors(vertexList):
        colors = vertexList.getColors()
        for c in colors:
            print c.red(), c.green(), c.blue()
    
    vl = T2GvertexList()
    vl.append(T2Gvertex())
    vl.append(T2Gvertex(1, 2, 3))
    vl.select(1)
    printColors(vl)
    vl.clearSelection()
    printColors(vl)
    