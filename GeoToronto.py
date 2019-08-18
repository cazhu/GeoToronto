#!/usr/bin/env python
import sys
import matplotlib
import math
import pyproj
from descartes import PolygonPatch
import matplotlib.pyplot as plt
matplotlib.use('ps')
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
import urllib.request
import shutil


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


class GeoToronto(object):
    def __init__(self, cache=True):
        self.geo_proj = GeoProj()
        self._get_data_files(cache=cache)

    def _get_data_files(self, cache):
        if not cache:
            try:
                shutil.rmtree('./data/') 
                
            except FileNotFoundError:
                print('No such file or directory.')
        
        try:
            print('Creating data folder')
            os.makedirs('./data/')
        except IOError:
            print('Folder already exists')
            pass

        zip_file = "./data/zoning_wgs84.zip"
        if not os.path.exists(zip_file):
            url = "http://opendata.toronto.ca/gcc/zoning_wgs84.zip"
            print('Downloading compressed shp file from data soure: \n', url)
            urllib.request.urlretrieve(url, './data/zoning_wgs84.zip')
        shp_file = "./data/ZONING_ZONE_CATAGORIES_WGS84.shp"
        if not os.path.exists(shp_file):
            print('Extracting shp file')
            with zipfile.ZipFile(zip_file) as zf:
                zf.extractall('./data')

    def get_plot(self):
        shape = fiona.open("./data/ZONING_ZONE_CATAGORIES_WGS84.shp")
        fig = plt.figure(figsize=(15,15))
        x1, y1 = self.geo_proj.transform([-79.63, 43.58])
        x2, y2 = self.geo_proj.transform([-79.11, 43.85])

        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(x1, x2)
        ax.set_ylim(y1, y2)


        fc = "#ffffff"
        ec = "#ff0000"
        z = 100

        while True:
            try:
                i = next(shape)
                poly = i['geometry']
                poly = self.geo_proj.transform(poly)     
                ax.add_patch(PolygonPatch(poly, fc=fc, ec=ec, zorder=z))
            except StopIteration: 
                print('Finish')
                break
        return fig


if __name__ == '__main__':
    geo_toronto = GeoToronto()
    fig = geo_toronto.get_plot()
    fig.savefig('output.png')
