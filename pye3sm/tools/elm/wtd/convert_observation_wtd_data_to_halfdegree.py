import os
import sys
import numpy as np

from netCDF4 import Dataset #it maybe be replaced by gdal 
from osgeo import gdal #the default operator
from scipy.interpolate import griddata #generate grid

from pyearth.system.define_global_variables import *
from pyearth.gis.envi.envi_write_header import envi_write_header

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
 

from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def convert_observation_wtd_data_to_halfdegree(oE3SM_in, oCase_in):
    
    sModel  = oCase_in.sModel    
    sRegion = oCase_in.sRegion
    sWorkspace_data=  '/qfs/people/liao313/data'
    dConversion = 1.0
    sVariable = 'wtd'
    sFilename_mosart_input = '/qfs/people/liao313/data/h2sc/global/raster/dem/MOSART_Global_half_20180606c.chang_9999.nc'

    sFilename_wtd = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
        + 'wtd' + slash + 'Global_wtd_lowres.nc'

    if os.path.isfile(sFilename_mosart_input):
        pass
    else:
        error_code = 0
        exit()
    aDatasets = Dataset(sFilename_mosart_input)
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
    #read obs
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

#new grid
    longitude = np.arange(-179.75, 180., 0.5)
    latitude = np.arange(89.75, -90, -0.5)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
    

    nrow_obs = len(aLatitude)
    ncol_obs = len(aLongitude)

    dummy = np.array(aLongitude)
    aLongitude = np.transpose( np.tile(dummy.reshape(ncol_obs, 1), (1, nrow_obs)) )

    dummy = np.array(aLatitude)
    aLatitude =  np.tile(dummy.reshape(nrow_obs, 1), (1, ncol_obs))

    aWTD = aWTD.reshape(nrow_obs, ncol_obs)
    missing_value1 = np.min(aWTD)
    dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 ) \
                          &(aWTD != missing_value1 ) )
    aLongitude_subset = aLongitude[dummy_index]
    aLatitude_subset = aLatitude[dummy_index]
    aData_subset = aWTD[dummy_index] 
    points = np.vstack((aLongitude_subset, aLatitude_subset))
    points = np.transpose(points)
    values = aData_subset 
    aGrid_data = griddata(  points, values, (grid_x, grid_y), method='linear')
    aGrid_data[aMask] = missing_value

    #save output
    #save netcdf
    sFilename_output = sWorkspace_data + slash + sModel + slash +  sRegion + slash + 'raster' + slash \
        + 'wtd' + slash  + sVariable.lower() + '_halfdegree' + sExtension_netcdf
    pFile = Dataset(sFilename_output, 'w', format='NETCDF4') 

    pDimension_longitude = pFile.createDimension('lon', ncolumn_new) 
    pDimension_latitude = pFile.createDimension('lat', nrow_new) 
    pVar = pFile.createVariable('wtd', 'f4', ('lat' , 'lon')) 
    pVar[:] = aGrid_data
    pVar.description = 'Water table depth' 
    pVar.unit = 'm' 
    pFile.close()
    

    #optional
    iFlag_optional = 1
    if(iFlag_optional ==1):
        #save as envi
        pHeaderParameters = {}
        pHeaderParameters['ncolumn'] = '720'
        pHeaderParameters['nrow'] = '360'
        pHeaderParameters['ULlon'] = '-180'
        pHeaderParameters['ULlat'] = '90'
        pHeaderParameters['pixelSize'] = '0.5'
        pHeaderParameters['nband'] = '1'
        pHeaderParameters['offset'] = '0'
        pHeaderParameters['data_type'] = '4'
        pHeaderParameters['bsq'] = 'bsq'
        pHeaderParameters['byte_order'] = '0'
        pHeaderParameters['missing_value'] = '-9999'
        sFilename_envi = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
            + 'wtd' + slash  + sVariable.lower() + '_halfdegree'  + sExtension_envi

        aGrid_data.astype('float32').tofile(sFilename_envi)
        #write header
        sFilename_header = sWorkspace_data + slash + sModel + slash + sRegion+ slash + 'raster' + slash \
            + 'wtd' + slash  + sVariable.lower() + '_halfdegree'  + sExtension_header
        pHeaderParameters['sFilename'] = sFilename_header
        envi_write_header(sFilename_header, pHeaderParameters)


        #Open output format driver, see gdal_translate --formats for list
        src_ds = gdal.Open( sFilename_envi )
        sFormat = "GTiff"
        driver = gdal.GetDriverByName( sFormat )
        #Output to new format
        sFilename_tiff = sWorkspace_data + slash + sModel +  slash + sRegion + slash + 'raster' + slash \
            + 'wtd' + slash  + sVariable.lower() + '_halfdegree' + sExtension_tiff
        dst_ds = driver.CreateCopy( sFilename_tiff, src_ds, 0 )
        #Properly close the datasets to flush to disk
        dst_ds = None
        src_ds = None

if __name__ == '__main__':
    
    
    sModel = 'h2sc'
    sRegion ='global'
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration )


    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration)
    oE3SM = pye3sm(aParameter_e3sm)
    oCase = pycase(aParameter_case)
    convert_observation_wtd_data_to_halfdegree(oE3SM, oCase)

    
    print('finished')