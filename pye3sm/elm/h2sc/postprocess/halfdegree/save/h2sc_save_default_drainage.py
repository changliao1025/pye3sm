
import os
import sys
import numpy as np
import platform
from pathlib import Path #get the home directory
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from mpl_toolkits.axes_grid1 import AxesGrid
import shapefile
from osgeo import ogr, osr
from netCDF4 import Dataset #it maybe be replaced by gdal 




sPath_library_python = sWorkspace_code +  slash + 'python' + slash + 'library' + slash + 'pyes_python'
print(sPath_library_python)
sys.path.append(sPath_library_python)
from envi.envi_write_header import envi_write_header
missing_value = -9999.0
sExtension_nc = '.nc'
sExtension_envi ='.dat'
sExtension_header ='.hdr'
sExtension_tif = '.tif'
sExtension_jpg ='.jpg'
sExtension_shapefile = '.shp'
sModel = 'h2sc'
#for the sake of simplicity, all directory will be the same, no matter on mac or cluster
sWorkspace_data = home + slash + 'data'
sWorkspace_simulation = sWorkspace_scratch + slash + 'csmruns'
sWorkspace_analysis = sWorkspace_scratch + slash + '03model' + slash \
    + sModel + slash + 'analysis'
if not os.path.isdir(sWorkspace_analysis):
    os.makedirs(sWorkspace_analysis)

sFilename_mask = sWorkspace_data + slash \
    + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
    + 'MOSART_Global_half_20180606c.chang_9999.nc'
#we only need to change the case number, all variables will be processed one by one
iCase = 178
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


spatialRef = osr.SpatialReference()
spatialRef.ImportFromEPSG(4326)  


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
                        
                    

                        sWorkspace_variable_shapefile  = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'shape'
                        if not os.path.exists(sWorkspace_variable_shapefile):
                            os.makedirs(sWorkspace_variable_shapefile)
                        

                        sFilename_shapefile = sWorkspace_variable_shapefile + slash + sVariable.lower() + sYear + sMonth + sExtension_shapefile
                        driver = ogr.GetDriverByName('Esri Shapefile')
                        ds = driver.CreateDataSource(sFilename_shapefile)
                        layer = ds.CreateLayer(sVariable, spatialRef, ogr.wkbPoint)
                        # Add one attribute
                        layer.CreateField(ogr.FieldDefn(sVariable, ogr.OFTReal))
                        defn = layer.GetLayerDefn()
                        feat = ogr.Feature(defn)

                        npoint = len(values)

                        for i in range(npoint):
                            point = ogr.Geometry(ogr.wkbPoint)
                            x = float( aLongitude_subset[i] )
                            y = float( aLatitude_subset[i] )
                            value= float(values[i])
                            point.AddPoint( x, y ) 
                            feat.SetGeometry(point)
                            feat.SetField(sVariable,value)
                            layer.CreateFeature(feat)

                        
                        ds = layer = feat  = None  


                    else:                        
                        pass
                else:
                    continue
        #produce grid

    print("finished")
