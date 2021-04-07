import os, sys
import numpy as np
from netCDF4 import Dataset
from osgeo import gdal #the default operator
sSystem_paths = os.environ['PATH'].split(os.pathsep)
 
from pyearth.system.define_global_variables import *

sPath_pye3sm = sWorkspace_code +  slash + 'python' + slash + 'e3sm' + slash + 'e3sm_python'
 

from pyearth.gis.envi.envi_write_header import envi_write_header

from e3sm.shared import oE3SM
from e3sm.shared.e3sm_read_configuration_file import e3sm_read_configuration_file

def h2sc_map_soil_clay_content(sFilename_configuration_in, iCase_index):
    #extract information
    e3sm_read_configuration_file(sFilename_configuration_in, iCase_index_in = iCase_index)       
    sModel  = oE3SM.sModel
    sRegion = oE3SM.sRegion   
    if( sModel == 'h2sc'):
        pass
    else:
        if(sModel == 'vsfm'):
            aDimension = [ 96, 144]
        else:
            pass 
    dConversion = oE3SM.dConversion   
    sVariable  = oE3SM.sVariable
    #for the sake of simplicity, all directory will be the same, no matter on mac or cluster
    #sWorkspace_data = home + slash + 'data'
    sWorkspace_simulation = sWorkspace_scratch + slash + 'e3sm_scratch'
    sWorkspace_analysis = sWorkspace_scratch + slash + '04model' + slash \
        + sModel + slash + sRegion + slash + 'analysis'
    if not os.path.isdir(sWorkspace_analysis):
        os.makedirs(sWorkspace_analysis)
    sCase = oE3SM.sCase
    sWorkspace_simulation_case = sWorkspace_simulation + slash + sCase + slash + 'run'
    sWorkspace_analysis_case = sWorkspace_analysis + slash + sCase
    
    if not os.path.exists(sWorkspace_analysis_case):
        os.makedirs(sWorkspace_analysis_case)
    
    #read in global 0.5 * 0.5 mask
    sFilename_mask = oE3SM.sFilename_mask

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
    nlayer_new = 10
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
    #read surface data
    sFilename = '/compyfs/inputdata/lnd/clm2/surfdata_map' + slash + 'surfdata_0.5x0.5_simyr2010_c191025.nc'
    
    aDatasets = Dataset(sFilename)

  
     
    

    #read the actual data
    for sKey, aValue in aDatasets.variables.items():
        if sVariable == sKey:
            #for attrname in aValue.ncattrs():
            #print("{} -- {}".format(attrname, getattr(aValue, attrname)))                    
            aData = (aValue[:]).data                     
                               
            #missing_value1 = np.max(aData)           
           
            aData = aData.reshape(nlayer_new, nrow_new, ncolumn_new)      
            aData = np.mean(aData, axis= 0)
            aData = np.flip(aData, 0)    
            #dummy_index = np.where( aData == missing_value1 ) 
            #aData[dummy_index] = missing_value
            print(np.nanmax(aData))
            aGrid_data = aData
               
            
            #save output
            aGrid_data[aMask] = missing_value
            
           

            sWorkspace_variable_dat = sWorkspace_analysis_case + slash \
                + sVariable.lower() + slash + 'dat'
            if not os.path.exists(sWorkspace_variable_dat):
                os.makedirs(sWorkspace_variable_dat)
            sWorkspace_variable_tiff = sWorkspace_analysis_case + slash + sVariable.lower() + slash + 'tiff'
            if not os.path.exists(sWorkspace_variable_tiff):
                os.makedirs(sWorkspace_variable_tiff)
            sFilename_envi = sWorkspace_variable_dat + slash + sVariable.lower() +sExtension_envi
            aGrid_data.astype('float32').tofile(sFilename_envi)
            #write header
            sFilename_header = sWorkspace_variable_dat + slash + sVariable.lower()  + sExtension_header
            pHeaderParameters['sFilename'] = sFilename_header
            envi_write_header(sFilename_header, pHeaderParameters)
            #Open output format driver, see gdal_translate --formats for list
            src_ds = gdal.Open( sFilename_envi )
            sFormat = "GTiff"
            driver = gdal.GetDriverByName( sFormat )
            #Output to new format
            sFilename_tiff = sWorkspace_variable_tiff + slash + sVariable.lower()  + sExtension_tiff
            dst_ds = driver.CreateCopy( sFilename_tiff, src_ds, 0 )
            #Properly close the datasets to flush to disk
            dst_ds = None
            src_ds = None
           
            break
    print('finished')
    return
if __name__ == '__main__':

    sModel = 'h2sc'
    sRegion = 'global'
    sVariable = 'PCT_CLAY'
    iCase_index = 553
    sFilename_configuration = sWorkspace_configuration + slash + sModel + slash \
               + sRegion + slash + 'h2sc_configuration_' + sVariable.lower() + sExtension_txt
    print(sFilename_configuration)
    h2sc_map_soil_clay_content(sFilename_configuration, iCase_index)