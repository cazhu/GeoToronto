#!/usr/bin/env python
import sys
import matplotlib
import math
import pyproj
from descartes import PolygonPatch
# matplotlib.use('agg', warn=False)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.colorbar import ColorbarBase
from mpl_toolkits.axes_grid.inset_locator import inset_axes
import sys
import os
import zipfile
import subprocess
import json
import shelve
import fiona


class GeoToronto(object):
    def __init__(self):
        self._data_path = './data'
        self._zip_file = 'zoning_wgs84.zip'
        self._download_link = 'http://opendata.toronto.ca/gcc/'
        self._shp_file = 'ZONING_ZONE_CATAGORIES_WGS84.shp'
        self._get_data_files()
        self._geo_proj = GeoProj()

    def _get_data_files(self):
        try:
            os.makedirs(self._data_path)
        except IOError:
            pass
        zip_file = os.path.join(self._data_path, self._zip_file)
        shp_file = os.path.join(self._data_path, self._shp_file)

        if not os.path.exists(zip_file):
            sys.exit(f"Data source not found. Please download the .shp file from: {self._download_link}")
        if not os.path.exists(shp_file):
            print("  - extracting shp files")
            with zipfile.ZipFile(zip_file) as zf:
                zf.extractall(self._data_path)
        self._shape = fiona.open(shp_file)
        return

    def get_plot(self):
        fig = plt.figure(figsize=(15,15))
        x1, y1 = self._geo_proj.transform([-79.63, 43.58])
        x2, y2 = self._geo_proj.transform([-79.11, 43.85])

        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(x1, x2)
        ax.set_ylim(y1, y2)

        fc = "#ffffff"
        ec = "#ff0000"
        z = 100

        while True:
            try:
                i = next(self._shape)
                poly = i['geometry']
                poly = self._geo_proj.transform(poly)
                ax.add_patch(PolygonPatch(poly, fc=fc, ec=ec, zorder=z))
            except:
                print('Finish')
                break
        return fig


class GeoProj(object):
    def __init__(self, input="epsg:4326", output="epsg:3857"):
        self._outProj = pyproj.Proj(init=output)
        self._inProj = pyproj.Proj(init=input)

    def transform(self, source):
        if isinstance(source, dict):
            return {'type': source['type'],
                    'coordinates': self.transform(source['coordinates'])}
        ans = []
        if any(isinstance(el, list) for el in source) or any(isinstance(el, tuple) for el in source):
            for el in source:
                ans.append(self.transform(el))
        else:
            ans = pyproj.transform(self._inProj, self._outProj, source[0], source[1])
        return ans


if __name__ == '__main__':
    geo_toronto = GeoToronto()
    fig = geo_toronto.get_plot()
    fig.savefig("zoning_trt.png")
