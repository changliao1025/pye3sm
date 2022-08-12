import os
import sys
import numpy as np

from netCDF4 import Dataset #it maybe be replaced by gdal 
from osgeo import gdal #the default operator
from osgeo import gdal, osr

from pyearth.system.define_global_variables import *

from pye3sm.shared.e3sm import pye3sm
from pye3sm.shared.case import pycase
from pyearth.gis.gdal.write.gdal_write_envi_file import gdal_write_envi_file
from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_e3sm_configuration_file
from pye3sm.shared.pye3sm_read_configuration_file import pye3sm_read_case_configuration_file

def convert_observation_wtd_data_to_raster(oE3SM_in, oCase_in):
    
    sModel  = oCase_in.sModel    
    sRegion = oCase_in.sRegion
    sWorkspace_data=  '/qfs/people/liao313/data'
    dConversion = 1.0
    sVariable = 'wtd'

    sFilename_wtd = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
        + 'wtd' + slash + 'Global_wtd_lowres.nc'

    
    
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

    nrow=580
    ncolumn=1436

    dLat_min=np.min(aLatitude)
    dLat_max=np.max(aLatitude)
    dLon_min=np.min(aLongitude)
    dLon_max=np.max(aLongitude)

    dResolution=(dLat_max-dLat_min)/(nrow-1)
    dResolution1=(dLon_max-dLon_min)/(ncolumn-1)

    ULlon = dLon_min - dResolution/2.0
    ULlat = dLat_max + dResolution/2.0
    aWTD=np.reshape(aWTD,(nrow,ncolumn))
    aGrid_data = np.flip(aWTD, 0)
    aGrid_data[np.where(aGrid_data<0)]=-9999

    #optional
    iFlag_optional = 1
    if(iFlag_optional ==1):
        #save as envi
        pHeaderParameters = {}
        pHeaderParameters['ncolumn'] = '1436'
        pHeaderParameters['nrow'] = '580'
        pHeaderParameters['ULlon'] = ULlon
        pHeaderParameters['ULlat'] = ULlat
        pHeaderParameters['pixelSize'] = '0.25'
        pHeaderParameters['nband'] = '1'
        pHeaderParameters['offset'] = '0'
        pHeaderParameters['data_type'] = '4'
        pHeaderParameters['bsq'] = 'bsq'
        pHeaderParameters['byte_order'] = '0'
        pHeaderParameters['missing_value'] = '-9999'
        sFilename_envi = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
            + 'wtd' + slash  + sVariable.lower() + '_025'  + sExtension_envi
        pSpatial = osr.SpatialReference()
        pSpatial.ImportFromEPSG(4326)
        gdal_write_envi_file(sFilename_envi, aGrid_data, dResolution,float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial   )

        sFilename_tiff = sWorkspace_data + slash + sModel + slash + sRegion + slash + 'raster' + slash \
            + 'wtd' + slash  + sVariable.lower() + '_025'  + sExtension_tiff
        gdal_write_geotiff_file(sFilename_tiff, aGrid_data,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)


        

if __name__ == '__main__':
    
    
    sModel = 'h2sc'
    sRegion ='global'
    sFilename_e3sm_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/e3sm.xml'
    sFilename_case_configuration = '/qfs/people/liao313/workspace/python/pye3sm/pye3sm/case.xml'
    aParameter_e3sm = pye3sm_read_e3sm_configuration_file(sFilename_e3sm_configuration )


    aParameter_case = pye3sm_read_case_configuration_file(sFilename_case_configuration)
    oE3SM = pye3sm(aParameter_e3sm)
    oCase = pycase(aParameter_case)
    convert_observation_wtd_data_to_raster(oE3SM, oCase)

    
    print('finished')