import os

import qgis.core as qgc

from qgreenland.constants import BBOX, PROJECT_CRS, REQUEST_TIMEOUT
from qgreenland.util.edl import create_earthdata_authenticated_session


def fetch_file(url):
    # TODO: Share the session across requests somehow?
    s = create_earthdata_authenticated_session(hosts=[url])

    return s.get(url, timeout=REQUEST_TIMEOUT)


def make_qgs(layers_cfg, path):
    """Create a QGIS project file with the correct stuff in it.

    path: the desired path to .qgs project file, e.g.:
          /luigi/data/qgreenland/qgreenland.qgs

    Developed from examples:

        https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
    """
    # The qgreenland .qgs project file will live at the root of the qgreenland
    # package distributed to end users.
    ROOT_PATH = os.path.dirname(path)
    # TODO: Reconsider normpath
    PROJECT_PATH = os.path.normpath(os.path.join(path))

    # Write your code here to load some layers, use processing algorithms, etc.
    project = qgc.QgsProject.instance()

    # Create a new project; initializes basic structure
    project.write(PROJECT_PATH)
    # An existing project can be opened w/ the `load` method

    # write the project coordinate ref system.
    project_crs = qgc.QgsCoordinateReferenceSystem(PROJECT_CRS)
    project.setCrs(project_crs)

    # Set the default extent. Eventually we may want to pull the extent directly
    # from the configured 'map frame' layer.
    view = project.viewSettings()
    extent = qgc.QgsReferencedRectangle(qgc.QgsRectangle(*BBOX.values()),
                                        project_crs)
    view.setDefaultViewExtent(extent)

    basemap_group = project.layerTreeRoot().addGroup('basemap')

    groups = {
        'basemaps': basemap_group,
        'TBD': None,
    }
    # TODO: Parameterize, e.g. below
    #       But then how would we get the ProviderType/ProviderLib?
    #       Just more mapping. But where do we put it? Wrapper class?
    # layer_constructors = {
    #     'raster': qgc.QgsRasterLayer,
    #     'vector': qgc.QgsVectorLayer,
    # }

    for layer_name, layer_cfg in layers_cfg.items():
        layer_path = os.path.join(ROOT_PATH,
                                  layer_cfg['layer_group'],
                                  layer_name,
                                  f"{layer_name}.{layer_cfg['file_type']}")
        # construct a relative path to the coastline layer.
        # TODO: do we need to worry about differences in path structure between linux
        # and windows?
        layer_relpath = os.path.relpath(layer_path, start=os.path.dirname(PROJECT_PATH))

        # https://qgis.org/pyqgis/master/core/QgsVectorLayer.html
        if layer_cfg['data_type'] == 'vector':
            map_layer = qgc.QgsVectorLayer(
                layer_relpath,
                layer_cfg['name'],  # layer name as it shows up in TOC
                'ogr'  # name of the data provider (memory, postgresql)
            )
        elif layer_cfg['data_type'] == 'raster':
            map_layer = qgc.QgsRasterLayer(
                layer_relpath,
                layer_cfg['name'],
                'gdal'
            )

        map_layer.setCrs(project_crs)

        group = groups[layer_cfg['layer_group']]
        group.addLayer(map_layer)

        # TODO is this necessary? Without adding the map layer to the project (which
        # automatically adds it to the root layer unless `addToLegend` is `False`), the
        # layer added to the basemap does not render.
        project.addMapLayer(map_layer, addToLegend=False)

    # TODO: is it normal to write multiple times?
    project.write()
