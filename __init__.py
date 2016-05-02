# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SQRCSNRC
                                 A QGIS plugin
 Search for a city name in Quebec, Canada and get the SQRC/SNRC map number
                             -------------------
        begin                : 2016-04-30
        copyright            : (C) 2016 by Patrice Pineault
        email                : patrice.pineault@usherbrooke.ca
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
    """Load SQRCSNRC class from file SQRCSNRC.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qc_sqrc_snrc import SQRCSNRC
    return SQRCSNRC(iface)
