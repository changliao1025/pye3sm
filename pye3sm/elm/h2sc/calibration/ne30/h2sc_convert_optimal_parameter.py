#most likely needed packages
import os #operate folder
import sys
import numpy as np
from netCDF4 import Dataset #it maybe be replaced by gdal 
from osgeo import ogr, osr
#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *
def h2sc_convert_optimal_parameter():
    ngrid   = 48602
    sModel = 'h2sc'
    sVariable = 'anisotropy'
    #read mapping netcdf
    sFilename_map = '/compyfs/inputdata/lnd/clm2/mappingdata/maps/ne30np4' + slash +    'map_0.5x0.5_nomask_to_ne30np4_nomask_aave_da_c121019.nc'
    aDatasets = Dataset(sFilename_map)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "xc_b" == sKey:
            aLongitude = (aValue[:]).data
            continue
        if "yc_b" == sKey:
            aLatitude = (aValue[:]).data
            continue
    #read parameter file
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)  
    sRecord = '240_261'
    sFilename_in = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_netcdf
    print(sFilename_in)    
    aDatasets = Dataset(sFilename_in)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "optimal" == sKey:
            aAnisotropy_optimal = (aValue[:]).data
            continue
        

    #export to shapefile
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(4326) 
    sFilename_shapefile = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()+'_ne30'   + sExtension_shapefile
    print(sFilename_shapefile)
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(sFilename_shapefile)
    layer = ds.CreateLayer(sVariable, spatialRef, ogr.wkbPoint)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn(sVariable, ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
    defn = layer.GetLayerDefn()
    feat = ogr.Feature(defn)
    npoint = ngrid
    for i in range(ngrid):
        point = ogr.Geometry(ogr.wkbPoint)
        x = float( aLongitude[i] )
        if (x > 180):
            x =  x - 360
        else:
            pass
        y = float( aLatitude[i] )        
        value= float(aAnisotropy_optimal[i])
        if(value != missing_value):            
            point.AddPoint( x, y ) 
            feat.SetGeometry(point)
            feat.SetField(sVariable,value)
            feat.SetField('lon',x)
            feat.SetField('lat',y)
            layer.CreateFeature(feat)
        else:    
            #print(value)       
            pass
    
    ds = layer = feat  = None  
    print('finished')          
if __name__ == '__main__':
    h2sc_convert_optimal_parameter()