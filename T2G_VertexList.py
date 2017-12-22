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
from AnchorUpdateDialog import AnchorUpdateDialog

WKT_VALUES = re.compile(r"[\d\-\.]+")
WKT_STRIP = re.compile(r"^\D+|\D+$")
WKT_REMOVE_MEASURE = re.compile(r" \d+(?=[,)])")
WKT_EXTENSIONS = [' ', 'Z ', 'ZM ']

try:
    import shapefile
except ImportError:
    print 'Please install pyshp from https://pypi.python.org/pypi/pyshp/ to handle shapefiles'
    raise
## Updating anchor points that are used to enable snapping when manually adding 
#  geometries is delegated to its own thread. This class is required to do that.
class AnchorUpdater(QObject):
    # The thread uses signals to communicate its progress to the AnchorUpdateDialog
    signalGeometriesProgress = pyqtSignal(int)
    signalAnchorCount = pyqtSignal(int)
    signalAnchorProgress = pyqtSignal(int)
    signalFinished = pyqtSignal()
    
    ## Constructor
    #  @param parent Not used
    #  @param layer The vector layer which is to be scanned for vertices    
    def __init__(self, parent = None, layer = None):
        super(self.__class__, self).__init__(parent)
        self.layer = layer
        self.anchorPoints = []
        self.anchorIndex = QgsSpatialIndex()
        self.abort = False
        self._mutex =QMutex()
    
    
    ## A slot to receive the 'Abort' signal from the AnchorUpdateDialog
    @pyqtSlot()
    def abortExtraction(self):
        self._mutex.lock()
        self.abort = True
        self._mutex.unlock()

    def startExtraction(self):
        features = self.layer.getFeatures()
        # getting all features and making sure they have geometries that can be
        # exported to wkt. This solution with expection handling has been chosen
        # because checking 'geometry is None' leads to instant crashing (No
        # stack trace,no exception, no nothing).
        # The enumerator is required to update the progress bar
        wkts = []
        for i, feature in enumerate(features):
            geometry = feature.geometry()
            try:
                wkts.append(geometry.exportToWkt())
            except:
                pass
            self.signalGeometriesProgress.emit(i)
            # frequently forcing event processing is required to actually update
            # the progress bars and to be able to receive the abort signal 
            qApp.processEvents()
            if self.abort: 
                self.anchorPoints = []
                self.anchorIndex = QgsSpatialIndex()
                return
        allVertices = []
        
        pointIndex = 0
        self.signalAnchorCount.emit(len(wkts))
        for i, wkt in enumerate(wkts):
            # The feature wtk strings are broken into their vertices 
            for vertext in wkt.split(','):
                # a regex pulls out the numbers, of which the first three are mapped to float
                dimensions = WKT_VALUES.findall(vertext)
                coordinates = tuple(map(float, dimensions[:3]))
                # this ensures that only distinct vertices are indexed
                if coordinates not in allVertices:
                    allVertices.append(coordinates)
                    # preparing a new wkt string representing the vertex as point
                    coordText = WKT_STRIP.sub('', vertext)
                    extension = WKT_EXTENSIONS[len(dimensions) - 2]
                    self.anchorPoints.append('Point' + extension + '(' + coordText + ')')
                    # creating and adding a new entry to the index. The id is 
                    # synchronized with the point list 
                    newAnchor = QgsFeature(pointIndex)
                    pointIndex += 1
                    newAnchor.setGeometry(QgsGeometry.fromPoint(QgsPoint(coordinates[0], coordinates[1])))
                    self.anchorIndex.insertFeature(newAnchor)
                self.signalAnchorCount.emit(i)
                qApp.processEvents()
                if self.abort: 
                    self.anchorPoints = []
                    self.anchorIndex = QgsSpatialIndex()
                    return
        self.signalFinished.emit()
        

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
    #  @param label Point number or identifier
    #  @param source Should be one of the defined source keywords
    #  @param x,y,z Vertex coordinates
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
    
    ## Returns a 2D QgsPoint. Currently only used in getMarker()
    def getQpoint(self):
        return QgsPoint(self.x, self.y)
    
    def setXyz(self, xyz):
        self.x, self.y, self.z = xyz
    
    ## Sets the vertex' coordinates from Well Known Text
    #  @param wkt A string containing at least two numbers
    def setWkt(self, wkt):
        self.wkt = wkt
        # a regex extracts all numbers from the wkt
        dimensions = WKT_VALUES.findall(wkt)
        # x and y are assumed to be present
        self.x, self.y = map(float, dimensions[:2])
        self.wktDimensions = len(dimensions)
        # if there are at least three dimensions, z is extracted as well
        if self.wktDimensions >= 3:
            self.z = float(dimensions[2])
        else:
            self.z = None
    
    ## Gives you a marker to draw on the map canvas. The shape depends on the
    #  source of the vertex, to help distinguishing between manually created
    #  vertices and external ones
    def getMarker(self, canvas):
        marker = QgsVertexMarker(canvas)
        marker.setCenter(self.getQpoint())
        marker.setIconType(self.SHAPE_MAP[self.source])
        return marker
    
    ## Returns the points' coordinates as a tuple. The tuple's length corresponds
    #  to the actually populated dimensions to avoid upsetting the shapefile export.
    def getCoords(self):
        if self.wktDimensions == 2:
            return (self.x, self.y)
        else:
            return (self.x, self.y, self.z)


