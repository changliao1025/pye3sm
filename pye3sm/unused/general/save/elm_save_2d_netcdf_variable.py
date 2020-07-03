import os
import numpy as np

import platform
import statistics
from mpl_toolkits.axes_grid1 import make_axes_locatable
from netCDF4 import Dataset
from scipy.interpolate import griddata

platform_os = platform.system()
if platform_os == 'Windows':
    slash = '\\'
else:
    slash = '/'

missing_value = -9999.0
sExtension_nc = '.nc'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = '/Volumes/mac/01data/'
sWorkspace_simulation = '/Volumes/mac/csmruns/'
sWorkspace_analysis = '/Volumes/mac/03model/h2sc/analysis/'

sFilename_mask = sWorkspace_data + slash \
    + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
    + 'MOSART_Global_half_20180606c.chang_9999.nc'
#we only need to change the case number, all variables will be processed one by one
iCase = 142
#be careful with the name
iYear_start = 1960
iYear_end = 1960
nlayer = 15
aVariable = ['H2OSOI']
aDimension = [2]

mms2mmd = 24 * 3600.0
aConversion = [1.0]

sCase = 'h2sc' + "{:02d}".format(iCase)

sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'

sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase

if not os.path.exists(sWorkspace_analysis_case):
    os.makedirs(sWorkspace_analysis_case)



iMonth_start = 1
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

print('prepare grid')

# the target domain
#matlab version
#xi = -179.75:0.5:179.75;
#yi = 89.75:-0.5:-89.75;
#[Xi, Yi] = meshgrid(xi,yi);
#temp = griddata(pft_lon,pft_lat,vv,Xi,Yi); # interp vv from ne30 to 0.5 degree domain;
#python version
#np.arange(3,7,2)
longitude = np.arange(-180, 180, 0.5)
latitude = np.arange(-90, 90, 0.5)
grid_x, grid_y = np.meshgrid(longitude, latitude)

for iYear in range(iYear_start, iYear_end + 1):
    sYear = str(iYear).zfill(4)

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
        #print(netcdf_format)
        #print("Print dimensions:")
        #print(aDatasets.dimensions.keys())
        #print("Print variables:")

        #print(aDatasets.variables.keys())

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
                    if (iDimension == 2):
                        #normal
                        dummy1 =  len(aData[0][0])
                        aData = aData.reshape(nlayer,  dummy1)
                        for iLayer in range (1, nlayer+1):
                            sLayer = str(iLayer).zfill(2)
                            aData_layer = aData[iLayer-1, :]
                            missing_value1 = max(aData_layer)
                            dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 ) \
                              &(aData_layer != missing_value1 ) )

                            aLongitude_subset = aLongitude[dummy_index]
                            aLatitude_subset = aLatitude[dummy_index]
                            aData_subset = aData_layer[dummy_index]

                            points = np.vstack((aLongitude_subset, aLatitude_subset))
                            points = np.transpose(points)
                            values = aData_subset
                            grid_z3 = griddata(
                                points, values, (grid_x, grid_y), method='nearest')

                            #save outside
                            grid_z3[aMask] = missing_value

                            sWorkspace_variable_dat = sWorkspace_analysis_case + slash + sVariable.lower(
                            ) +slash+'dat'
                            if not os.path.exists(sWorkspace_variable_dat):
                                os.makedirs(sWorkspace_variable_dat)

                            sFilename = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sLayer + '.dat'
                            a = np.flip(grid_z3, 0)
                            a.astype('float32').tofile(sFilename)

                            #write header
                            headerParameters = {}
                            headerParameters['fileName'] = sVariable
                            headerParameters['samples'] = '720'
                            headerParameters['lines'] = '360'
                            headerParameters['ULlon'] = '-180'
                            headerParameters['ULlat'] = '90'
                            headerParameters['pixelSize'] = '0.5'

                            headerText = '''ENVI
description = {{{fileName}}}
samples = {samples}
lines = {lines}
bands = 1
header offset = 0
data type = 4
interleave = bsq
sensor type = Unknown
byte order = 0
data ignore value = -9999
map info = {{Geographic Lat/Lon, 1.000, 1.000, {ULlon}, {ULlat}, {pixelSize}, {pixelSize}, WGS-84, units=Degrees}}
wavelength units = Unknown'''.format(**headerParameters)

                            sFilename = sWorkspace_variable_dat + slash + sVariable.lower() + sYear + sMonth + sLayer + '.hdr'
                            headerFile = open(sFilename, 'w')
                            headerFile.write(headerText)
                            headerFile.close()
                    else:
                        #this is different
                        pass

                else:
                    continue

        #produce grid

    print("finished")