import os , sys

import numpy as np
from scipy.interpolate import griddata #generate grid
from netCDF4 import Dataset #read netcdf
from osgeo import gdal, osr #the default operator


sSystem_paths = os.environ['PATH'].split(os.pathsep)
sys.path.extend(sSystem_paths)

from eslib.system.define_global_variables import *     
#from eslib.gis.envi.envi_write_header import envi_write_header
from eslib.gis.gdal.write.gdal_write_envi_file_multiple_band import gdal_write_envi_file_multiple_band

from eslib.gis.gdal.write.gdal_write_geotiff_multiple_band import gdal_write_geotiff_multiple_band

sPath_e3sm_python = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
sys.path.append(sPath_e3sm_python)

from e3sm.shared import e3sm_global
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def elm_save_variable_halfdegree(sFilename_configuration_in, iCase_index, \
    iFlag_same_grid_in = None, \
    iYear_start_in = None, \
    iYear_end_in = None, \
    sDate_in = None ):
    
    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in, iCase_index_in = iCase_index,\
         iYear_start_in = iYear_start_in, \
    iYear_end_in = iYear_end_in, \
         sDate_in= sDate_in)       
    sModel  = e3sm_global.sModel
    sRegion = e3sm_global.sRegion      
    if iYear_start_in is not None:        
        iYear_start = iYear_start_in
    else:       
        iYear_start = e3sm_global.iYear_start
    if iYear_end_in is not None:        
        iYear_end = iYear_end_in
    else:       
        iYear_end = e3sm_global.iYear_end
    
    if iFlag_same_grid_in is not None:        
        iFlag_same_grid = iFlag_same_grid_in
    else:       
        iFlag_same_grid = 0
 
    print('The following model is processed: ', sModel)
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass    
    dConversion = e3sm_global.dConversion   
    sVariable  = e3sm_global.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
   
    sCase = e3sm_global.sCase
    #we only need to change the case number, all variables will be processed one by one
    
    
    sWorkspace_simulation_case_run = e3sm_global.sWorkspace_simulation_case_run
    sWorkspace_analysis_case = e3sm_global.sWorkspace_analysis_case
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)
    
    #read in global 0.5 * 0.5 mask
    sFilename_mask = e3sm_global.sFilename_mask

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
        + sVariable.lower() + slash + 'netcdf'
    if not os.path.exists(sWorkspace_variable_netcdf):
        os.makedirs(sWorkspace_variable_netcdf)
    sWorkspace_variable_dat = sWorkspace_analysis_case + slash \
                            + sVariable.lower() + slash + 'dat'
    if not os.path.exists(sWorkspace_variable_dat):
        os.makedirs(sWorkspace_variable_dat)
    sWorkspace_variable_tif = sWorkspace_analysis_case + slash \
        + sVariable.lower() + slash + 'tif'
    if not os.path.exists(sWorkspace_variable_tif):
        os.makedirs(sWorkspace_variable_tif)
        
    sFilename_output = sWorkspace_variable_netcdf + slash + sVariable.lower() +  sExtension_netcdf
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
                if sVariable == sKey:
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

                    sDummy = sVariable.lower() + sYear + sMonth
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
    
    pSpatial =osr.SpatialReference()
    pSpatial.ImportFromEPSG(4326)
    sFilename_envi = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_envi

    gdal_write_envi_file_multiple_band(sFilename_envi, aGrid_stack,\
        float(pHeaderParameters['pixelSize']),\
         float(pHeaderParameters['ULlon']),\
              float(pHeaderParameters['ULlat']),\
                  -9999.0, pSpatial)

    sFilename_tif = sWorkspace_variable_tif + slash + sVariable.lower()  + sExtension_tif

    gdal_write_geotiff_multiple_band(sFilename_tif, aGrid_stack,\
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

    sFilename_configuration = sWorkspace_scratch + slash + '03model' + slash \
              + 'elm_configuration' + sFilename_config
   
    eco3d_evaluate_soil_doc_concentration_scatterplot(sFilename_configuration, iCase)
