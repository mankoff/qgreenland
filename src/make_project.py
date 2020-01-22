"""
Developed from examples: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
"""
import os

from qgis.core import (QgsApplication, QgsProject,
                       QgsVectorLayer, QgsCoordinateReferenceSystem,
                       QgsReferencedRectangle, QgsRectangle)

import qgis.core as qgc


PROJECT_CRS = 'EPSG:3411'

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
LAYER_BASE_DIR = os.path.abspath(os.path.join(THIS_DIR, '../qgis-data/qgreenland/'))

# The qgreenland .qgs project file will (proably?) live at the root of the
# qgreenland package distributed to end users.
PROJECT_PATH = os.path.normpath(os.path.join(THIS_DIR,
                                             '..',
                                             'qgis-data',
                                             'qgreenland',
                                             'qgreenland.qgs'))
# TODO get this from config.
LAYER_PATH = os.path.join(LAYER_BASE_DIR, 'basemap/ne_coastlines/ne_coastlines.shp')

# TODO how to get this path programatically?
QgsApplication.setPrefixPath('/home/trst2284/miniconda3/envs/qgis/', True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Write your code here to load some layers, use processing
# algorithms, etc.

project = QgsProject.instance()

# Create a new project
project.write(PROJECT_PATH)
# An existing project can be opened w/ the `load` method

# write the project coordinate ref system.
project_crs = QgsCoordinateReferenceSystem(PROJECT_CRS)
project.setCrs(project_crs)

# Set the default extent. Eventually we may want to pull the extent directly
# from the configured 'map frame' layer.
view = project.viewSettings()
extent = QgsReferencedRectangle(QgsRectangle(-3850000.000,
                                             -5350000.0,
                                             3750000.0,
                                             5850000.000),
                                project_crs)
view.setDefaultViewExtent(extent)

# construct a relative path to the coastline layer.
# TODO: do we need to worry about differences in path structure between linux
# and windows?
coastline_path = os.path.relpath(LAYER_PATH, start=os.path.dirname(PROJECT_PATH))

# https://qgis.org/pyqgis/master/core/QgsVectorLayer.html
map_layer = QgsVectorLayer(coastline_path,
                           'Coastlines',  # layer name as it shows up in TOC
                           'ogr')  # name of the data provider (memory, postgresql)

# Create 'basemap' Layer Group.
basemap_group = project.layerTreeRoot().addGroup('basemap')
basemap_group.addLayer(map_layer)

# TODO is this necessary? Without adding the map layer to the project (which
# automatically adds it to the root layer unless `addToLegend` is `False`), the
# layer added to the basemap does not render.
project.addMapLayer(map_layer, addToLegend=False)

project.write()

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
