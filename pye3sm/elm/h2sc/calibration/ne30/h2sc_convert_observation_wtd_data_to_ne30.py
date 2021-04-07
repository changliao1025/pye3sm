import os
import sys
import numpy as np
import xarray as xr
from nco import nco 

from osgeo import ogr, osr
from netCDF4 import Dataset #it maybe be replaced by gdal 
import netCDF4 as nc
from osgeo import gdal #the default operator
from scipy.interpolate import griddata #generate grid
from scipy.sparse import csr_matrix

#import library
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
#import global variable
from pyearth.system import define_global_variables
from pyearth.system.define_global_variables import *
from pyearth.toolbox.reader.read_configuration_file import read_configuration_file

from pyearth.gis.envi.envi_write_header import envi_write_header
from pyearth.gis.gdal.gdal_save_envi_file import gdal_save_envi_file

dConversion =1.0
sVariable = 'wtd'

def h2sc_convert_observation_wtd_data_to_ne30():

    #sWorkspace_data = '/qfs/people/liao313/data'
    sModel = 'h2sc'

    sFilename_wtd = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash + 'Global_wtd_lowres.nc'

    sFilename_map = '/compyfs/inputdata/lnd/clm2/mappingdata/maps/ne30np4' + slash +    'map_0.5x0.5_nomask_to_ne30np4_nomask_aave_da_c121019.nc'
    sFilename_mask = sWorkspace_data + slash \
            + 'h2sc' + slash + 'raster' + slash + 'dem' + slash \
            + 'MOSART_Global_half_20180606c.chang_9999.nc'
    sFilename_location = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_ne30np4_simyr2000_c190730.nc'
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
    nrow_new = 360
    ncolumn_new = 720
    aEle0 = aEle0.reshape(nrow_new, ncolumn_new)
    #remember that mask latitude start from -90, so need to flip it    
    aEle0 = np.flip(aEle0, 0) 
    aMask = np.where(aEle0 == missing_value)

    #read coordinates
    aDatasets = Dataset(sFilename_location)
    for sKey, aValue in aDatasets.variables.items():
        if "LONGXY" == sKey:
            LONGXY = (aValue[:]).data
            continue
        if "LATIXY" == sKey:
            LATIXY = (aValue[:]).data 
            continue

    #read wtd data        
    if os.path.isfile(sFilename_wtd):
        pass
    else:
        error_code = 0
        exit()
    aDatasets = Dataset(sFilename_wtd)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())

    for sKey, aValue in aDatasets.variables.items():
        if "lat" == sKey:
            aLatitude = (aValue[:]).data
            print(aValue.datatype)
            print(aValue.dimensions)
        if "lon" == sKey:
            aLongitude = (aValue[:]).data
            print(aValue.datatype)
            print(aValue.dimensions)
        if "WTD" == sKey:
            aWTD = (aValue[:]).data
            print(aValue.datatype)
            print(aValue.dimensions)

    print('prepare grid')

    longitude = np.arange(-179.75, 180., 0.5)
    latitude = np.arange(89.75, -90, -0.5)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
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

    nrow = len(aLatitude)
    ncolumn = len(aLongitude)
    ngrid  = 48602
    
    ncell = nrow_new * ncolumn_new

    dummy = np.array(aLongitude)
    aLongitude = np.transpose( np.tile(dummy.reshape(ncolumn, 1), (1, nrow)) )

    dummy = np.array(aLatitude)
    aLatitude =  np.tile(dummy.reshape(nrow, 1), (1, ncolumn))

    aWTD = aWTD.reshape(nrow, ncolumn)
    missing_value1 = np.min(aWTD)
    dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 ) \
                          &(aWTD != missing_value1 ) )
    aLongitude_subset = aLongitude[dummy_index]
    aLatitude_subset = aLatitude[dummy_index]
    aData_subset = aWTD[dummy_index] 
    points = np.vstack((aLongitude_subset, aLatitude_subset))
    points = np.transpose(points)
    values = aData_subset * dConversion
    grid_z3 = griddata(  points, values, (grid_x, grid_y), method='nearest')
    grid_z3[aMask] = missing_value

    #save output
    sFilename_envi = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()  + sExtension_envi

    #because grid_x, grid_y is from negative to positive
    aWTD_new = grid_z3 
    aWTD_new.astype('float32').tofile(sFilename_envi)
    #write header
    sFilename_header = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()  + sExtension_header
    headerParameters['sFilename'] = sFilename_header
    envi_write_header(sFilename_header, headerParameters)
    #test new method to save

    #sFilename_out = = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
    #    + 'wtd' + slash  + sVariable.lower() + '_new' + sExtension_envi
    #dPixelWidth = 0.5
    #dOriginX = -180
    #dOriginY = 90
    #pProjection = 
    #gdal_save_envi_file(sFilename_out, aWTD_new, dPixelWidth,\
    # dOriginX, dOriginY, pProjection )


    #Open output format driver, see gdal_translate --formats for list
    src_ds = gdal.Open( sFilename_envi )
    sFormat = "GTiff"
    driver = gdal.GetDriverByName( sFormat )
    #Output to new format
    sFilename_tiff = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()  + sExtension_tiff
    dst_ds = driver.CreateCopy( sFilename_tiff, src_ds, 0 )
    #Properly close the datasets to flush to disk
    dst_ds = None
    src_ds = None

    #now save as netcdf ne30 format
    aDatasets = Dataset(sFilename_map)
    netcdf_format = aDatasets.file_format
    print(netcdf_format)
    print("Print dimensions:")
    print(aDatasets.dimensions.keys())
    print("Print variables:")
    print(aDatasets.variables.keys())
    for sKey, aValue in aDatasets.variables.items():
        if "dst_grid_dims" == sKey:
            dst_grid_dims1 = (aValue[:]).data
            continue
        if "frac_a" == sKey:
            frac_a1 = (aValue[:]).data
            continue
        if "frac_b" == sKey:
            frac_b1 = (aValue[:]).data
            continue
        if "col" == sKey:
            iColumn_index1 = (aValue[:]).data
            continue
        if "row" == sKey:
            iRow_index1 = (aValue[:]).data
            continue
        if "area_a" == sKey:
            area_a1 = (aValue[:]).data
            continue
        if "area_b" == sKey:
            area_b1 = (aValue[:]).data
            continue
        if "S" == sKey:
            c1 = (aValue[:]).data
            continue
    iRow_index1= iRow_index1.astype(int) - 1
    iColumn_index1= iColumn_index1.astype(int) - 1    
    S1 = csr_matrix((c1, (iRow_index1, iColumn_index1)), shape=( ngrid, ncell))
    S1 = np.transpose(S1)      

    sFilename_output = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()  + sExtension_netcdf
    sFilename_output2 = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()+'_ne30'  + sExtension_netcdf

    pFile = nc.Dataset(sFilename_output, 'w', format='NETCDF4') 

    pDimension_longitude = pFile.createDimension('lon', 720) 
    pDimension_latitude = pFile.createDimension('lat', 360) 
    pVar = pFile.createVariable('wtd', 'f4', ('lat' , 'lon')) 
    pVar[:] = aWTD_new
    pVar.description = 'Water table depth' 
    pVar.unit = 'm' 
    pFile.close()

    #mapping file use -90 to 90 for latitude
    data = np.flip(aWTD_new, 0)
    data1 = data.reshape(1, ncell)
    data21 = data.swapaxes(0,1)
    data2 = data21.reshape(1, ncell)
   
    dummy1 = data1
    #we need to mask out missing value
    aMask = np.where(dummy1 == missing_value)
    dummy1[aMask] = np.nan

    total_in = np.sum(dummy1 * area_a1)
    dummy2 = dummy1 * S1
    aMask =  np.where(np.isnan(dummy2))
    dummy2[aMask] = missing_value
    aData_out = dummy2

    total_out = np.sum(dummy2 * area_b1 )   
    print(total_in, total_out)
   
    #save output
    pFile2 = nc.Dataset(sFilename_output2, 'w', format='NETCDF4') 

    pDimension_longitude = pFile2.createDimension('lon', ngrid) 
    pDimension_latitude = pFile2.createDimension('lat', ngrid) 
    pDimension_grid = pFile2.createDimension('ngrid', ngrid) 
    
    aLongitude = LONGXY.reshape(1, ngrid)
    aLatitude = LATIXY.reshape(1, ngrid)
    pVar1 = pFile2.createVariable('column', 'f4', ('ngrid',)) 
    pVar1[:] = aLongitude
    pVar1.description = 'longitude' 
    pVar1.unit = 'degree' 
    pVar2 = pFile2.createVariable('row', 'f4', ('ngrid',)) 
    pVar2[:] = aLatitude
    pVar2.description = 'latitude' 
    pVar2.unit = 'degree' 
    pVar3 = pFile2.createVariable('wtd', 'f4', ('ngrid',)) 
    pVar3[:] = aData_out
    pVar3.description = 'Water table depth' 
    pVar3.unit = 'm' 
    pFile2.close()

    #export to shapefile
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(4326) 
    sFilename_shapefile = sWorkspace_data + slash + sModel + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower()+'_ne30'   + sExtension_shapefile
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
        x = float( LONGXY[i] )
        if (x > 180):
            x =  x - 360
        else:
            pass
        y = float( LATIXY[i] )        
        value= float(aData_out[0][i])
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
    h2sc_convert_observation_wtd_data_to_ne30()
    print('finished')

