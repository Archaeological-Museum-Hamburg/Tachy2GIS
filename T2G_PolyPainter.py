# -*- coding: utf-8 -*-
#******************************************************************************
#
#
#******************************************************************************
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from docutils.parsers.rst.roles import role



class T2Gvertex():
    SOURCE_INTERNAL = 'Man.'
    SOURCE_EXTERNAL = 'Ext.'
    def __init__(self, label = None, source = None, x = None, y = None, z = None):
        self.label = str(label)
        self.source = source
        self.x = x
        self.y = y
        self.z = z
        self.fields = [self.label,
                       self.source,
                       self.x,
                       self.y,                       
                       self.z]
        self.headers = ['#', 'Source', 'x', 'y', 'z']
        
    def getQpoint(self):
        return QgsPoint(self.x, self.y)
    
    def getMarker(self):
        pass
    
class T2GvertexList():
    VERTEX_COLOR = QColor(0, 255, 0)
    SELECTED_COLOR = QColor(255, 0, 0)
    SHAPE_INTERNAL = QgsVertexMarker.ICON_BOX
    SHAPE_EXTERNAL =QgsVertexMarker.ICON_X
    
    def __init__(self, vertices = []):
        self.vertices = vertices
        self.colors = []
        self.shapes = []
        self.selected = None
        self.maxIndex = None
    
    def refreshIndex(self):
        self.maxIndex = len(self.vertices) - 1
    
    def __len__(self):
        return self.vertices.__len__()
    
    def __getitem__(self, key):
        return self.vertices[key]
    
    def append(self, vertex):
        self.vertices.append(vertex)
        self.refreshIndex()
    
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
    
    def getShapes(self):
        shapes = []
        for vertex in self.vertices:
            if vertex.source == T2Gvertex.SOURCE_EXTERNAL:
                shapes.append(self.SHAPE_EXTERNAL)
            else:
                shapes.appen(self.SHAPE_INTERNAL)
        return shapes

class VertexTableModel(QAbstractTableModel):
    def __init__(self, vertexList, parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.columnCount = len(T2Gvertex().fields)
        self.vertices = vertexList

    def rowCount(self, *args, **kwargs):
        return len(self.vertices)
    
    def columnCount(self, *args, **kwargs):
        return self.columnCount
    
    def data(self, index, role):
        if Qt is None:
            return
        if not index.isValid():
            return
        elif role != Qt.DisplayRole:
            return
        row = index.row()
        col = index.column()
        vertex = self.vertices[row]
        field = vertex.fields[col]
        return field
    
    def addVertex(self, vertex):
        self.vertices.append(vertex)
        self.layoutChanged.emit()
    
    def headerData(self, section, orientation, role):
        if Qt is None:
            return
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = T2Gvertex().headers
            return headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
        #return QVariant()
        

class T2G_PolyPainter(QgsMapTool):
    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())
    
        self.canvas = iface.mapCanvas()
        #self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.iface = iface
        self.vertices = T2GvertexList()
        self.vertexTableModel = VertexTableModel(self.vertices)
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.reset()
    
    def reset(self):
        self.rubberBand.reset(QGis.Polygon)
        
    def addVertex(self, label = None, source = None, x = None, y = None, z = None):
        vertex = T2Gvertex(label, source, x, y, z)
        self.vertexTableModel.addVertex(vertex)
        
        
    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        self.addVertex(None, T2Gvertex.SOURCE_INTERNAL, point.x(), point.y(), None)
        
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
    