# -*- coding: utf-8 -*-
#******************************************************************************
#
#
#******************************************************************************

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

class AddPointTool(QgsMapTool):
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