## The T2G_VertexList handles the painting and selection of vertices
#  it also pulls existing vertices from a vector layer to use them as anchors when
#  manually creating vertices.
class T2G_VertexList(QAbstractTableModel):
    ## The color of unselected vertice
    VERTEX_COLOR = Qt.red
    ### Selected vertices get a different color
    SELECTED_COLOR = Qt.green
    
    
    def __init__(self, vertices = [], parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.columnCount = len(T2G_Vertex().fields())
        self.vertices = vertices
        self.colors = []
        self.shapes = []
        self.anchorPoints = []
        self.anchorIndex = QgsSpatialIndex()
        self.selected = None
        self.maxIndex = None
        self.updateThread = QThread()
        self.anchorUpdater = None
        
    def rowCount(self, *args, **kwargs):
        return len(self)
    
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
        field = vertex.fields()[col]
        return field
    
    def headerData(self, section, orientation, role):
        if Qt is None:
            return
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = T2G_Vertex().headers
            return headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    
    
    ## this method updates anchor points for snapping
    #  extracting all vertices from the geometeries in a layer may take some time,
    #  so the method report its progress via a dialog. The process is time consuming,
    #  because it relies on wkt export to access the vertices.
    #  
    #  @param layer: The currently active layer
    def updateAnchors(self, layer):
        ## Snapping is driven by a spatial index of all distinct existing vertices
        #  the index is 2D only, so 3-4D information has to be stored elsewhere
        #  (self.anchorPoints in this case).
        #  self.anchorPoints holds wkt representation of all vertices that can be 
        #  passed to the ctor of a new T2G_Vertex. 
        self.anchorIndex = QgsSpatialIndex()
        self.anchorPoints = []
        if layer is None:
            # empty or noneexisting layers leave us with an empty point list and index.
            return
        # Initializing and displaying the progress dialog
        aud = AnchorUpdateDialog()
        aud.abortButton.clicked.connect(self.abortUpdate)
        aud.geometriesBar.setMaximum(layer.featureCount())
        aud.geometriesBar.setValue(0)
        aud.anchorBar.setValue(0)
        # the layer is passed to the anchorUpdater and the updater is moved to
        # a new thread
        self.anchorUpdater = AnchorUpdater(layer = layer)
        self.anchorUpdater.moveToThread(self.updateThread)
        self.updateThread.start()
        self.anchorUpdater.signalAnchorCount.connect(aud.setAnchorCount)
        self.anchorUpdater.signalAnchorProgress.connect(aud.anchorProgress)
        self.anchorUpdater.signalGeometriesProgress.connect(aud.geometriesProgress)
        aud.show()
        self.anchorUpdater.startExtraction()
        # the abort method of the updater clears its index and points list, so
        # we can just use them, even if we aborted. They will be empty in that 
        # case. 
        self.anchorIndex = self.anchorUpdater.anchorIndex
        self.anchorPoints = self.anchorUpdater.anchorPoints
        
    def hasAnchors(self):
        return len(self.anchorPoints) > 0
    
    @pyqtSlot()
    def abortUpdate(self):
        if self.updateThread.isRunning():
            self.anchorUpdater.abortExtraction()
            self.updateThread.terminate()
            self.updateThread.wait()
    
    
    def __len__(self):
        return self.vertices.__len__()
    
    def __getitem__(self, index):
        return self.vertices.__getitem__(index)
    
    def addVertex(self, vertex):
        adjusted = self.vertexList.append(vertex)
        
        return adjusted
    
    def append(self, vertex):
        if vertex.source == T2G_Vertex.SOURCE_INTERNAL:
            anchorId = self.anchorIndex.nearestNeighbor(QgsPoint(vertex.x,vertex.y), 1)
            if anchorId:
                wkt = self.anchorPoints[anchorId[0]]
                vertex.setWkt(wkt)
        self.vertices.append(vertex)
        self.layoutChanged.emit()
        return vertex
    
    def deleteVertex(self, index):
        del self.vertices[index]
        self.layoutChanged.emit()
    
    def select(self, index):
        if index >= len(self):
            return
        self.selected = index
        
    def clearSelection(self):
        self.selected = None
    
    def getColors(self):
        colors = []
        for i, vertex in enumerate(self.vertices):
            if i == self.selected:
                colors.append(self.SELECTED_COLOR)
            else:
                colors.append(self.VERTEX_COLOR)
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
        self.layoutChanged.emit()
    
    def getParts(self):
        return [[v.getCoords() for v in self.vertices]]
    
    def dump(self, targetLayer, fieldMap):
        if targetLayer is None:
            return
        if targetLayer.geometryType() == QGis.Polygon:
            wkts = [vertex.wkt for vertex in self.vertices]
            coordinates = [WKT_STRIP.sub('', wkt) for wkt in wkts]
            coordinates.append(coordinates[0])
                
            wktType = 'Polygon'
            extension = WKT_EXTENSIONS[self.vertices[0].wktDimensions - 2]
            parts = '((' + ','.join(coordinates) + '))'
        
        newWkt = wktType + extension + parts
        newFeature = QgsFeature(targetLayer.pendingFields())
        for name, value in fieldMap:
            newFeature.setAttribute(name, value)
        newGeometry = QgsGeometry.fromWkt(newWkt)
        newFeature.setGeometry(newGeometry)
        success, features = targetLayer.dataProvider().addFeatures([newFeature])
        if not success:
            newWkt = WKT_REMOVE_MEASURE.sub('', newWkt)
            newWkt = newWkt.replace('ZM', 'Z')
            newGeometry = QgsGeometry.fromWkt(newWkt)
            newFeature.setGeometry(newGeometry)
            targetLayer.dataProvider().addFeatures([newFeature])
            pass
        

    def writePoly(self, reader):
        if self.vertices[0].wktDimensions > 2:
            shapeType = shapefile.POLYGONZ
        else:
            shapeType = shapefile.POLYGON
        writer = shapefile.Writer(shapeType)
        writer.fields = list(reader.fields)
        writer.records.extend(reader.records())
        writer._shapes.extend(reader.shapes())
        vertexParts = self.getParts()
        writer.poly(parts=vertexParts, shapeType=shapeType)
        return writer
    
    def writeLine(self, reader):
        if self.vertices[0].wktDimensions > 2:
            shapeType = shapefile.POLYLINEZ
        else:
            shapeType = shapefile.POLYLINE
        writer = shapefile.Writer(shapeType)
        writer.fields = list(reader.fields)
        writer.records.extend(reader.records())
        writer._shapes.extend(reader.shapes())
        vertexParts = self.getParts()
        writer.line(parts=vertexParts, shapeType=shapeType)
        return writer
    
    def writePoint(self, reader):
        if self.vertices[0].wktDimensions > 2:
            shapeType = shapefile.POINTZ
        else:
            shapeType = shapefile.POINT
        writer = shapefile.Writer(shapeType)
        writer.fields = list(reader.fields)
        writer.records.extend(reader.records())
        writer._shapes.extend(reader.shapes())
        coords = self.vertices[self.selected].getCoords()
        writer.point(*coords, shapeType=shapeType)
        return writer

    def dumpToFile(self, targetLayer, fieldData):
        if targetLayer is None:
            return
        if not targetLayer.dataProvider().name() == u'ogr':
            return
        dataUri = targetLayer.dataProvider().dataSourceUri()
        targetFileName = os.path.splitext(dataUri.split('|')[0])[0]
        reader = shapefile.Reader(targetFileName)
        targetType = reader.shapeType
        if targetType in (shapefile.POLYGON, shapefile.POLYGONZ):
            writer = self.writePoly(reader)
        elif targetType in (shapefile.POLYLINE, shapefile.POLYLINEZ):
            writer = self.writeLine(reader)
        elif targetType in (shapefile.POINT, shapefile.POINTZ):
            writer = self.writePoint(reader)
            
        else:
            return
        #writer.record(recordDict = dict(fieldMap))
        writer.record(*fieldData)
        writer.save(targetFileName)
        