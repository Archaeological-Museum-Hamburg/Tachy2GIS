"""
/***************************************************************************
Name			 	 : Tachy2Gis
Description          : Allows to enter shapes directly via a connected tachymeter
Date                 : 26/Nov/17 
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
from PyQt4 import QtCore, QtGui 
from Ui_Tachy2GIS import Ui_Tachy2GIS
# create the dialog for Tachy2GIS
class Tachy2GISDialog(QtGui.QDialog):
  def __init__(self): 
    QtGui.QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    self.ui = Ui_Tachy2GIS ()
    self.ui.setupUi(self)