# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Tachy2Gis
                                 A QGIS plugin
 This plugin allows to create geometries directly with a connected tachymeter
                             -------------------
        begin                : 2017-11-26
        copyright            : (C) 2017 by Christian Trapp
        email                : mail@christiantrapp.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Tachy2Gis class from file Tachy2Gis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Tachy2GIS import Tachy2Gis
    return Tachy2Gis(iface)
