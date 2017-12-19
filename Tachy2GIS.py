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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
import os.path
from qgis.utils import iface

from T2G_PolyPainter import *
from Tachy2GIS_dialog import Tachy2GisDialog
from FieldDialog import FieldDialog
from pointProvider import PointProvider
import resources

# Initialize Qt resources from file resources.py

# Import the code for the dialog

    


class Tachy2Gis:
    
    """QGIS Plugin Implementation."""
    # Custom methods go here:
    
    def drawPoint(self):
        x, y, z = self.pointProvider.getPoint()
        self.mapTool.addVertex(None, T2G_Vertex.SOURCE_EXTERNAL, x, y, z)
        
    
    def clearCanvas(self):
        self.mapTool.clear()
        
    def dump(self):
        self.fieldDialog.populateFieldTable()
        result = self.fieldDialog.exec_()
        if result == QDialog.Accepted:
            fields = self.fieldDialog.getFields()
            return
        else:
            return
        layer = self.dlg.targetLayerComboBox.currentLayer()
        self.vertexTableModel.vertexList.dump(layer)
        self.mapTool.clear()
        layer.dataProvider().forceReload()
        layer.triggerRepaint()
        self.vertices.updateAnchors(layer)
    
    def restoreTool(self):
        if self.previousTool is None:
            self.previousTool = QgsMapToolPan(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.previousTool)
    

    def setActiveLayer(self):
        activeLayer = self.dlg.sourceLayerComboBox.currentLayer()
        if activeLayer is None:
            return
        self.iface.setActiveLayer(activeLayer)
        self.vertices.updateAnchors(activeLayer)
        self.mapTool.setGeometryType(activeLayer)
       
    
    def toggleEdit(self):
        iface.actionToggleEditing().trigger()
        
    def sourceChanged(self):
        #if self.dlg.synchCheckBox.isChecked() and not (self.dlg.sourceLayerComboBox.currentLayer() == self.dlg.targetLayerComboBox.currentLayer()):
        #    self.dlg.targetLayerComboBox.setLayer(self.dlg.sourceLayerComboBox.currentLayer())
        self.setActiveLayer()
    
    # Interface code goes here:
    def setupControls(self):
        """This method connects all controls in the UI to their callbacks.
        It is called in ad_action"""
        self.dlg.pushButton.clicked.connect(self.drawPoint)
        self.dlg.deleteAllButton.clicked.connect(self.clearCanvas)
        self.dlg.finished.connect(self.mapTool.clear)
        self.dlg.dumpButton.clicked.connect(self.dump)
        self.dlg.deleteVertexButton.clicked.connect(self.mapTool.deleteVertex)
        
        self.dlg.vertexTableView.setModel(self.vertexTableModel)
        self.dlg.vertexTableView.setSelectionModel(QItemSelectionModel(self.vertexTableModel))
        self.dlg.vertexTableView.selectionModel().selectionChanged.connect(self.mapTool.selectVertex)
        
        self.dlg.finished.connect(self.restoreTool)
        self.dlg.accepted.connect(self.restoreTool)
        self.dlg.rejected.connect(self.restoreTool)
        
        self.dlg.sourceLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer | QgsMapLayerProxyModel.WritableLayer)
        self.dlg.sourceLayerComboBox.setLayer(self.iface.activeLayer())
        self.dlg.sourceLayerComboBox.layerChanged.connect(self.sourceChanged)
        self.dlg.sourceLayerComboBox.layerChanged.connect(self.mapTool.clear)
         
        """
        self.dlg.targetLayerComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer | QgsMapLayerProxyModel.WritableLayer)
        self.dlg.targetLayerComboBox.setLayer(self.iface.activeLayer())
        self.dlg.targetLayerComboBox.layerChanged.connect(self.setDumpEnabled)
        self.dlg.targetLayerComboBox.layerChanged.connect(self.mapTool.clear)
        """

    
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
        self.menu = self.tr(u'&Tachy2GIS')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Tachy2Gis')
        self.toolbar.setObjectName(u'Tachy2Gis')
        
        ## From here: Own additions
        self.pointProvider = PointProvider()
        self.vertices = T2G_VertexList()
        
        self.vertexTableModel = T2G_VertexTableModel(self.vertices)
        self.mapTool = T2G_PolyPainter(self)
        self.previousTool = None
        self.fieldDialog = FieldDialog(self.iface.activeLayer())
        crs = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
        #self.vertexLayer = QgsVectorLayer("Point?crs=" + crs, "vertices", "memory")
        #self.vertexLayer.dataProvider().addAttributes([QgsField("z", QVariant.Double)])
        #self.vertexLayer.updateFields()
        
        

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
        self.dlg = Tachy2GisDialog()
        self.setupControls()

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
            text=self.tr(u'Tachy2GIS'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Tachy2GIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
     
        # show the dialog
        self.previousTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.sourceChanged()
        self.setActiveLayer()
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        
        
