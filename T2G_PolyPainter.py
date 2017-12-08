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
import os.path
import re
from shapely import wkt

WKT_VALUES = re.compile(r"[\d\-\.]+")
WKT_STRIP = re.compile(r"^\D+|\D+$")

try:
    import shapefile
except ImportError:
    print 'Please install pyshp from https://pypi.python.org/pypi/pyshp/ to handle shapefiles'
    raise

def extractAnchors(layer):
    wkts = [feature.geometry().exportToWkt() for feature in layer.getFeatures()]
    allVertices = []
    anchorWkts = []
    extensions = [' ', 'Z ', 'MZ ']
    for wkt in wkts:
        for part in wkt.split(','):
            dimensions = WKT_VALUES.findall(part)
            coordinates = tuple(map(float, dimensions[:3]))
            if coordinates not in allVertices:
                allVertices.append(coordinates)
                coordText = WKT_STRIP.sub('', part)
                extension = extensions[len(dimensions) - 2]
                anchorWkts.append('Point' + extension + '(' + coordText + ')')
    return allVertices, anchorWkts




## This class handles individual vertices for data acquisition and visualization
#
class T2G_Vertex():
    ## String constant to identify manually generated vertices
    SOURCE_INTERNAL = 'Man.'
    ## String constant to identify automatically generated vertices
    SOURCE_EXTERNAL = 'Ext.'
    ## Manually generated vertices get a 'box' icon
    SHAPE_INTERNAL = QgsVertexMarker.ICON_BOX
    ## Vertices from an external source get an 'X'
    SHAPE_EXTERNAL =QgsVertexMarker.ICON_X
    ## Mapping source keywords to the corresponding shapes.
    SHAPE_MAP = {SOURCE_INTERNAL: SHAPE_INTERNAL,
                 SOURCE_EXTERNAL: SHAPE_EXTERNAL}
    
    
    
    ## Constructor
    # @param label Point number or identifier
    # @param source Should be one of the defined source keywords
    # @param x,y,z Vertex coordinates
    def __init__(self, label = None, source = None, x = None, y = None, z = None, wkt = ""):
        self.label = str(label)
        self.source = source
        self.x = x
        self.y = y
        self.z = z
        self.wkt = wkt
        self.wktDimensions = 0
        if not wkt == "":
            dimensions = WKT_VALUES.findall(wkt)
            self.x, self.y, self.z = map(float, dimensions[:3])
            self.wktDimensions = len(dimensions)
        ### Headers for a table model
        self.headers = ['#', 'Source', 'x', 'y', 'z']
    

    ## list of fields used to feed a table model
    def fields(self):
        return [self.label, self.source, self.x, self.y, self.z]
    
    def getQpoint(self):
        return QgsPoint(self.x, self.y)
    
    def setXyz(self, xyz):
        self.x, self.y, self.z = xyz
    
    def setWkt(self, wkt):
        self.wkt = wkt
        dimensions = WKT_VALUES.findall(wkt)
        self.x, self.y, self.z = map(float, dimensions[:3])
        self.wktDimensions = len(dimensions)
    
    def getMarker(self, canvas):
        marker = QgsVertexMarker(canvas)
        marker.setCenter(self.getQpoint())
        marker.setIconType(self.SHAPE_MAP[self.source])
        return marker

## The T2G_VertexList handles the painting and selection of vertices

#  it also pulls existing vertices from a shapefile to use them as anchors when
#  manually creating vertices.
class T2G_VertexList():
    ## The color of unselected vertices
    VERTEX_COLOR = QColor(0, 255, 0)
    ### Selected vertices get a different color
    SELECTED_COLOR = QColor(255, 0, 0)
    
    
    def __init__(self, vertices = []):
        self.vertices = vertices
        self.colors = []
        self.shapes = []
        self.anchorPoints = []
        self.anchorIndex = QgsSpatialIndex()
        self.selected = None
        self.maxIndex = None
    
