from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QMutex, QAbstractTableModel, Qt
from qgis.core import *
from PyQt5.QtWidgets import qApp
import vtk
import json
import re

#  some helpful regular expressions for handling wkt:
## This regular expressions pulls all numbers from a single vertex
WKT_VALUES = re.compile(r"[\d\-\.]+")
## This regular expressions can be used to discard leading and trailing text from coordinates
WKT_STRIP = re.compile(r"^\D+|\D+$")
## This regular expressions can be used to drop the last coordinate from a vertex.
#  That this is the measure is purely an assumption, this has to be used carefully.
WKT_REMOVE_MEASURE = re.compile(r" \d+(?=[,)])")
## List of wkt extensions used to indicate the available dimensions
WKT_EXTENSIONS = [' ', 'Z ', 'ZM ']


class VtkGeometry:
    pass
    # POINTGEOMETRY = 0
    # LINEGEOMETRY = 1
    # POLYGONGEOMETRY = 2
    # NULLGEOMETRY = 4
    # NOGEOMETRY = 100

class AnchorUpdater(QObject):
    # The thread uses signals to communicate its progress to the AnchorUpdateDialog
    signalGeometriesProgress = pyqtSignal(int)
    signalAnchorCount = pyqtSignal(int)
    signalAnchorProgress = pyqtSignal(int)
    signalFinished = pyqtSignal()

    ## Constructor
    #  @param parent Not used
    #  @param layer The vector layer which is to be scanned for vertices
    def __init__(self, parent=None, layer=None, geoType=None):
        super().__init__(parent)
        self.layer = layer
        self.geoType = geoType
        self.anchorPoints = []
        self.anchorIndex = QgsSpatialIndex()
        self.abort = False
        self._mutex = QMutex()
        self.geometries = []

    ## A slot to receive the 'Abort' signal from the AnchorUpdateDialog.
    @pyqtSlot()
    def abortExtraction(self):
        self._mutex.lock()
        self.abort = True
        self._mutex.unlock()

    ## The main worker method
    #  getting all features and making sure they have geometries that can be
    #  exported to wkt. This solution with expection handling has been chosen
    #  because checking 'geometry is None' leads to instant crashing (No
    #  stack trace,no exception, no nothing).
    #  The enumerator is required to update the progress bar
    def startExtraction(self):
        features = self.layer.getFeatures()
        wkts = []
        for i, feature in enumerate(features):
            geometry = feature.geometry()
            # This is ugly, I know, but as mentioned above, it works
            try:
                wkts.append(geometry.asWkt())
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
                if len(dimensions) >= 3:
                    coordinates = tuple(map(float, dimensions[:3]))
                    # this ensures that only distinct vertices are indexed
                    if coordinates not in allVertices:
                        allVertices.append(coordinates)
                        # preparing a new wkt string representing the vertex as point
                        coordText = WKT_STRIP.sub('', vertext)
                        extension = WKT_EXTENSIONS[len(dimensions) - 2]
                        anchorWkt = 'Point' + extension + '(' + coordText + ')'
                        self.anchorPoints.append(anchorWkt)
                        # creating and adding a new entry to the index. The id is
                        # synchronized with the point list
                        newAnchor = QgsFeature(pointIndex)
                        pointIndex += 1
                        # anchorPoint.fromWkt(anchorWkt)
                        newAnchor.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coordinates[0], coordinates[1])))
                        self.anchorIndex.insertFeature(newAnchor)
                self.signalAnchorCount.emit(i + 1)
                qApp.processEvents()
                if self.abort:
                    self.anchorPoints = []
                    self.anchorIndex = QgsSpatialIndex()
                    return
        self.signalFinished.emit()


def unpack_multi_polygons(geometries):
    unpacked = []
    for geo in geometries:
        if geo.asWkt().startswith('MultiPolygon'):
            coordinates = json.loads(geo.asJson()).get('coordinates', [[]])
            unpacked += coordinates[0]
            if len(coordinates) > 1:
                for i in range(1, len(coordinates)):
                    unpacked += coordinates[i]
        elif geo.asWkt().startswith('MultiLine'):
            coordinates = json.loads(geo.asJson()).get('coordinates', [[]])
            unpacked.append(coordinates[0])
            if len(coordinates) > 1:
                for i in range(1, len(coordinates)):
                    unpacked.append(coordinates[i])
        else:
            unpacked.append(list(geo.vertices()))
    # TODO: This has to go away
    # Convert points to QgsPoint
    for i in range(len(unpacked)):
        for j in range(len(unpacked[i])):
            try:
                unpacked[i][j] = QgsPoint(*unpacked[i][j])
            except:
                pass
    return unpacked


