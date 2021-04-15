import os , sys

import numpy as np
from scipy.interpolate import griddata #generate grid
from netCDF4 import Dataset #read netcdf
from osgeo import gdal, osr #the default operator



from pyearth.system.define_global_variables import *     

from pyearth.gis.gdal.write.gdal_write_envi_file import gdal_write_envi_file_multiple_band

from pyearth.gis.gdal.write.gdal_write_geotiff_file import gdal_write_geotiff_file_multiple_band

 
 

from ..shared.e3sm import pye3sm
from ..shared.case import pycase

def elm_save_variable_halfdegree(oE3SM_in, oCase_in):

    sModel  = oCase_in.sModel
    sRegion = oCase_in.sRegion               
    iYear_start = oCase_in.iYear_start        
    iYear_end = oCase_in.iYear_end          
    iFlag_same_grid = oCase_in.iFlag_same_grid 
    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass    
        
    dConversion = oCase_in.dConversion   
    sVariable  = oCase_in.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = oCase_in.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = oCase_in.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = oCase_in.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)
    
    #read in global 0.5 * 0.5 mask
    sFilename_mask = oCase_in.sFilename_mask

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


    print('Prepare the map grid')
   
    longitude = np.arange(-179.75, 180., 0.5)
    latitude = np.arange(89.75, -90, -0.5)
    grid_x, grid_y = np.meshgrid(longitude, latitude)
    #prepare the header in
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
    
    iFlag_optional = 1 

    #save netcdf
    sWorkspace_variable_netcdf = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'netcdf'
    if not os.path.exists(sWorkspace_variable_netcdf):
        os.makedirs(sWorkspace_variable_netcdf)
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash \
                            + sVariable + slash + 'dat'
    if not os.path.exists(sWorkspace_variable_dat):
        os.makedirs(sWorkspace_variable_dat)
    sWorkspace_variable_tiff = sWorkspace_analysis_case + slash \
        + sVariable + slash + 'tiff'
    if not os.path.exists(sWorkspace_variable_tiff):
        os.makedirs(sWorkspace_variable_tiff)
        
    sFilename_output = sWorkspace_variable_netcdf + slash + sVariable +  sExtension_netcdf
    pFile = Dataset(sFilename_output, 'w', format='NETCDF4') 
    pDimension_longitude = pFile.createDimension('lon', ncolumn_new) 
    pDimension_latitude = pFile.createDimension('lat', nrow_new) 

    nmonth = (iYear_end - iYear_start +1) * 12
    aGrid_stack= np.full((nmonth, nrow_new, ncolumn_new), -9999.0, dtype= float)
    i=0
    for iYear in range(iYear_start, iYear_end + 1):
        sYear = "{:04d}".format(iYear) #str(iYear).zfill(4)
    
        for iMonth in range(iMonth_start, iMonth_end + 1):
            sMonth = str(iMonth).zfill(2)
    
            sDummy = '.clm2.h0.' + sYear + '-' + sMonth + sExtension_netcdf
            sFilename = sWorkspace_simulation_case_run + slash + sCase + sDummy
    
            #read before modification
    
            if os.path.exists(sFilename):
                print("Yep, I can read that file: " + sFilename)
            else:
                print(sFilename)
                print("Nope, the path doesn't reach your file. Go research filepath in python")
                quit()
    
            aDatasets = Dataset(sFilename)
    
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
            
            #quality control the longitude data
            dummy_index = np.where(aLongitude > 180)
            aLongitude[dummy_index] = aLongitude[dummy_index] - 360.0
    
            #read the actual data
            for sKey, aValue in aDatasets.variables.items():
                if sVariable == sKey.lower():
                    #for attrname in aValue.ncattrs():
                    #print("{} -- {}".format(attrname, getattr(aValue, attrname)))                    
                    aData = (aValue[:]).data                     
                    #print(aData)
                    missing_value1 = np.max(aData)           
                    if(iFlag_same_grid == 1 ): #no need to resample if there are the same grid
                        aData = aData.reshape(nrow_new, ncolumn_new)      
                        aData = np.flip(aData, 0)    
                        dummy_index = np.where( aData == missing_value1 ) 
                        aData[dummy_index] = missing_value
                        #print(np.nanmax(aData))
                        #print(aData)
                        aGrid_data = aData
                       
                    else:

                        dummy_index = np.where( (aLongitude < 180 ) & ( aLatitude < 90 )  &(aData != missing_value1 ) )
                        #use the missing value mask to choose the points
                        aLongitude_subset = aLongitude[dummy_index]
                        aLatitude_subset = aLatitude[dummy_index]
                        aData_subset = aData[dummy_index]
                        points = np.vstack((aLongitude_subset, aLatitude_subset))
                        points = np.transpose(points)
                        values = aData_subset * dConversion
                        if(np.isnan( values ).any()) :
                            print('nan')
                        #resample
                        aGrid_data = griddata(points, values,\
                                 (grid_x, grid_y), method='nearest')
                    #save output
                    aGrid_data[aMask] = missing_value

                    sDummy = sVariable + sYear + sMonth
                    pVar = pFile.createVariable( sDummy , 'f4', ('lat' , 'lon')) 
                    pVar[:] = aGrid_data
                    pVar.description = sDummy
                    pVar.unit = 'm' 
                    iFlag_netcdf_first = 0
                    
                    if(iFlag_optional == 1):
                        #stack data
                        aGrid_stack[i, :,: ] =  aGrid_data
                        i=i+1
                    break
                else:
                    pass
    
    
    #close netcdf file   
    pFile.close()
    #write envi and geotiff file
    
    pSpatial = osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_envi = sWorkspace_variable_dat + slash + sVariable  + sExtension_envi

    gdal_write_envi_file_multiple_band(sFilename_envi, aGrid_stack,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)

    sFilename_tiff = sWorkspace_variable_tiff + slash + sVariable + sExtension_tiff

    gdal_write_geotiff_file_multiple_band(sFilename_tiff, aGrid_stack,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)


    print("finished")

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("iCase", help = "the id of the e3sm case",
                        type=int)
    args = parser.parse_args()
    iCase = args.iCase

    
