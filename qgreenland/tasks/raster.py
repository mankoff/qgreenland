import os

import geopandas
import luigi
import rasterio as rio
from earthpy import spatial as eps
from osgeo import gdal
from shapely.geometry import Polygon

from qgreenland.constants import TaskType
from qgreenland.tasks.common import FetchData
from qgreenland.util import BBOX_POLYGON, LayerConfigMixin, PROJECT_CRS


class ReprojectRaster(LayerConfigMixin, luigi.Task):
    task_type = TaskType.WIP

    def requires(self):
        return FetchData(self.layer_cfg)

    def output(self):
        # TODO: may not always be .tif
        of = os.path.join(self.outdir, 'reprojected.tif')
        return luigi.LocalTarget(of)

    def run(self):
        gdal.Warp(self.output().path, self.input().path,
                  dstSRS=PROJECT_CRS,
                  resampleAlg='bilinear')


class SubsetRaster(LayerConfigMixin, luigi.Task):
    task_type = TaskType.WIP

    def requires(self):
        return ReprojectRaster(self.layer_cfg)

    def output(self):
        # TODO: may not always be .tif
        of = os.path.join(self.outdir, 'subset.tif')
        return luigi.LocalTarget(of)

    def run(self):
        with rio.open(self.input().path, 'r') as ds:
            bb_poly = geopandas.GeoSeries([Polygon(BBOX_POLYGON)])
            img_out, meta_out = eps.crop_image(ds, bb_poly)

        with rio.open(self.output().path, 'w', **meta_out) as c_ds:
            c_ds.write(img_out)