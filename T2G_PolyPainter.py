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



class T2G_Vertex():
    SOURCE_INTERNAL = 'Man.'
    SOURCE_EXTERNAL = 'Ext.'
    SHAPE_INTERNAL = QgsVertexMarker.ICON_BOX
    SHAPE_EXTERNAL =QgsVertexMarker.ICON_X
    SHAPE_MAP = {SOURCE_INTERNAL: SHAPE_INTERNAL,
                 SOURCE_EXTERNAL: SHAPE_EXTERNAL}
    
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
    
    def getMarker(self, canvas):
        marker = QgsVertexMarker(canvas)
        marker.setCenter(self.getQpoint())
        marker.setIconType(self.SHAPE_MAP[self.source])
        return marker
    
class T2G_VertexList():
    VERTEX_COLOR = QColor(0, 255, 0)
    SELECTED_COLOR = QColor(255, 0, 0)
    
    
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
    
    def __getitem__(self, index):
        return self.vertices.__getitem__(index)
    
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
            if vertex.source == T2G_Vertex.SOURCE_EXTERNAL:
                shapes.append(self.SHAPE_EXTERNAL)
            else:
                shapes.appen(self.SHAPE_INTERNAL)
        return shapes
    
    def clear(self):
        self.vertices = []
        self.refreshIndex()

class T2G_VertexTableModel(QAbstractTableModel):
    def __init__(self, vertexList, parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.columnCount = len(T2G_Vertex().fields)
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
            headers = T2G_Vertex().headers
            return headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def clear(self):
        self.vertices.clear()
        self.layoutChanged.emit()
        

class T2G_PolyPainter(QgsMapTool):
    RB_COLOR = Qt.red
    RB_FILLCOLOR = QColor(255, 0, 0, 127)
    def __init__(self, iface, tableModel):
        QgsMapTool.__init__(self, iface.mapCanvas())
    
        self.canvas = iface.mapCanvas()
        #self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.iface = iface
        self.tableModel = tableModel
        self.vertices = self.tableModel.vertices
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setColor(self.RB_COLOR)
        self.rubberBand.setFillColor(self.RB_FILLCOLOR)
        self.rubberBand.setWidth(1)
        self.markers = []
        self.reset()
    
    def reset(self):
        self.rubberBand.reset(QGis.Polygon)
        self.markers = []
    
        
    def addVertex(self, label = None, source = None, x = None, y = None, z = None):
        vertex = T2G_Vertex(label, source, x, y, z)
        self.rubberBand.addPoint(vertex.getQpoint(), True)
        self.tableModel.addVertex(vertex)
        self.markers.append(vertex.getMarker(self.canvas))
    
    def clear(self):
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.reset()
        self.tableModel.clear()
        
        
    def canvasReleaseEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        
        self.addVertex(None, T2G_Vertex.SOURCE_INTERNAL, point.x(), point.y(), None)
    
    """
    def activate(self, *args, **kwargs):
        super(T2G_PolyPainter, self).activate()
        
    def deativate(self):
        self.clear()
        super(T2G_PolyPainter, self).deactivate()
        self.emit(SIGNAL("deactivated()"))
    """
        
if __name__ == "__main__":
    def printColors(vertexList):
        colors = vertexList.getColors()
        for c in colors:
            print c.red(), c.green(), c.blue()
    
    vl = T2G_VertexList()
    vl.append(T2G_Vertex())
    vl.append(T2G_Vertex(1, 2, 3))
    vl.select(1)
    printColors(vl)
    vl.clearSelection()
    printColors(vl)
    