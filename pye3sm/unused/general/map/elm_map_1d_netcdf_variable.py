from __future__ import division
import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib as mpl
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
mms2mmd = 24 * 3600.0
sExtension_nc = '.nc'
sExtension_envi = '.dat'
sExtension_png = '.png'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = '/Volumes/mac/01data/'
sWorkspace_simulation = '/Volumes/mac/csmruns/'
sWorkspace_analysis = '/Volumes/mac/03model/vsfm/analysis/'

#we only need to change the case number, all variables will be processed one by one
iCase = 11
iYear_start = 1948
iYear_end = 2013

aVariable = ['ZWT']
aDimension = [1]
#aConversion = [ 1]
aUnit =[ r'unit: m']


#aVariable = ['hk_sat']
aVariable = ['QDRAI']
#aDimension = [1]
#aConversion = [mms2mmd]
#aUnit =[r'units: mm/s']

nVariable = len(aVariable)
#be careful with the name


def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)

    return r'${} \times 10^{{{}}}$'.format(a, b)


#a = '{:.4f}'.format(x)
#return a



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
            sFilename = sWorkspace_variable_dat + slash + sVariable.lower(
            ) + sYear + sMonth + sExtension_envi

            aData = ENVI_raster_binary_to_2d_array(sFilename)
            img = aData[0]
            aMask = np.where(img == missing_value )
            aMask2 = np.where( (img != missing_value)  & (img >0.0))
              
            good_value = img[aMask2]

            max_value = np.ceil(max(np.log10(good_value)  )  )
            min_value = np.floor( min(np.log10(good_value)   )  )
            min_value = -8 
            img = np.log10(img)  
            img[img< min_value] = min_value
            img[img > max_value] =  max_value      
        
            img[aMask] = np.nan
            levelsCIN = 1 * np.arange( (max_value - min_value+1) , dtype= float) + min_value
            levelsCIN2 = np.power(10.0, levelsCIN)            
            cmap = plt.get_cmap('rainbow')  
            fig, ax = plt.subplots(1, 1, figsize=(12, 9))
            l, b, w, h = ax.get_position().bounds
            ax.set_position([0.75 * l, b, w - l * 0.25, h])            
            img[aMask] = np.nan            
            im = ax.imshow(img, extent=(-180, 180, -90, 90), origin='upper',cmap=cmap , vmax = max_value, vmin=min_value )            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="1.5%", pad=0.2)
            cb = plt.colorbar(
                im,                
                cax = cax,
                #format=ticker.FuncFormatter(fmt),                              
                extend = 'both')

            tick_locator = ticker.MaxNLocator(nbins=5)
            cb.locator = tick_locator
            
            cb.ax.set_yticklabels(['{:.0e}'.format(x) for x in levelsCIN2], fontsize=12)
            
            
            ax.set_title(sVariable.capitalize())
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.text(100, -75, aUnit[iIndex], color="black")
          
            sWorkspace_variable_png = sWorkspace_variable + slash + 'png'
            if not os.path.exists(sWorkspace_variable_png):
                os.makedirs(sWorkspace_variable_png)
            sFilename_fig = sWorkspace_variable_png + slash + sVariable.lower(
            ) + sYear + sMonth + sExtension_png
            fig.savefig(sFilename_fig, dpi=300)
            #plt.show()

print('finished')
