# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS Line Trimmer
                                 A QGIS plugin
 Um plugin para QGIS que corta automaticamente linhas quando elas se cruzam durante a vetorização.
                             -------------------
        begin                : 2025-07-30
        copyright            : (C) 2025 by Your Name
        email                : your.email@example.com
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
    """Load LineTrimmer class from file LineTrimmer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .line_trimmer import LineTrimmer
    return LineTrimmer(iface)

