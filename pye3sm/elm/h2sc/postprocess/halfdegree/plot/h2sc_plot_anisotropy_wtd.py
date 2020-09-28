import os
import sys
import numpy as np
import platform
from pathlib import Path #get the home directory
import matplotlib.pyplot as plt
from osgeo import ogr, osr
from netCDF4 import Dataset #it maybe be replaced by gdal 
from osgeo import gdal #the default operator
from scipy.interpolate import griddata #generate grid



sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'pyes_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)

from gis.gdal.reader.gdal_read_tiff import gdal_read_tiff


missing_value = -9999.0
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tiff = '.tif'
sExtension_jpg ='.jpg'
dConversion = 1.0
sVariable = 'zwt'
sModel = 'h2sc'

#sWorkspace_data = '/Users/liao313/data'
sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash + sModel + slash \
        + 'cases' + slash + 'h2sc_configuration_wtd.txt'
ifs = open(sFilename_configuration, 'r')
config = {}
for sLine in ifs:
    sDummy = sLine.split(',')
    if (len(sDummy) == 2):
        print(sDummy)
        sKey = (sDummy[0]).strip()
        sValue = (sDummy[1]).strip()
        config[sKey] = sValue
    else:
        pass
ifs.close()
sWorkspace_home = config['sWorkspace_home']
sWorkspace_scratch = config['sWorkspace_scratch']
sWorkspace_data = config['sWorkspace_data']
sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
        + sModel + slash + 'analysis'


sFilename_mask = sWorkspace_data + slash \
        + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
        + 'MOSART_Global_half_20180606c.chang_9999.nc'
sFilename_wtd = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
    + 'wtd' + slash + 'wtd.tif'
if os.path.isfile(sFilename_mask):
    pass
else:
    error_code = 0
    exit()
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

#read wtd 
sFilename_tiff = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
    + 'wtd' + slash  + 'wtd'  + sExtension_tiff

pWTD = gdal_read_tiff(sFilename_tiff)
aWTD = pWTD[0]


#we must align the case with the parameter space


aHydraulic_anisotropy = [0.5, 1, 5, 150, 200, 250, 300, 400, 500, 1000]  
aAnisotropy = [ 0.5, 1, 5, 10, 20, 30 ,40, 50, 60, 70, 80, 90 , 100, 150, 200, 250, 300, 400, 500, 1000]

aCase = [ 190, 191, 192, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 193, 194, 195, 196, 197, 198, 199 ]

print(len(aAnisotropy))
print( len(aCase) )

nCase = len(aCase)

for i in range( nrow ):
    for j in range(ncol):

        iMask = aEle0[i,j]
        dWtd = aWTD[i,j]

        if iMask == 1:

            aWtd1 = np.full(  nCase, missing_value, dtype = float)
            for iCase in aCase:

                sCase  = "{:0d}".format(iCase)

                #read geotiff
                dummy = gdal_read_tiff()

                dummy_wtd = (dummy[1])[i, j]
                aWtd1[iCase-1] = dummy_wtd
            #plot 
            fig, ax = plt.subplots(1, 1, figsize=(12, 9),  dpi=100 )            
            cmap = plt.get_cmap('rainbow')    
            ax.set_xmargin(0.05)
            ax.set_ymargin(0.10)
            x= aCase
            y= aWtd1
            ax.plot(x, y)
            #plot observation wtd
            x = [0, np.max(aCase)]
            y = [dWtd, dWtd]
            ax.plot(x, y)
                
            ax.set_title('Water table depth (m)', loc='center')

            #
                


        else:
            pass

