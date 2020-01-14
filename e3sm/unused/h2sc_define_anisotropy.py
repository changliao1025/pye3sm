import os
import sys
import numpy as np
import platform
from pathlib import Path #get the home directory

from osgeo import ogr, osr
from netCDF4 import Dataset #it maybe be replaced by gdal 
from osgeo import gdal #the default operator
from scipy.interpolate import griddata #generate grid



sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'eslib_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_write_header import envi_write_header
from toolbox.reader.gdal_read_tiff import gdal_read_tiff



missing_value = -9999.0
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tif = '.tif'
sExtension_jpg ='.jpg'
dConversion =1.0
sVariable = 'zwt'
sModel = 'h2sc'
#prepare the header in
headerParameters = {}    
headerParameters['ncolumn'] = '720'
headerParameters['nrow'] = '360'
headerParameters['ULlon'] = '-180'
headerParameters['ULlat'] = '90'
headerParameters['pixelSize'] = '0.5'
headerParameters['nband'] = '1'
headerParameters['offset'] = '0'
headerParameters['data_type'] = '4'
headerParameters['bsq'] = 'bsq'
headerParameters['byte_order'] = '0'
headerParameters['missing_value'] = '-9999'

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
    + 'wtd' + slash  + 'wtd'  + sExtension_tif

pWTD = gdal_read_tiff(sFilename_tiff)
aWTD = pWTD[0]

longitude = np.arange(-180, 180, 0.5)
latitude = np.arange(-90, 90, 0.5)

nrow = len(latitude)
ncol = len(longitude)

grid_x, grid_y = np.meshgrid(longitude, latitude)

aAnisotropy = np.full( (nrow, ncol), 10.0 , dtype=float )  
aResidual = np.full( (nrow, ncol), missing_value , dtype=float )  
iCase_start= 180
iCase_end = 189
sYear = '2012'
sMonth ='08'
for i in range( nrow ):
    for j in range(ncol):

        iMask = aEle0[i,j]
        dWtd = aWTD[i,j]
        if(iMask != missing_value and dWtd!=missing_value):            
            #get the wtd 
            print('ok')
            #extract
            aWTD_sim = np.full( (iCase_end-iCase_start+1), missing_value , dtype=float )  
            for iCase in range(iCase_start, iCase_end+1):
                sCase = "{:0d}".format(iCase)
                sWorkspace_analysis_case = sWorkspace_analysis + slash + sModel + sCase
                sWorkspace_variable_tif = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'tiff'
                sFilename_wtd_sim = sWorkspace_variable_tif + slash + sVariable.lower() + sYear + sMonth + sExtension_tif
                pWTD = gdal_read_tiff(sFilename_wtd_sim)
                dummy = pWTD[0]
                #display image to check
                
                aWTD_sim[iCase - iCase_start] = dummy[i,j]
                print(dummy[i,j])
            #choose the closest
            dDistance = np.power( (aWTD_sim - dWtd ), 2  )
            dMin = np.min(dDistance)
            iIndex = np.where( dDistance == dMin )
            dummy_index = iIndex[0] 
            if(len(dummy_index) == 1):            
                aAnisotropy[i,j] = (dummy_index + 1) * 10
                aResidual[i,j] = aWTD_sim[dummy_index] - dWtd
            else:
                print('index is: ', dummy_index)
                dummy = dummy_index[0]
                aAnisotropy[i,j] = (dummy+ 1) * 10
                aResidual[i,j] = aWTD_sim[dummy] - dWtd

            #now search for the close match
        else:
            pass

aAnisotropy[aMask] = missing_value
aAnisotropy = np.flip(aAnisotropy, 0)
#save it out
sFilename_envi = sWorkspace_analysis + slash + 'anisotropy' + sExtension_envi
aAnisotropy.astype('float32').tofile(sFilename_envi)
#write header
sFilename_header = sWorkspace_analysis + slash + 'anisotropy' + sMonsExtension_header
headerParameters['sFilename'] = sFilename_header
envi_write_header(sFilename_header, headerParameters)

aResidual[aMask] = missing_value
aResidual = np.flip(aResidual, 0)
#save it out
sFilename_envi = sWorkspace_analysis + slash + 'aResidual' + sExtension_envi
aResidual.astype('float32').tofile(sFilename_envi)
#write header
sFilename_header = sWorkspace_analysis + slash + 'aResidual' + sMonsExtension_header
headerParameters['sFilename'] = sFilename_header
envi_write_header(sFilename_header, headerParameters)