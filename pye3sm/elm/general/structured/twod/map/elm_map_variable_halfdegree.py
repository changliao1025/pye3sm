
#no longer used because we will use IDL for this step
import os
import sys

import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import AxesGrid

from pyearth.system.define_global_variables import *
from pyearth.gis.gdal.gdal_read_envi_file import gdal_read_envi_file_multiple

def fomatter(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def elm_map_variable_halfdegree(sFilename_configuration_in, \
    iCase_index, \
    iFlag_same_grid_in = None, \
    iYear_start_in = None, \
    iYear_end_in = None, \
    sDate_in = None):
    #local
    e3sm_read_configuration_file(sFilename_configuration_in, iCase_index_in = iCase_index,\
         iYear_start_in = iYear_start_in, \
    iYear_end_in = iYear_end_in, \
         sDate_in= sDate_in)      
    sModel = 'vsfm'
    sVariable ='qdrai'
    mms2mmd = 24 * 3600.0
    dConversion = mms2mmd
    iCase = 11
    sCase = sModel + "{:02d}".format(iCase)
    iYear_start = 1948
    iYear_end = 2013
    iMonth_start = 1
    iMonth_end = 12


    #for the sake of simplicity, all directory will be the same, no matter on mac or    cluster
    sWorkspace_data = home + slash + 'data'
    sWorkspace_simulation = sWorkspace_scratch + slash + 'csmruns'
    sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
        + sModel + slash + 'analysis'
        
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)


    sWorkspace_simulation_case = sWorkspace_simulation + slash  + sCase + slash + 'run'

    sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase 

    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)

    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'dat'

    sWorkspace_variable_png = sWorkspace_analysis_case + slash + sVariable.lower() +    slash + 'png'
    if not os.path.exists(sWorkspace_variable_png):
                        os.makedirs(sWorkspace_variable_png)


    #read the stack data

    sFilename = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    aData_all = gdal_read_envi_file_multiple(sFilename)

    for iYear in range(iYear_start, iYear_end + 1):
        sYear = str(iYear).zfill(4)
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
            i = (iYear-iYear_start) * 12 + iMonth-iMonth_start
            img=(aData_all[0])[i]
            min_value = -4
            max_value = 1.5
            aMask1 = np.where(  img != missing_value )  
            aMask2 = np.where(  img == missing_value )
            aMask3 = np.where(  img == 0.0 )

            img = img * dConversion
            img[aMask2] = 10**(min_value )
            img[aMask3] = 10**(min_value )
            img = np.log10(img) 
            print(np.max(img))
            print(np.min(img))
            img[ np.where(  img < min_value )  ] = min_value
            img[ np.where(  img > max_value )  ] = max_value
            img[aMask2] = np.nan               
            img_extent=(-180,180,-90,90)
            #plot
            fig = plt.figure(figsize=(12,9),  dpi=100 )
            cmap = plt.get_cmap('rainbow') 
            projection = ccrs.PlateCarree()
            axes_class = (GeoAxes,
                      dict(map_projection=projection))
            axgr = AxesGrid(fig, 111, axes_class=axes_class,
                        nrows_ncols=(1,1),
                        axes_pad=0.6,
                        cbar_location='right',
                        cbar_mode='single',
                        cbar_pad=0.2,
                        cbar_size='1.5%',
                        label_mode='')  # note the empty label_mode

            for i, ax in enumerate(axgr):
                #ax.coastlines()
                ax.axis('off')
                #ax.gridlines() 
                #ax.add_feature(cfeature.OCEAN, zorder=0)
                #ax.add_feature(cfeature.LAND, zorder=0, edgecolor='black')
                #ax.add_feature(cfeature.COASTLINE)
                ax.set_global()
                ax.set_xmargin(0.05)
                ax.set_ymargin(0.10)
                ax.set_xticks(np.linspace(-180, 180, 5), crs=projection)
                ax.set_yticks(np.linspace(-90, 90, 5), crs=projection)
                lon_formatter = LongitudeFormatter(zero_direction_label=True)
                lat_formatter = LatitudeFormatter()
                ax.xaxis.set_major_formatter(lon_formatter)
                ax.yaxis.set_major_formatter(lat_formatter)
                ax.set_title('Total Drainage (mm/day)', loc='center')
                implot = ax.imshow(img, extent = img_extent, origin='upper',cmap=cmap , \
                 vmax = max_value, vmin = min_value , transform = projection ) 

            #axgr.cbar_axes[0].colorbar(p)
            cb_label_log = 1 * np.arange( (max_value - min_value + 1) , dtype= float) +     min_value
            cb_label = np.power(10.0, cb_label_log)
            cb = plt.colorbar(implot, cax = axgr.cbar_axes[0], extend = 'both')
            tick_locs   = cb_label_log
            tick_labels = ['{:.0e}'.format(x) for x in cb_label]
            cb.locator     = ticker.FixedLocator(tick_locs)
            cb.formatter   = ticker.FixedFormatter(tick_labels)       
            cb.update_ticks()
            #plt.show()
            sFilename_png= sWorkspace_variable_png + slash + sVariable.lower() + sYear +    sMonth + sExtension_png
            plt.savefig(sFilename_png, bbox_inches = 'tight')
            print(sFilename_png)
            plt.close('all')
