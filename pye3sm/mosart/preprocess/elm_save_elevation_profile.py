
import os
import sys
import numpy as np
import platform
from scipy.interpolate import griddata
from pathlib import Path #get the home directory
from netCDF4 import Dataset #read netcdf
from osgeo import gdal #the default operator



sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'pyes_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_write_header import envi_write_header

missing_value = -9999.0 #used to save binary
sExtension_nc = '.nc'
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tiff = '.tif'

sModel = 'h2sc'
#vsdm dimension
aDimension = [ 96, 144]
mms2mmd = 24 * 3600.0
dConversion = mms2mmd

#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = home + slash + 'data'
sWorkspace_simulation = sWorkspace_scratch + slash + 'csmruns'
sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
    + sModel + slash + 'analysis'
if not os.path.isdir(sWorkspace_analysis):
    os.makedirs(sWorkspace_analysis)

#we only need to change the case number, all variables will be processed one by one
iCase = 173
iYear_start = 1948
iYear_end = 2013

iMonth_start = 1
iMonth_end = 12
aVariable = ['ele0', 'ele1','ele2', 'ele3','ele4','ele5','ele6','ele7','ele8','ele9','ele10']
sCase = sModel + "{:0d}".format(iCase)
sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'
sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)




#read in global 0.5 * 0.5 mask
sFilename_mask = sWorkspace_data + slash \
    + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
    + 'MOSART_Global_half_20180606c.chang_9999.nc'
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
        aMask = np.where(aEle0 == missing_value)
        break
    
print('Prepare the map grid')
longitude = np.arange(-180, 180, 0.5)
latitude = np.arange(-90, 90, 0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)
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




sCase = 'h2sc' + "{:02d}".format(iCase)

sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'

sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)

iYear_start = 1948
iYear_end = 1972

iMonth_start = 2
iMonth_end = 12

#read in mask
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



print('Prepare the map grid')
longitude = np.arange(-179.75, 180., 0.5)
latitude = np.arange(-89.75, 90., 0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)
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

for iYear in range(iYear_start, iYear_end + 1):
    #sYear = str(iYear).zfill(4)
    sYear = "{:04d}".format(iYear) 
    for iMonth in range(iMonth_start, iMonth_end + 1):
        sMonth = str(iMonth).zfill(2)

        sDummy = '.clm2.h0.' + sYear + '-' + sMonth + sExtension_nc
        sFilename = sWorkspace_simulation_case + slash + sCase + sDummy

        #read before modification

        if os.path.exists(sFilename):
            print("Yep, I can read that file!")
        else:
            print(
                "Nope, the path doesn't reach your file. Go research filepath in python"
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
                    values = aData_subset
                    grid_z3 = griddata(
                        points, values, (grid_x, grid_y), method='nearest')
                    #save outside
                    grid_z3[aMask] = missing_value
                    sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower() +slash + 'dat'
                    if not os.path.exists(sWorkspace_variable_dat):
                        os.makedirs(sWorkspace_variable_dat)
                    sFilename_envi = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sExtension_envi
                    a = np.flip(grid_z3, 0)
                    a.astype('float32').tofile(sFilename_envi)
                    
                    #write header
                    sFilename_header = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sExtension_header
                    headerParameters['sFilename'] = sFilename_header
                    envi_write_header(sFilename_header, headerParameters)
                    

                else:
                    continue

        #produce grid

    print("finished")
