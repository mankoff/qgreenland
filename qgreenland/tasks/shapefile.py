import os
import zipfile

import luigi

from qgreenland.constants import TaskType
from qgreenland.tasks.common import FetchData
from qgreenland.util import (LayerConfigMixin,
                             find_shapefile_in_dir,
                             reproject_shapefile,
                             subset_shapefile,
                             tempdir_renamed_to)


# TODO: Is there any task history? e.g. can we look at the final output target
# and generate a list of tasks that were performed to generate it?

class UnzipShapefile(LayerConfigMixin, luigi.Task):
    task_type = TaskType.WIP

    def requires(self):
        return FetchData(self.layer_cfg)

    def output(self):
        return luigi.LocalTarget(f'{self.outdir}/unzip/')

    def run(self):
        with tempdir_renamed_to(self.output().path) as tmpdir:
            zf = zipfile.ZipFile(self.input().path)

            for fn in zf.namelist():
                zf.extract(fn, tmpdir)
            zf.close()


class ReprojectShapefile(LayerConfigMixin, luigi.Task):
    task_type = TaskType.WIP

    def requires(self):
        return UnzipShapefile(self.layer_cfg)

    def output(self):
        return luigi.LocalTarget(f'{self.outdir}/reproject/')

    def run(self):
        shapefile = find_shapefile_in_dir(self.input().path)

        gdf = reproject_shapefile(shapefile)
        with tempdir_renamed_to(self.output().path) as tmpdir:
            fn = os.path.join(tmpdir, 'shapefile.shp')
            gdf.to_file(fn, driver='ESRI Shapefile')


class SubsetShapefile(LayerConfigMixin, luigi.Task):
    task_type = TaskType.WIP

    def requires(self):
        return ReprojectShapefile(self.layer_cfg)

    def output(self):
        return luigi.LocalTarget(f'{self.outdir}/subset/')

    def run(self):
        shapefile = find_shapefile_in_dir(self.input().path)

        gdf = subset_shapefile(shapefile)
        with tempdir_renamed_to(self.output().path) as tmpdir:
            fn = os.path.join(tmpdir, 'shapefile.shp')
            gdf.to_file(fn, driver='ESRI Shapefile')