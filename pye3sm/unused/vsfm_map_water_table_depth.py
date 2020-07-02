

import os
import sys
import platform
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path #get the home directory
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import AxesGrid


sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'eslib_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_raster_binary_to_2d_array import envi_raster_binary_to_2d_array

def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

#global
missing_value = -9999.0
sExtension_nc = '.nc'
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tif = '.tif'
sExtension_png = '.png'
#local
sModel = 'vsfm'
sVariable ='zwt'
mms2mmd = 24 * 3600.0
dConversion = 1.0
iCase = 11
sCase = sModel + "{:02d}".format(iCase)
iYear_start = 1948
iYear_end = 2013
iMonth_start = 1
iMonth_end = 12

            
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
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

sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'dat'

sWorkspace_variable_png = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'png'
if not os.path.exists(sWorkspace_variable_png):
                    os.makedirs(sWorkspace_variable_png)

for iYear in range(iYear_start, iYear_end + 1):
    sYear = str(iYear).zfill(4)
    for iMonth in range(iMonth_start, iMonth_end + 1):
        sMonth = str(iMonth).zfill(2)
        #read raster data
        sFilename_envi = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sExtension_envi

        dummy = envi_raster_binary_to_2d_array(sFilename_envi)
        img = dummy[0] 
    
        
        aMask1 = np.where(  img != missing_value )  
        aMask2 = np.where(  img == missing_value )
        aMask3 = np.where(  img == 0.0 )
        
        img = img * dConversion
        
        min_value = 0
        max_value = 50
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
            ax.set_title('Water table depth (m)', loc='center')
            implot = ax.imshow(img, extent = img_extent, origin='upper',cmap=cmap , \
             vmax = max_value, vmin = min_value , transform = projection ) 

        #axgr.cbar_axes[0].colorbar(p)
        cb_label_log =  np.arange( min_value , (max_value+1) , 5.0 , dtype= float)
        cb_label = cb_label_log
        cb = plt.colorbar(implot, cax = axgr.cbar_axes[0], extend = 'both')
        tick_locs   = cb_label_log
        tick_labels = ['{:.0f}'.format(x) for x in cb_label]
        cb.locator     = ticker.FixedLocator(tick_locs)
        cb.formatter   = ticker.FixedFormatter(tick_labels)       
        cb.update_ticks()
        #plt.show()
        sFilename_png= sWorkspace_variable_png + slash + sVariable.lower() + sYear + sMonth + sExtension_png
        plt.savefig(sFilename_png, bbox_inches = 'tight')
        print(sFilename_png)
        plt.close('all')