#     def refreshIndex(self):
#         self.maxIndex = len(self.vertices) - 1
#     
    def updateAnchors(self, layer):
        self.anchorIndex = QgsSpatialIndex()
        self.anchorPoints = []
        if layer is None:
            return
        i = 0
        vertices, wkts = extractAnchors(layer)
        for vertex, wkt in zip(vertices, wkts):
            newAnchor = QgsFeature(i)
            i += 1
    
            newAnchor.setGeometry(QgsGeometry.fromPoint(QgsPoint(vertex[0], vertex[1])))

            self.anchorIndex.insertFeature(newAnchor)
            self.anchorPoints.append(wkt)
    
    def __len__(self):
        return self.vertices.__len__()
    
    def __getitem__(self, index):
        return self.vertices.__getitem__(index)
    
    def append(self, vertex):
        if vertex.source == T2G_Vertex.SOURCE_INTERNAL:
            anchorId = self.anchorIndex.nearestNeighbor(QgsPoint(vertex.x,vertex.y), 1)
            if anchorId:
                wkt = self.anchorPoints[anchorId[0]]
                vertex.setWkt(wkt)
        self.vertices.append(vertex)
        return vertex
    
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
    
    def getParts(self):
        return [[[v.x, v.y, v.z] for v in self.vertices]]
    
    def dumpToFile(self, targetLayer):
        if targetLayer is None:
            return
        if not targetLayer.dataProvider().name() == u'ogr':
            return
        dataUri = targetLayer.dataProvider().dataSourceUri()
        targetFileName = os.path.splitext(dataUri.split('|')[0])[0]
        reader = shapefile.Reader(targetFileName)
        writer = shapefile.Writer(shapefile.POLYGONZ)
        writer.fields = list(reader.fields)
        writer.records.extend(reader.records())
        writer._shapes.extend(reader.shapes())
        l = len(writer.shapes())
        vertexParts = self.getParts()
        writer.poly(parts = vertexParts, shapeType = shapefile.POLYGONZ)
        writer.record(id=8)
        l = len(writer.shapes())
        writer.save(targetFileName)
        

class T2G_VertexTableModel(QAbstractTableModel):
    def __init__(self, vertexList, parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.columnCount = len(T2G_Vertex().fields())
        self.vertexList = vertexList

    def rowCount(self, *args, **kwargs):
        return len(self.vertexList)
    
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
        vertex = self.vertexList[row]
        field = vertex.fields()[col]
        return field
    
    def addVertex(self, vertex):
        adjusted = self.vertexList.append(vertex)
        self.layoutChanged.emit()
        return adjusted
    
    def headerData(self, section, orientation, role):
        if Qt is None:
            return
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = T2G_Vertex().headers
            return headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def clear(self):
        self.vertexList.clear()
        self.layoutChanged.emit()
## T2G_PolyPainter
#
# This is the map tool that allows the plugin to draw shapes on the map canvas
# while they are recorded.
class T2G_PolyPainter(QgsMapTool):
    ## Rubberband color
    RB_COLOR = Qt.red
    ## Rubberband fill color, alpha set to 50%
    RB_FILLCOLOR = QColor(255, 0, 0, 127)
    def __init__(self, parent): #tableModel, vertexIndex, zIndex):
        
        QgsMapTool.__init__(self, parent.iface.mapCanvas())
        self.parent = parent
        self.canvas = parent.iface.mapCanvas()
        #self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.tableModel = parent.vertexTableModel
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setColor(self.RB_COLOR)
        self.rubberBand.setFillColor(self.RB_FILLCOLOR)
        self.rubberBand.setWidth(1)
        self.markers = []
        self.reset()
    
    ## Reset the rubber band and clean up markers
    def reset(self):
        self.rubberBand.reset(QGis.Polygon)
        self.markers = []
    
    
    ## Adds a new vertex to the attached table model, the rubber band and the vertex markers
    def addVertex(self, label = None, source = None, x = None, y = None, z = None):
        vertex = T2G_Vertex(label, source, x, y, z)
        adjusted = self.tableModel.addVertex(vertex)
        self.rubberBand.addPoint(adjusted.getQpoint(), True)
        self.markers.append(adjusted.getMarker(self.canvas))
    
    ## Removes all markers, resets the rubber band and clears the table model 
    def clear(self):
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.reset()
        self.tableModel.clear()
        
    ## Finds the nearest existing 3D vertex, and adds it to the vertex list
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
    wktv = T2G_Vertex(wkt = '552364.36630000011064112 5921140.47400000039488077 49.57150000000000034 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368')
    print vl[0].wktDimensions
    print wktv.wktDimensions