#!/usr/bin/env python
import sys
import matplotlib
import math
import pyproj
from descartes import PolygonPatch
matplotlib.use('agg', warn=False)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.colorbar import ColorbarBase
from mpl_toolkits.axes_grid.inset_locator import inset_axes
import sys
import os
import zipfile
import ogr2ogr
import json
import shelve
import pyproj


class GeoToronto(object):
    def __init__(self):
        self._data_path = "./geo_toronto"
        self.json_file = self._get_data_files()

    def _get_data_files(self):
        # convert shp file to json file
        try:
            os.makedirs(self._data_path)
        except IOError:
            # already exists
            pass
        base = "ZONING_ZONE_CATAGORIES_WGS84"
        zip_file = os.path.join(self._data_path, "zoning_wgs84.zip")
        shp_file = os.path.join(self._data_path, base + ".shp")
        json_file = os.path.join(self._data_path, base + ".json")
        url = "http://opendata.toronto.ca/gcc/zoning_wgs84.zip"

        if not os.path.exists(zip_file):
            get_file(url, zip_file)
        if not os.path.exists(shp_file):
            print("  - Converting", base)
            with zipfile.ZipFile(zip_file) as zf:
                zf.extractall(self._data_path)
                args = ["", "-f", "GeoJSON", "-t_srs", "crs:84", json_file, shp_file]
                ogr2ogr.main(args)
                os.unlink(shp_file)
        return json_file

    def get_plot(self, transform=lambda x: x):
        with open(self.json_file) as json_file:
            json_data = json.load(json_file)
        fig = plt.figure(figsize=(15,15))
        ax = fig.add_subplot(1, 1, 1)
        for i in json_data['features']:
            poly = i['geometry']
            poly = transform(poly)
            fc = "#ffffff"
            ec = "#ff0000"
            z = 100
            ax.add_patch(PolygonPatch(poly,
                                      fc=fc,
                                      ec=ec,
                                      zorder=z))
            ax.set_xlim([-79.63, -79.11])
            ax.set_ylim([43.58, 43.85])
        return fig

def transform(source):
    outProj = pyproj.Proj(init="epsg:4326")
    inProj = pyproj.Proj(init="epsg:3857")
    if isinstance(source, dict):
        return {'type': source['type'],
                'coordinates': transform(source['coordinates'])}
    ans = []
    if any(isinstance(el, list) for el in source):
        for el in source:
            ans.append(transform(el))
    else:
        ans = pyproj.transform(inProj, outProj,
                               source[0], source[1])
        ans = list(ans)
    return ans

geo_toronto = GeoToronto()
fig = geo_toronto.get_plot()
fig.savefig("zoning_toront.png")
