
import os
import sys
import numpy as np
import platform
from pathlib import Path #get the home directory
import matplotlib as mpl

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import AxesGrid

from netCDF4 import Dataset #it maybe be replaced by gdal 




sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'pyes_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_write_header import envi_write_header

sModel = 'h2sc'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster

sWorkspace_simulation = sWorkspace_scratch + slash + 'csmruns'
sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
    + sModel + slash + 'analysis'
if not os.path.isdir(sWorkspace_analysis):
    os.makedirs(sWorkspace_analysis)

sFilename_mask = sWorkspace_data + slash \
    + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
    + 'MOSART_Global_half_20180606c.chang_9999.nc'
#we only need to change the case number, all variables will be processed one by one
iCase = 169
#be careful with the name
aVariable = ['QDRAI']
aDimension = [1]

#we do not change unit here
mms2mmd = 24 * 3600.0
dConversion = mms2mmd

sCase = sModel + "{:02d}".format(iCase)

sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'

sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)

iYear_start = 1948
iYear_end = 2013

iMonth_start = 1
iMonth_end = 12

#read in mask
print(sFilename_mask)
aDatasets = Dataset(sFilename_mask)

netcdf_format = aDatasets.file_format
print(netcdf_format)
print("Print dimensions:")
print(aDatasets.dimensions.keys())
print("Print variables:")
print(aDatasets.variables.keys())
for sKey, aValue in aDatasets.variables.items():
    if "ele0" == sKey:
        aEle0 = (aValue[:]).data
        break
aMask = np.where(aEle0 == missing_value)

print('prepare grid')


for iYear in range(iYear_start, iYear_end + 1):
    sYear = str(iYear).zfill(4)

    for iMonth in range(iMonth_start, iMonth_end + 1):
        sMonth = str(iMonth).zfill(2)

        sDummy = '.clm2.h0.' + sYear + '-' + sMonth + sExtension_nc
        sFilename = sWorkspace_simulation_case + slash + sCase + sDummy

        #read before modification

        if os.path.exists(sFilename):
            print('Yep, I can read ' + sFilename)
        else:
            print(  "Nope, the path doesn't reach your file " + sFilename
            )

        aDatasets = Dataset(sFilename)
        netcdf_format = aDatasets.file_format
        
        for sKey, aValue in aDatasets.variables.items():

            if (sKey == 'lon'):
                #print(aValue.datatype)
                #print(aValue.dimensions)
                aLongitude = (aValue[:]).data
                continue
            if (sKey == 'lat'):
                #print(aValue.datatype)
                #print(aValue.dimensions)
                aLatitude = (aValue[:]).data
                continue
        dummy_index = np.where(aLongitude > 180)
        aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0

        for sKey, aValue in aDatasets.variables.items():
            for iIndex, sVariable in enumerate(aVariable):
                if sVariable == sKey:
                    aData = (aValue[:]).data
                    #get dimension
                    iDimension = aDimension[iIndex]
                    if (iDimension == 1):
                        #normal
                        aData = aData.reshape(len(aData[0]))
                        missing_value1 = max(aData)
                        dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 ) \
                          &(aData != missing_value1 ) )

                        aLongitude_subset = aLongitude[dummy_index]
                        aLatitude_subset = aLatitude[dummy_index]
                        aData_subset = aData[dummy_index] 

                        points = np.vstack((aLongitude_subset, aLatitude_subset))
                        points = np.transpose(points)
                        values = aData_subset * dConversion
                        
                    

                        sWorkspace_variable_jpg  = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'jpg'
                        if not os.path.exists(sWorkspace_variable_jpg):
                            os.makedirs(sWorkspace_variable_jpg)

                        #plot
                        fig = plt.figure(figsize=(12,9),  dpi=600 )
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
                            scatterplot = ax.scatter(aLongitude_subset, aLatitude_subset, s = values, c  = values)

                        

                        max_value=-1
                        min_value = -5
                        cb_label_log = 1 * np.arange( (max_value - min_value + 1) , dtype= float) + min_value
                        cb_label = np.power(10.0, cb_label_log)
                        cb = plt.colorbar(scatterplot, cax = axgr.cbar_axes[0], extend = 'both')        
                        tick_locs   = cb_label_log
                        tick_labels = ['{:.0e}'.format(x) for x in cb_label]
                        cb.locator     = ticker.FixedLocator(tick_locs)
                        cb.formatter   = ticker.FixedFormatter(tick_labels)       
                        cb.update_ticks()
                        #plt.show()        

                        sFilename_jpg= sWorkspace_variable_jpg + slash + sVariable.lower() + sYear + sMonth + sExtension_jpg
                        plt.savefig(sFilename_jpg)
                        print(sFilename_jpg)
                        plt.close('all')

                        

                    else:                        
                        pass
                else:
                    continue
        #produce grid

    print("finished")
