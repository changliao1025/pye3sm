#most likely needed packages
import os #operate folder
import sys
import numpy as np
from netCDF4 import Dataset #read netcdf
sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *
from eslib.gis.gdal.read.gdal_read_geotiff import gdal_read_geotiff

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file


def h2sc_convert_parameter_to_model_grid_halfdegree(sFilename_configuration_in):
    
    #get configuration
    e3sm_read_configuration_file(sFilename_configuration_in)
    
    sDate='20200212'

    
    sRecord = sDate
    
    
    

    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass
    sWorkspace_analysis = e3sm_global.sWorkspace_analysis
   

    sWorkspace_analysis_wtd  = sWorkspace_analysis + slash + 'wtd'
    if not os.path.exists(sWorkspace_analysis_wtd):
        os.makedirs(sWorkspace_analysis_wtd)   
    
    dConversion = 1.0
    
    

    sFilename_parameter = sWorkspace_analysis_wtd + slash + 'optimal' + sRecord + sExtension_tif
    dummy = gdal_read_geotiff(sFilename_parameter)
    aAnisotropy_optimal = dummy[0]
    #extract the effective data from the matrix
    dummy_index = np.where(aAnisotropy_optimal != missing_value)
    aData_subset = aAnisotropy_optimal[dummy_index] 
    
    aLongitude_subset = grid_x[dummy_index]
    aLatitude_subset = grid_y[dummy_index]


    #read model grid from existing dataset
    #here we will use the surface data as example
    sFilename = '/compyfs/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr2000_c190730.nc'
    if os.path.exists(sFilename):
        print("Yep, I can read that file: " + sFilename)
    else:
        print(sFilename)
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        quit()
    aDatasets = Dataset(sFilename)
    for sKey, aValue in aDatasets.variables.items():
    
        if (sKey == 'LONGXY'):
            #print(aValue.datatype)
            #print(aValue.dimensions)
            aLongitude = (aValue[:]).data
            continue
        if (sKey == 'LATIXY'):
            #print(aValue.datatype)
            #print(aValue.dimensions)
            aLatitude = (aValue[:]).data
            continue
        if (sKey == 'PFTDATA_MASK'):
            #print(aValue.datatype)
            #print(aValue.dimensions)
            aMask = (aValue[:]).data
            continue
        
    
    #quality control the longitude data
    dummy_index = np.where(aLongitude > 180 )
    aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0
    dummy_index = np.where(aMask == 1 )
    aLongitude = aLongitude[dummy_index]
    aLatitude = aLatitude[dummy_index]

    #regrid the data
    points = np.vstack((aLongitude_subset, aLatitude_subset))
    points = np.transpose(points)
    values = aData_subset * dConversion
    #resample
    xi = (aLongitude, aLatitude)
    grid_z3 = griddata(points, values, xi, method='nearest')
    print(grid_z3)

    sFilename_shapefile = sWorkspace_analysis + slash + sVariable  + sExtension_shapefile
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(sFilename_shapefile)
    layer = ds.CreateLayer(sVariable, spatialRef, ogr.wkbPoint)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn(sVariable, ogr.OFTReal))
    defn = layer.GetLayerDefn()
    feat = ogr.Feature(defn)
    npoint = len(grid_z3)
    for i in range(npoint):
        point = ogr.Geometry(ogr.wkbPoint)
        x = float( aLongitude[i] )
        y = float( aLatitude[i] )
        #print(x, y)
        value= float(grid_z3[i])
        point.AddPoint( x, y ) 
        feat.SetGeometry(point)
        feat.SetField(sVariable,value)
        layer.CreateFeature(feat)
    
    ds = layer = feat  = None  
    print('finished')                 
if __name__ == '__main__':
    sModel = 'h2sc'
    sRegion = 'global'
    sFilename_configuration = sWorkspace_configuration  + slash + sModel + slash + sRegion + slash   + slash + 'h2sc_configuration_zwt.txt' 
    print(sFilename_configuration)

    iFlag_debug = 1
    if iFlag_debug == 1:
         
   
        h2sc_convert_parameter_to_model_grid_halfdegree(sFilename_configuration)
    else:
        pass
                                           