def unpack_qgspoint(point):
    if point.is3D():
        return point.x(), point.y(), point.z()
    else:
        return point.x(), point.y(), 0.0


# TODO: Polygon holes get rendered as polygon, remove layer cache code, handle 2d geometries
class VtkAnchorUpdater(AnchorUpdater):
    layer_cache = {}
    poly_data = None
    anchors = None

    def startExtraction(self):
        if self.geoType == QgsWkbTypes.PolygonGeometry:
            geometries = list([feature.geometry() for feature in self.layer.getFeatures()])
            self.signalAnchorCount.emit(len(geometries))
            active_layer_id = self.layer.id()
            if active_layer_id not in self.layer_cache.keys():
                pass
            qApp.processEvents()
            polies = vtk.vtkCellArray()
            anchors = vtk.vtkPoints()
            anchors.SetDataTypeToDouble()
            point_index = 0
            geometries = unpack_multi_polygons(geometries)
            for geometry in geometries:
                poly = vtk.vtkPolygon()
                for vertex in map(unpack_qgspoint, geometry):
                    poly.GetPointIds().InsertNextId(point_index)
                    point_index += 1
                    anchors.InsertNextPoint(*vertex)
                    self.signalAnchorCount.emit(point_index)
                    qApp.processEvents()
                    if self.abort:
                        return
                polies.InsertNextCell(poly)
            poly_data = vtk.vtkPolyData()
            poly_data.SetPoints(anchors)
            poly_data.SetPolys(polies)

            self.layer_cache[active_layer_id] = {'poly_data': poly_data, 'anchors': anchors}
            # print('loaded cache')
            self.poly_data = self.layer_cache[active_layer_id]['poly_data']
            self.anchors = self.layer_cache[active_layer_id]['anchors']
            self.polies = self.poly_data.GetPolys()

        if self.geoType == QgsWkbTypes.LineGeometry:
            geometries = list([feature.geometry() for feature in self.layer.getFeatures()])
            self.signalAnchorCount.emit(len(geometries))
            active_layer_id = self.layer.id()
            if active_layer_id not in self.layer_cache.keys():
                pass
            linePoints = vtk.vtkPoints()
            linePoints.SetDataTypeToDouble()
            cells = vtk.vtkCellArray()
            geometries = unpack_multi_polygons(geometries)
            index = 0
            for geometry in geometries:
                polyLine = vtk.vtkPolyLine()
                for vertex in map(unpack_qgspoint, geometry):
                    polyLine.GetPointIds().InsertNextId(index)
                    linePoints.InsertNextPoint(*vertex)
                    index += 1
                cells.InsertNextCell(polyLine)

            polyData = vtk.vtkPolyData()
            polyData.SetPoints(linePoints)
            polyData.SetLines(cells)

            self.layer_cache[active_layer_id] = {'poly_data': polyData, 'anchors': linePoints}
            # print('loaded cache')
            self.poly_data = self.layer_cache[active_layer_id]['poly_data']
            self.anchors = self.layer_cache[active_layer_id]['anchors']

        if self.geoType == QgsWkbTypes.PointGeometry:
            geometries = list([feature.geometry() for feature in self.layer.getFeatures()])
            self.signalAnchorCount.emit(len(geometries))
            active_layer_id = self.layer.id()
            if active_layer_id not in self.layer_cache.keys():
                pass
            points = vtk.vtkPoints()
            points.SetDataTypeToDouble()
            v_cells = vtk.vtkCellArray()
            geometries = unpack_multi_polygons(geometries)
            for geometry in geometries:
                for vertex in map(unpack_qgspoint, geometry):
                    pid = points.InsertNextPoint(*vertex)
                    v_cells.InsertNextCell(1, [pid])

            pointData = vtk.vtkPolyData()
            pointData.SetPoints(points)
            pointData.SetVerts(v_cells)
            self.layer_cache[active_layer_id] = {'poly_data': pointData, 'anchors': points}
            # print('loaded cache')
            self.poly_data = self.layer_cache[active_layer_id]['poly_data']
            self.anchors = self.layer_cache[active_layer_id]['anchors']

        self.signalFinished.emit  # unused
        return self.poly_data



