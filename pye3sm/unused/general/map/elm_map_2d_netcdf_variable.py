
from __future__ import division
import os
import numpy as np
import matplotlib.pyplot as plt
import platform
import statistics

import os
import sys
import numpy as np
import glob
import platform
import statistics
import xarray as xr
import pandas as pd

import time, datetime, calendar, pytz
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.util import add_cyclic_point

from skimage import exposure

from mpl_toolkits.axes_grid1 import make_axes_locatable
from osgeo import gdal, gdalconst
from osgeo.gdalconst import *
from netCDF4 import Dataset

from scipy.interpolate import griddata

platform_os = platform.system()
if platform_os == 'Windows':
    slash = '\\'
else:
    slash = '/'

missing_value = -9999.0
nlayer =15
sExtension_nc = '.nc'
sExtension_envi = '.dat'
sExtension_png = '.png'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = '/Volumes/mac/01data/'
sWorkspace_simulation = '/Volumes/mac/csmruns/'
sWorkspace_analysis = '/Volumes/mac/03model/h2sc/analysis/'

#we only need to change the case number, all variables will be processed one by one
iCase = 142
iYear_start = 1960
iYear_end = 1960
aVariable = ['H2OSOI']
aDimension = [1]
nVariable = len(aVariable)

mms2mmd = 24 * 3600.0
aConversion = [1.0]
aUnit =[r'units: fraction']
#be careful with the name


def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)

    return r'${} \times 10^{{{}}}$'.format(a, b)


#a = '{:.4f}'.format(x)
#return a


def ENVI_raster_binary_to_2d_array(file_name):
    '''
	Converts a binary file of ENVI type to a numpy array.
	Lack of an ENVI .hdr file will cause this to crash.
	'''
    driver = gdal.GetDriverByName('ENVI')
    driver.Register()

    inDs = gdal.Open(file_name, GA_ReadOnly)

    if inDs is None:
        print("Couldn't open this file: " + file_name)
        print('Perhaps you need an ENVI .hdr file?')
        sys.exit("Try again!")
    else:
        print("%s opened successfully" % file_name)

        print('~~~~~~~~~~~~~~')
        print('Get image size')
        print('~~~~~~~~~~~~~~')
        cols = inDs.RasterXSize
        rows = inDs.RasterYSize
        bands = inDs.RasterCount

        print("columns: %i" % cols)
        print("rows: %i" % rows)
        print("bands: %i" % bands)

        print('~~~~~~~~~~~~~~')
        print('Get georeference information')
        print('~~~~~~~~~~~~~~')
        geotransform = inDs.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]

        print("origin x: %i" % originX)
        print("origin y: %i" % originY)
        print("width: %2.2f" % pixelWidth)
        print("height: %2.2f" % pixelHeight)

        # Set pixel offset.....
        print('~~~~~~~~~~~~~~')
        print('Convert image to 2D array')
        print('~~~~~~~~~~~~~~')
        band = inDs.GetRasterBand(1)
        image_array = band.ReadAsArray(0, 0, cols, rows)
        image_array_name = file_name
        print(type(image_array))
        print(image_array.shape)

        return image_array, pixelWidth, (geotransform, inDs)




sCase = 'h2sc' + "{:02d}".format(iCase)

sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'

sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)



iMonth_start = 1
iMonth_end = 12

for iIndex in range(0, nVariable):
    sVariable = aVariable[iIndex]

    for iYear in range(iYear_start, iYear_end + 1):
        sYear = str(iYear).zfill(4)

        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
            sWorkspace_variable = sWorkspace_analysis_case + slash + sVariable.lower(
            )
            sWorkspace_variable_dat = sWorkspace_variable + slash + 'dat'

            for iLayer in range (1, nlayer+1):
                sLayer = str(iLayer).zfill(2)

                sFilename = sWorkspace_variable_dat + slash + sVariable.lower(
                ) + sYear + sMonth + sLayer +  sExtension_envi

                aData = ENVI_raster_binary_to_2d_array(sFilename)
                img = aData[0]
                aMask = np.where(img == missing_value)
                aMask2 = (img != missing_value)
                #img[aMask] = np.nan
                #f = plt.figure(figsize=(10,3))
                fig, ax = plt.subplots(1, 1, figsize=(12, 9))

                l, b, w, h = ax.get_position().bounds
                ax.set_position([0.75 * l, b, w - l * 0.25, h])

                img_eq = exposure.equalize_hist(img, mask=aMask2)
                img_eq[aMask] = np.nan
                im = ax.imshow(img_eq, extent=(-180, 180, -90, 90), origin='upper',cmap='Spectral', vmax =1.0, vmin=0.0)
                #plt.axis('off')
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="1.5%", pad=0.2)
                cb = plt.colorbar(
                    im,
                    cax=cax,
                    #format=ticker.FuncFormatter(fmt),                
                    extend='both')

                tick_locator = ticker.MaxNLocator(nbins=5)
                cb.locator = tick_locator
                cb.update_ticks()
                ax.set_title(sVariable.capitalize())
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')
                ax.text(100, -75, aUnit[iIndex], color="black")
                #plt.tight_layout()
                sWorkspace_variable_png = sWorkspace_variable + slash + 'png'
                if not os.path.exists(sWorkspace_variable_png):
                    os.makedirs(sWorkspace_variable_png)
                sFilename_fig = sWorkspace_variable_png + slash + sVariable.lower(
                ) + sYear + sMonth  + sLayer + sExtension_png
                fig.savefig(sFilename_fig, dpi=300)
                #plt.show()

print('finished')
